"""Interactive helper for collecting responses by hand, without the file juggling.

    python scripts/run_assistant.py evaluation/runs/<run_id>

For each run-sheet row that has no response yet, in order:
  1. the exact message is copied to your clipboard;
  2. you open a NEW chat in Claude, paste (Ctrl+V), send, wait, and click the copy
     button under Claude's answer;
  3. you press Enter here: the response is read from the clipboard, saved to
     responses/<row_id>.md, and the run sheet row is filled in and saved.

The script never touches Claude's website. It only reads and writes your clipboard and the
files in the run folder. Progress is saved after every row, so you can stop (q or Ctrl+C) and
rerun the same command to continue where you left off.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402

SESSION_FIELDS = ("surface", "model_label", "thinking_setting", "operator")
ACTIVATION_CHOICES = {"y": "yes", "n": "no", "u": "unclear"}
DEFAULT_EVIDENCE = {
    "yes": "activity panel showed socialized/SKILL.md being read",
    "no": "no sign of the skill in the activity panel",
    "unclear": "activity panel ambiguous or not shown",
}
SKILL_TOGGLE = "Customize -> Skills"


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------

class ClipboardError(RuntimeError):
    pass


class SystemClipboard:
    """Clipboard access with no third-party dependency (pyperclip is used if installed)."""

    def __init__(self) -> None:
        try:
            import pyperclip  # type: ignore
            self._copy, self._paste = pyperclip.copy, pyperclip.paste
            return
        except ImportError:
            pass
        if sys.platform == "win32":
            self._copy, self._paste = self._win_copy, self._win_paste
        elif sys.platform == "darwin":
            self._copy = lambda text: self._run(["pbcopy"], text)
            self._paste = lambda: self._run(["pbpaste"])
        elif shutil.which("wl-copy") and shutil.which("wl-paste"):
            self._copy = lambda text: self._run(["wl-copy"], text)
            self._paste = lambda: self._run(["wl-paste", "--no-newline"])
        elif shutil.which("xclip"):
            self._copy = lambda text: self._run(["xclip", "-selection", "clipboard"], text)
            self._paste = lambda: self._run(["xclip", "-selection", "clipboard", "-o"])
        else:
            raise ClipboardError("No clipboard tool found. Install pyperclip (pip install pyperclip) "
                                 "or xclip / wl-clipboard.")

    @staticmethod
    def _run(cmd: list[str], text: str | None = None) -> str:
        result = subprocess.run(cmd, input=text.encode("utf-8") if text is not None else None,
                                capture_output=True, check=False)
        if result.returncode != 0:
            raise ClipboardError(f"{cmd[0]} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
        return result.stdout.decode("utf-8", "replace")

    @classmethod
    def _win_copy(cls, text: str) -> None:
        script = ("[Console]::InputEncoding=[Text.Encoding]::UTF8; "
                  "Set-Clipboard -Value ([Console]::In.ReadToEnd())")
        cls._run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], text)

    @classmethod
    def _win_paste(cls) -> str:
        script = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"
        out = cls._run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script])
        out = out.lstrip("\ufeff")
        return out[:-2] if out.endswith("\r\n") else out

    def copy(self, text: str) -> None:
        self._copy(text)

    def paste(self) -> str:
        return self._paste() or ""


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


# ---------------------------------------------------------------------------
# Run sheet helpers (pure, unit-tested)
# ---------------------------------------------------------------------------

def response_done(run_dir: Path, row: dict) -> bool:
    path = run_dir / row["response_file"]
    return path.is_file() and bool(path.read_text(encoding="utf-8").strip())


def pending_rows(run_dir: Path, rows: list[dict], batch: str | None = None) -> list[dict]:
    todo = [r for r in rows if not response_done(run_dir, r) and (batch is None or r["batch"] == batch)]
    return sorted(todo, key=lambda r: int(r["order"] or 0))


def check_response(response: str, message: str, previous: str | None) -> str | None:
    """Return a problem description, or None if the clipboard looks like a real response."""
    if not response:
        return "The clipboard is empty."
    if response == normalize(message):
        return "The clipboard still holds the message you sent, not Claude's answer."
    if previous is not None and response == previous:
        return "The clipboard holds the same text as the previous saved response."
    return None


def session_defaults(rows: list[dict]) -> dict[str, str]:
    """Most recent non-empty value of each session field, so a resumed session keeps its settings."""
    defaults: dict[str, str] = {}
    for row in sorted(rows, key=lambda r: int(r["order"] or 0)):
        for name in SESSION_FIELDS:
            if row.get(name):
                defaults[name] = row[name]
    return defaults


def fill_row(row: dict, session: dict[str, str], today: str, activation: str | None = None,
             evidence: str = "", references: str = "", note: str = "", skill_sha: str = "") -> None:
    row["date"] = today
    for name in SESSION_FIELDS:
        row[name] = session.get(name, "")
    if row["batch"] == "skill_off":
        row["activation_observed"] = "na"
    else:
        row["activation_observed"] = activation or ""
        row["activation_evidence"] = evidence
        row["references_loaded"] = references
        if not row.get("skill_zip_sha256") and skill_sha:
            row["skill_zip_sha256"] = skill_sha
    if note:
        row["notes"] = f"{row['notes']}; {note}" if row.get("notes") else note


def save_sheet(path: Path, header: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(".csv.tmp")
    es.write_csv(tmp, header, rows)
    os.replace(tmp, path)


def manifest_sha(batch: str) -> str:
    dist = es.REPO_ROOT / "dist"
    try:
        skill = es.dist_skill_name(dist)
    except (FileNotFoundError, ValueError):
        return ""
    if batch == "skill_on" or batch == "variant:full":
        manifest = dist / f"{skill}.manifest.json"
    elif batch.startswith("variant:"):
        manifest = dist / "ablation" / f"{skill}--{batch.split(':', 1)[1]}.manifest.json"
    else:
        return ""
    return json.loads(manifest.read_text(encoding="utf-8"))["zip_sha256"] if manifest.is_file() else ""


def batch_instruction(batch: str) -> str:
    skill = "socialized"
    try:
        skill = es.dist_skill_name(es.REPO_ROOT / "dist")
    except (FileNotFoundError, ValueError):
        pass
    if batch == "skill_off":
        return f"In Claude, open {SKILL_TOGGLE} and make sure '{skill}' is turned OFF."
    if batch == "skill_on":
        return f"In Claude, open {SKILL_TOGGLE} and make sure '{skill}' is turned ON (no other custom skills)."
    variant = batch.split(":", 1)[1]
    packaged = f"dist/{skill}.zip" if variant == "full" else f"dist/ablation/{skill}--{variant}.zip"
    return (f"In Claude, delete the installed '{skill}', upload {packaged} and turn it ON.")


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------

class Quit(Exception):
    pass


def ask(prompt: str, read: Callable[[str], str]) -> str:
    try:
        return read(prompt).strip()
    except EOFError as exc:
        raise Quit from exc


def ask_session(defaults: dict[str, str], read: Callable[[str], str], write: Callable[[str], None]) -> dict[str, str]:
    labels = {
        "surface": "Where are you using Claude (e.g. 'claude.ai web', 'claude desktop')",
        "model_label": "Model name exactly as shown in Claude's model picker",
        "thinking_setting": "Extended thinking: on or off",
        "operator": "Your name or initials",
    }
    write("\nSession settings. These are recorded on every row; keep them identical for the whole run.")
    session = {}
    for name in SESSION_FIELDS:
        default = defaults.get(name, "")
        while True:
            suffix = f" [{default}]" if default else ""
            value = ask(f"  {labels[name]}{suffix}: ", read) or default
            if value:
                session[name] = value
                break
            write("    A value is required.")
    if defaults.get("model_label") and session["model_label"] != defaults["model_label"]:
        write(f"  WARNING: earlier rows used model '{defaults['model_label']}'. Mixing models invalidates "
              "comparisons; redo the batch if the model really changed.")
    return session


def ask_activation(read: Callable[[str], str], write: Callable[[str], None]) -> tuple[str, str, str]:
    write("  Expand the activity/thinking panel above Claude's answer. Did it read socialized/SKILL.md?")
    while True:
        choice = ask("  Activation [y]es / [n]o / [u]nclear: ", read).lower()[:1]
        if choice in ACTIVATION_CHOICES:
            break
        write("    Type y, n or u.")
    activation = ACTIVATION_CHOICES[choice]
    evidence = ask(f"  What did you see? (Enter = '{DEFAULT_EVIDENCE[activation]}'): ", read) or DEFAULT_EVIDENCE[activation]
    references = ""
    if activation == "yes":
        references = ask("  Reference files also read, e.g. explanation-examples.md (Enter = none): ", read)
    return activation, evidence, references


HELP = ("  Commands: Enter = save the response from the clipboard | c = copy the message again | "
        "n <text> = add a note | s = skip this row for now | q = quit (progress is saved)")


def run(run_dir: Path, *, clipboard, read: Callable[[str], str] = input,
        write: Callable[[str], None] = print, batch: str | None = None,
        today: str | None = None) -> int:
    sheet = run_dir / "run_sheet.csv"
    if not sheet.is_file():
        write(f"Run sheet not found: {sheet}. Create it with scripts/make_run_sheet.py first.")
        return 1
    header, rows = es.read_csv(sheet)
    missing = [c for c in es.RESULTS_COLUMNS if c not in header]
    if missing:
        write(f"{sheet} is missing columns {missing}.")
        return 1
    today = today or dt.date.today().isoformat()
    todo = pending_rows(run_dir, rows, batch)
    total, done_before = len(rows), len(rows) - len(pending_rows(run_dir, rows))
    if not todo:
        write(f"Nothing to do: all {'selected ' if batch else ''}rows already have responses.")
        write(f"Next: python scripts/summarize_results.py {run_dir.as_posix()} --check-only")
        return 0

    write(f"Run '{run_dir.name}': {done_before}/{total} responses already saved, {len(todo)} to go.")
    write("Rules: use a NEW chat for every row, never regenerate to get a better answer, keep the same model.")
    try:
        session = ask_session(session_defaults(rows), read, write)
        previous: str | None = None
        current_batch = None
        saved = 0
        for row in todo:
            if row["batch"] != current_batch:
                current_batch = row["batch"]
                remaining = sum(1 for r in todo if r["batch"] == current_batch)
                write(f"\n=== Batch '{current_batch}' ({remaining} rows) ===")
                write(f"  {batch_instruction(current_batch)}")
                while ask("  Type 'ok' when done: ", read).lower() != "ok":
                    write("    Change the skill setting first, then type ok.")
            message = (run_dir / row["message_file"]).read_text(encoding="utf-8")
            position = done_before + saved + 1
            write(f"\n[{position}/{total}] {row['row_id']}  (condition {row['condition']})")
            clipboard.copy(message)
            write("  Message copied. In Claude: New chat -> Ctrl+V -> Enter. When the answer is finished,")
            write("  click the copy button under it, then come back here.")
            write(HELP)
            note = ""
            while True:
                command = ask("  > ", read)
                if command.lower() == "q":
                    raise Quit
                if command.lower() == "s":
                    write("  Skipped; it will be offered again next time.")
                    break
                if command.lower() == "c":
                    clipboard.copy(message)
                    write("  Message copied again.")
                    continue
                if command.lower().startswith("n "):
                    note = command[2:].strip()
                    write(f"  Note recorded: {note}")
                    continue
                if command:
                    write("  Unknown command.")
                    continue
                response = normalize(clipboard.paste())
                problem = check_response(response, message, previous)
                if problem:
                    write(f"  {problem} Click the copy button under Claude's answer and press Enter again.")
                    continue
                activation = evidence = references = ""
                if row["batch"] != "skill_off":
                    activation, evidence, references = ask_activation(read, write)
                (run_dir / row["response_file"]).parent.mkdir(parents=True, exist_ok=True)
                (run_dir / row["response_file"]).write_bytes((response + "\n").encode("utf-8"))
                fill_row(row, session, today, activation, evidence, references, note, manifest_sha(row["batch"]))
                save_sheet(sheet, header, rows)
                previous = response
                saved += 1
                write(f"  Saved {row['response_file']} ({es.word_count(response)} words).")
                break
    except (Quit, KeyboardInterrupt):
        write("\nStopped. Everything saved so far is kept; rerun the same command to continue.")
        return 0
    left = len(pending_rows(run_dir, rows, batch))
    write(f"\nSession finished: {left} row(s) still without a response.")
    write(f"Next: python scripts/summarize_results.py {run_dir.as_posix()} --check-only")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect responses for a run with clipboard help.")
    parser.add_argument("run_dir")
    parser.add_argument("--batch", default=None, help="only this batch, e.g. skill_off or skill_on")
    args = parser.parse_args(argv)
    try:
        clipboard = SystemClipboard()
    except ClipboardError as exc:
        print(exc)
        return 1
    return run(Path(args.run_dir), clipboard=clipboard, batch=args.batch)


if __name__ == "__main__":
    sys.exit(main())
