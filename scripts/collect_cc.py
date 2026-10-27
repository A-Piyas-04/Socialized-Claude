"""Collect run-sheet responses automatically with Claude Code (`claude -p`) on a subscription.

    python scripts/collect_cc.py --smoke                                     # 2-row smoke test: skill on + skill off
    python scripts/collect_cc.py evaluation/runs/<run_id> --check-arms       # verify arm control; uses no quota
    python scripts/collect_cc.py evaluation/runs/<run_id> --dry-run          # print the plan; calls nothing
    python scripts/collect_cc.py evaluation/runs/<run_id>                    # fill every pending row
    python scripts/collect_cc.py evaluation/runs/<new_id> --create --subset pilot16 --samples 3

Auth: requires CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`). Refuses to run while
ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN is set, because in `-p` mode a set key takes
precedence over the subscription and would be billed.

Arm control: every row runs in a fresh sandbox directory outside the repository with its own
CLAUDE_CONFIG_DIR, so user-level skills, CLAUDE.md, memory and plugins cannot leak in. The
built skill ZIP for the row's batch is extracted to <sandbox>/.claude/skills/explanation-lab/.
Skill-off rows additionally pass --settings {"skillOverrides": {"explanation-lab": "off"}}.
The arm is never trusted: the `system/init` event is parsed and the row fails, and the process
is killed, if the observed skill state disagrees with the intended arm. A skill-off row also
fails if the transcript shows any Skill or Read call touching the skill.

Resumable: each response is written to responses/<row_id>.md as soon as it arrives, and rows
with a response file are skipped. Rate limits back off and retry up to a cap, then the row is
recorded as incomplete and the run moves on.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402
import make_run_sheet  # noqa: E402
from skilllib import SECRET_PATTERNS  # noqa: E402

SKILL_NAME = "explanation-lab"
SURFACE = "claude-code"
OPERATOR = "collect_cc"
TOKEN_ENV = "CLAUDE_CODE_OAUTH_TOKEN"
FORBIDDEN_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
TOOLS = ("Read", "Skill")
ALLOWED_API_KEY_SOURCES = {"none"}
DIST_DIR = es.REPO_ROOT / "dist"
SMOKE_DIR = es.REPO_ROOT / ".scratch" / "cc-smoke"
SMOKE_CASE = "mech_001"
SMOKE_CONDITIONS = ("A_normal", "C_skill_explicit")
RATE_LIMIT_RE = re.compile(r"(?i)rate.?limit|usage limit|overloaded|too many requests|429|529")
AUTH_RE = re.compile(r"(?i)not logged in|please run /login|invalid api key|auth token|authorization header|"
                     r"authentication")
PINNED_GLOBS = (
    "$LOCALAPPDATA/smart-claude/cc-*/node_modules/@anthropic-ai/claude-code-*/claude*",
    "~/.local/share/smart-claude/cc-*/node_modules/@anthropic-ai/claude-code-*/claude*",
)
EXTENSION_GLOBS = (
    "~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude*",
    "~/.cursor/extensions/anthropic.claude-code-*/resources/native-binary/claude*",
)


class HarnessError(RuntimeError):
    """A condition that must stop the whole run (auth, environment, missing build)."""


# ---------------------------------------------------------------------------
# Environment and binary
# ---------------------------------------------------------------------------

def environment_problems(env: dict[str, str], *, need_token: bool) -> list[str]:
    problems = []
    for name in FORBIDDEN_ENV:
        if env.get(name):
            problems.append(
                f"{name} is set. In `claude -p` a set key always takes precedence over the subscription "
                f"token and would be billed. Unset it in this shell yourself (collect_cc will not do it "
                f"for you), then rerun.")
    if need_token and not env.get(TOKEN_ENV):
        problems.append(
            f"{TOKEN_ENV} is not set. Run `claude setup-token` once, then set the printed token in this "
            f"shell's environment (never in a file inside the repository).")
    elif need_token and re.search(r"\s", env[TOKEN_ENV].strip()):
        problems.append(
            f"{TOKEN_ENV} contains spaces or line breaks, so it is not a single token. Re-run "
            f"`claude setup-token` and store only the token itself: one line, which for Claude Code "
            f"2.1.x begins 'sk-ant-oat'.")
    return problems


def normalize_token(env: dict[str, str]) -> bool:
    """Strip surrounding whitespace from the token in place; report whether anything changed."""
    token = env.get(TOKEN_ENV)
    if not token:
        return False
    env[TOKEN_ENV] = token.strip()
    return env[TOKEN_ENV] != token


def globbed(patterns: tuple[str, ...]) -> str | None:
    found = sorted(p for pattern in patterns for p in glob.glob(os.path.expanduser(os.path.expandvars(pattern)))
                   if Path(p).is_file() and Path(p).suffix in {"", ".exe"})
    return found[-1] if found else None


def find_claude(explicit: str | None, env: dict[str, str]) -> list[str]:
    """Explicit path, then CLAUDE_BIN, then the pinned install, then PATH, then an editor extension.

    Editor extensions update themselves (and briefly remove the binary) while running, so a sweep
    should use the pinned install: npm install --prefix <PINNED_HOME>/cc-<version> @anthropic-ai/claude-code@<version>
    """
    candidate = (explicit or env.get("CLAUDE_BIN") or globbed(PINNED_GLOBS) or shutil.which("claude")
                 or globbed(EXTENSION_GLOBS))
    if not candidate or not Path(candidate).is_file() and not shutil.which(candidate):
        raise HarnessError("Claude Code CLI not found. Pass --claude PATH or set CLAUDE_BIN.")
    return [candidate]


def scrub(text: str, secrets: list[str]) -> str:
    for secret in secrets:
        if secret and len(secret) >= 8:
            text = text.replace(secret, "[REDACTED]")
    for pattern in SECRET_PATTERNS.values():
        text = pattern.sub("[REDACTED]", text)
    return text


def secret_values(env: dict[str, str]) -> list[str]:
    return [env[name] for name in (TOKEN_ENV, *FORBIDDEN_ENV) if env.get(name)]


# ---------------------------------------------------------------------------
# Arms and sandboxes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Arm:
    batch: str
    skill_enabled: bool
    zip_path: Path
    manifest_path: Path


def arm_for_batch(batch: str, dist_dir: Path = DIST_DIR) -> Arm:
    if batch in {"skill_off", "skill_on", "variant:full"}:
        stem, folder = SKILL_NAME, dist_dir
    elif batch.startswith("variant:"):
        stem, folder = f"{SKILL_NAME}--{batch.split(':', 1)[1]}", dist_dir / "ablation"
    else:
        raise HarnessError(f"unknown batch '{batch}'")
    return Arm(batch, batch != "skill_off", folder / f"{stem}.zip", folder / f"{stem}.manifest.json")


def load_manifest(arm: Arm) -> dict:
    if not arm.zip_path.is_file() or not arm.manifest_path.is_file():
        raise HarnessError(f"{arm.zip_path} or its manifest is missing; run scripts/package_skill.py "
                           f"(--all-variants for ablation batches)")
    manifest = json.loads(arm.manifest_path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(arm.zip_path.read_bytes()).hexdigest()
    if actual != manifest["zip_sha256"]:
        raise HarnessError(f"{arm.zip_path} does not match its manifest; rebuild with scripts/package_skill.py")
    return manifest


def prepare_sandbox(root: Path, arm: Arm, manifest: dict) -> tuple[Path, Path, Path]:
    """Create <root>/work (cwd, with the skill installed), <root>/config and <root>/settings.json."""
    work, config = root / "work", root / "config"
    skills_dir = work / ".claude" / "skills"
    skills_dir.mkdir(parents=True)
    config.mkdir()
    with zipfile.ZipFile(arm.zip_path) as archive:
        for info in archive.infolist():
            parts = PurePosixPath(info.filename).parts
            if not parts or parts[0] != SKILL_NAME or ".." in parts or info.filename.startswith("/"):
                raise HarnessError(f"unexpected entry in {arm.zip_path.name}: {info.filename}")
            if info.is_dir():
                continue
            target = skills_dir.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))
    installed = skills_dir / SKILL_NAME
    for rel, digest in manifest["files"].items():
        path = installed / rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise HarnessError(f"installed {rel} does not match the manifest for {arm.batch}")
    settings = root / "settings.json"
    overrides = {} if arm.skill_enabled else {"skillOverrides": {SKILL_NAME: "off"}}
    settings.write_text(json.dumps(overrides), encoding="utf-8")
    return work, config, settings


def build_command(claude: list[str], settings: Path, model: str, effort: str | None) -> list[str]:
    cmd = [*claude, "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
           "--model", model,
           "--settings", str(settings), "--tools", ",".join(TOOLS), "--permission-mode", "dontAsk",
           "--no-session-persistence"]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def child_env(env: dict[str, str], config: Path, *, with_token: bool) -> dict[str, str]:
    out = dict(env)
    out["CLAUDE_CONFIG_DIR"] = str(config)
    out["DISABLE_AUTOUPDATER"] = "1"
    if not with_token:
        out.pop(TOKEN_ENV, None)
    return out


# ---------------------------------------------------------------------------
# Observing the arm (pure)
# ---------------------------------------------------------------------------

def observe_init(init: dict) -> dict:
    skills = init.get("skills")
    slash = init.get("slash_commands") or []
    return {
        "claude_code_version": init.get("claude_code_version"),
        "model": init.get("model"),
        "tools": sorted(init.get("tools") or []),
        "skills": sorted(skills) if isinstance(skills, list) else None,
        "skill_listed": isinstance(skills, list) and SKILL_NAME in skills,
        "slash_listed": SKILL_NAME in slash,
        "api_key_source": init.get("apiKeySource"),
        "permission_mode": init.get("permissionMode"),
    }


def arm_problems(skill_enabled: bool, observed: dict) -> list[str]:
    problems = []
    if observed["skills"] is None:
        problems.append("init event has no 'skills' list, so the arm cannot be verified")
    elif skill_enabled and not observed["skill_listed"]:
        problems.append(f"intended skill ON, but init.skills does not list {SKILL_NAME}")
    elif not skill_enabled and (observed["skill_listed"] or observed["slash_listed"]):
        problems.append(f"intended skill OFF, but init still lists {SKILL_NAME} (skillOverrides not honoured)")
    if observed["api_key_source"] not in ALLOWED_API_KEY_SOURCES:
        problems.append(f"apiKeySource is '{observed['api_key_source']}', expected 'none' (subscription OAuth)")
    if observed["tools"] != sorted(TOOLS):
        problems.append(f"tools are {observed['tools']}, expected {sorted(TOOLS)}")
    return problems


def tool_uses(event: dict) -> list[dict]:
    if event.get("type") != "assistant":
        return []
    content = (event.get("message") or {}).get("content") or []
    return [{"name": b.get("name"), "input": b.get("input") or {}}
            for b in content if isinstance(b, dict) and b.get("type") == "tool_use"]


def invokes_skill(use: dict) -> bool:
    if use["name"] != "Skill":
        return False
    value = str(use["input"].get("skill") or use["input"].get("command") or use["input"].get("name") or "")
    return value.lstrip("/").split(":")[-1].strip() == SKILL_NAME


def reads_skill_file(use: dict) -> str | None:
    if use["name"] != "Read":
        return None
    path = str(use["input"].get("file_path") or use["input"].get("path") or "").replace("\\", "/")
    marker = f"/skills/{SKILL_NAME}/"
    return path.split(marker, 1)[1] if marker in path else None


def touches_skill(use: dict) -> bool:
    return invokes_skill(use) or reads_skill_file(use) is not None


def observed_evidence(skill_enabled: bool, observed: dict | None, activated: bool) -> str:
    if observed is None:
        return "no system/init event observed"
    listed = "lists" if observed["skill_listed"] else "does not list"
    setting = "skillOverrides off" if not skill_enabled else "no override"
    call = "Skill tool invoked explanation-lab" if activated else "no Skill call for explanation-lab"
    return (f"cc init.skills {listed} {SKILL_NAME} ({setting}); {call}; "
            f"model={observed['model']}; cc={observed['claude_code_version']}")


# ---------------------------------------------------------------------------
# Running one invocation
# ---------------------------------------------------------------------------

@dataclass
class RowResult:
    status: str                       # ok | arm_mismatch | rate_limited | timeout | auth | error
    text: str = ""
    observed: dict | None = None
    problems: list[str] = field(default_factory=list)
    activated: bool = False
    references: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    result: dict = field(default_factory=dict)
    detail: str = ""
    turns: list[dict] = field(default_factory=list)   # [{"user": ..., "assistant": ...}] in order
    session_ids: list[str] = field(default_factory=list)


def classify_result(event: dict, auth_error: bool) -> tuple[str, str]:
    text = str(event.get("result") or "")
    if not event.get("is_error") and event.get("subtype") == "success" and text.strip():
        return "ok", ""
    status = event.get("api_error_status")
    if auth_error or AUTH_RE.search(text):
        return "auth", text[:300]
    if status in (429, 529) or RATE_LIMIT_RE.search(text):
        return "rate_limited", text[:300]
    return "error", text[:300] or f"subtype={event.get('subtype')}"


def user_line(text: str) -> bytes:
    return (json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n").encode("utf-8")


def run_invocation(cmd: list[str], turns: list[str], cwd: Path, env: dict[str, str], skill_enabled: bool,
                   timeout: float, *, stop_after_init: bool = False) -> RowResult:
    """Run one conversation in a single `claude -p` session, one user turn at a time.

    Each user turn is sent only after the previous turn's result event has arrived, so every
    assistant turn is generated live with the real conversation before it. Claude Code emits a
    system/init event per turn; every one is verified, and all must share one session id.
    """
    if not turns:
        raise ValueError("a conversation needs at least one user turn")
    with tempfile.TemporaryFile() as stderr_file:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=stderr_file)
        lines: queue.Queue = queue.Queue()

        def pump() -> None:
            for raw in proc.stdout:
                lines.put(raw)
            lines.put(None)

        def send(index: int) -> None:
            try:
                proc.stdin.write(user_line(turns[index]))
                proc.stdin.flush()
                if index == len(turns) - 1:
                    proc.stdin.close()
            except OSError:
                pass

        threading.Thread(target=pump, daemon=True).start()
        send(0)
        out = RowResult(status="error")
        auth_error = False
        deadline = time.monotonic() + timeout * len(turns)

        def finish(status: str, detail: str = "") -> RowResult:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            out.status, out.detail = status, detail or out.detail
            return out

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return finish("timeout", f"no result within {timeout:.0f}s")
            try:
                raw = lines.get(timeout=min(remaining, 1.0))
            except queue.Empty:
                continue
            if raw is None:
                break
            try:
                event = json.loads(raw.decode("utf-8", "replace"))
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("type") == "system" and event.get("subtype") == "init":
                out.observed = observe_init(event)
                out.problems = arm_problems(skill_enabled, out.observed)
                session = str(event.get("session_id") or "")
                if out.session_ids and session != out.session_ids[0]:
                    out.problems.append(f"turn {len(out.turns) + 1} started a new session; the conversation "
                                        "is not continuous")
                out.session_ids.append(session)
                if out.problems:
                    return finish("arm_mismatch", f"turn {len(out.turns) + 1}: " + "; ".join(out.problems))
                if stop_after_init:
                    return finish("ok", "arm verified at init; stopped before generation")
                continue
            if out.observed is None and event.get("type") in {"assistant", "result"}:
                out.problems = ["output arrived before any system/init event"]
                return finish("arm_mismatch", out.problems[0])
            if event.get("type") == "assistant" and event.get("error") == "authentication_failed":
                auth_error = True
            for use in tool_uses(event):
                out.tool_calls.append(use)
                if not skill_enabled and touches_skill(use):
                    out.problems = [f"skill-off row touched the skill via {use['name']}: {json.dumps(use['input'])}"]
                    return finish("arm_mismatch", out.problems[0])
                if invokes_skill(use):
                    out.activated = True
                ref = reads_skill_file(use)
                if ref and ref not in out.references and ref != "SKILL.md":
                    out.references.append(ref)
            if event.get("type") == "result":
                out.result = {k: event.get(k) for k in ("subtype", "is_error", "duration_ms", "num_turns",
                                                        "total_cost_usd", "usage", "api_error_status",
                                                        "terminal_reason")}
                status, detail = classify_result(event, auth_error)
                if status != "ok":
                    return finish(status, f"turn {len(out.turns) + 1}: {detail}" if len(turns) > 1 else detail)
                text = str(event["result"]).replace("\r\n", "\n").strip()
                out.turns.append({"user": turns[len(out.turns)], "assistant": text})
                if len(out.turns) == len(turns):
                    out.text = text
                    return finish("ok")
                send(len(out.turns))
        proc.wait()
        if out.observed is None:
            out.problems = ["process exited without a system/init event"]
            status = "arm_mismatch"
        else:
            status = "error"
        stderr_file.seek(0)
        tail = stderr_file.read().decode("utf-8", "replace")[-300:].strip()
        out.status, out.detail = status, out.problems[0] if out.problems else f"exited {proc.returncode}: {tail}"
        return out


# ---------------------------------------------------------------------------
# Run sheet
# ---------------------------------------------------------------------------

def response_done(run_dir: Path, row: dict) -> bool:
    path = run_dir / row["response_file"]
    return path.is_file() and bool(path.read_text(encoding="utf-8").strip())


def pending_rows(run_dir: Path, rows: list[dict], only: set[str] | None = None) -> list[dict]:
    todo = [r for r in rows if not response_done(run_dir, r) and (only is None or r["row_id"] in only)]
    return sorted(todo, key=lambda r: int(r["order"] or 0))


def save_sheet(path: Path, header: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(".csv.tmp")
    es.write_csv(tmp, header, rows)
    os.replace(tmp, path)


def row_fields(row: dict, result: RowResult, skill_enabled: bool, effort: str | None, zip_sha: str,
               today: str) -> dict[str, str]:
    evidence = observed_evidence(skill_enabled, result.observed, result.activated)
    return {
        "date": today,
        "surface": SURFACE,
        "model_label": (result.observed or {}).get("model") or "",
        "thinking_setting": f"effort={effort or 'default'}",
        "skill_zip_sha256": zip_sha if skill_enabled else row.get("skill_zip_sha256", ""),
        "activation_observed": ("yes" if result.activated else "no") if skill_enabled else "na",
        "activation_evidence": evidence,
        "references_loaded": ";".join(result.references),
        "operator": OPERATOR,
    }


def transcript_path(run_dir: Path, row: dict) -> Path:
    return (run_dir / row["response_file"]).with_suffix(".turns.json")


def run_versions(run_dir: Path) -> set[str]:
    """Claude Code versions of the rows already collected in this run."""
    found = set()
    for path in sorted((run_dir / "cc_meta").glob("*.json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta.get("status") == "ok" and (meta.get("observed_init") or {}).get("claude_code_version"):
            found.add(meta["observed_init"]["claude_code_version"])
    return found


def write_meta(run_dir: Path, row_id: str, payload: dict, secrets: list[str]) -> None:
    path = run_dir / "cc_meta" / f"{row_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps({"notice": es.SURFACE_NOTICE, **payload}, indent=2, sort_keys=True) + "\n"
    path.write_bytes(scrub(text, secrets).encode("utf-8"))


def backfill_from_meta(run_dir: Path, rows: list[dict]) -> int:
    """Fill sheet fields for rows whose response exists but whose sheet update was lost (crash)."""
    filled = 0
    for row in rows:
        meta_path = run_dir / "cc_meta" / f"{row['row_id']}.json"
        if row["date"] or not response_done(run_dir, row) or not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("status") == "ok" and meta.get("row_fields"):
            row.update(meta["row_fields"])
            filled += 1
    return filled


def write_notice(run_dir: Path, model: str, effort: str | None, claude: list[str]) -> None:
    lines = [
        "# Collection notice", "",
        es.SURFACE_NOTICE, "",
        "Any judge scores derived from these responses: " + es.JUDGE_NOTICE, "",
        "## How these responses were collected", "",
        f"- Collector: `scripts/collect_cc.py` (operator `{OPERATOR}`), surface `{SURFACE}`.",
        f"- Requested model: `{model}`; effort: `{effort or 'default'}`. The resolved model per row is in "
        "the run sheet's `model_label` column.",
        f"- Tools available to the model: {', '.join(TOOLS)}; permission mode `dontAsk`; no session persistence.",
        "- Each row ran in a fresh sandbox outside the repository with its own `CLAUDE_CONFIG_DIR`, so no "
        "user-level skills, CLAUDE.md, memory or plugins were present. The batch's built ZIP was installed "
        f"as a project skill at `.claude/skills/{SKILL_NAME}/`; skill-off rows also passed "
        f"`skillOverrides: {{\"{SKILL_NAME}\": \"off\"}}` through `--settings`.",
        "- Every row's arm was verified from the `system/init` event; the observation is recorded in "
        "`activation_evidence` and in `cc_meta/<row_id>.json`.",
        f"- CLI: `{Path(claude[-1]).name}`; version per row in `cc_meta/`.",
        "",
    ]
    (run_dir / "COLLECTION_NOTICE.md").write_bytes("\n".join(lines).encode("utf-8"))


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

@dataclass
class Options:
    model: str = "sonnet"
    effort: str | None = None
    timeout: float = 600.0
    max_retries: int = 4
    backoff: float = 60.0
    max_consecutive_incomplete: int = 3
    keep_sandbox: bool = False


def collect(run_dir: Path, claude: list[str], env: dict[str, str], opts: Options, *,
            only: set[str] | None = None, limit: int | None = None, write: Callable[[str], None] = print,
            sleep: Callable[[float], None] = time.sleep, today: str | None = None) -> int:
    problems = environment_problems(env, need_token=True)
    if problems:
        raise HarnessError("\n".join(problems))
    sheet = run_dir / "run_sheet.csv"
    if not sheet.is_file():
        raise HarnessError(f"run sheet not found: {sheet} (use --create)")
    header, rows = es.read_csv(sheet)
    missing = [c for c in es.RESULTS_COLUMNS if c not in header]
    if missing:
        raise HarnessError(f"{sheet} is missing columns {missing}")
    secrets = secret_values(env)
    today = today or dt.date.today().isoformat()
    if backfill_from_meta(run_dir, rows):
        save_sheet(sheet, header, rows)
    write_notice(run_dir, opts.model, opts.effort, claude)
    todo = pending_rows(run_dir, rows, only)
    if limit is not None:
        todo = todo[:limit]
    write(f"{run_dir.name}: {len(rows) - len(pending_rows(run_dir, rows))}/{len(rows)} done, "
          f"{len(todo)} to run now.")
    manifests: dict[str, dict] = {}
    versions = run_versions(run_dir)
    failed = incomplete = consecutive = 0
    for n, row in enumerate(todo, start=1):
        arm = arm_for_batch(row["batch"])
        if arm.batch not in manifests:
            manifests[arm.batch] = load_manifest(arm)
        manifest = manifests[arm.batch]
        if arm.skill_enabled and row["skill_zip_sha256"] and row["skill_zip_sha256"] != manifest["zip_sha256"]:
            raise HarnessError(f"{row['row_id']}: run sheet records skill ZIP {row['skill_zip_sha256'][:12]}… but "
                               f"{arm.zip_path.name} is now {manifest['zip_sha256'][:12]}…; the build changed "
                               "mid-run. Start a new run.")
        turns = es.read_turns(run_dir / row["message_file"])
        result = RowResult(status="error")
        for attempt in range(opts.max_retries + 1):
            root = Path(tempfile.mkdtemp(prefix="cc_row_"))
            try:
                work, config, settings = prepare_sandbox(root, arm, manifest)
                cmd = build_command(claude, settings, opts.model, opts.effort)
                result = run_invocation(cmd, turns, work, child_env(env, config, with_token=True),
                                        arm.skill_enabled, opts.timeout)
            finally:
                if not opts.keep_sandbox:
                    shutil.rmtree(root, ignore_errors=True)
            if result.status not in {"rate_limited", "timeout", "error"} or attempt == opts.max_retries:
                break
            wait = opts.backoff * (2 ** attempt)
            write(f"  {row['row_id']}: {result.status} ({scrub(result.detail, secrets)[:120]}); "
                  f"retry {attempt + 1}/{opts.max_retries} in {wait:.0f}s")
            sleep(wait)
        version = (result.observed or {}).get("claude_code_version")
        if result.status == "ok" and versions and version not in versions:
            result.status = "version_drift"
            result.detail = f"Claude Code is now {version}; earlier rows of this run used {sorted(versions)}"
        fields = row_fields(row, result, arm.skill_enabled, opts.effort, manifest["zip_sha256"], today)
        meta = {"row_id": row["row_id"], "batch": row["batch"], "intended_skill_enabled": arm.skill_enabled,
                "status": result.status, "detail": result.detail, "observed_init": result.observed,
                "arm_problems": result.problems, "tool_calls": result.tool_calls, "result": result.result,
                "user_turns": len(turns), "row_fields": fields if result.status == "ok" else None}
        write_meta(run_dir, row["row_id"], meta, secrets)
        if result.status == "auth":
            raise HarnessError(f"authentication failed ({scrub(result.detail, secrets)}). Check {TOKEN_ENV}.")
        if result.status == "version_drift":
            raise HarnessError(f"{result.detail}. Pin the CLI with --claude (or CLAUDE_BIN) to the version the "
                               "run started with, or start a new run.")
        if result.status == "ok":
            versions.add(version)
            response_path = run_dir / row["response_file"]
            response_path.parent.mkdir(parents=True, exist_ok=True)
            response_path.write_bytes((scrub(result.text, secrets) + "\n").encode("utf-8"))
            if len(turns) > 1:
                transcript = json.dumps({"notice": es.SURFACE_NOTICE, "turns": result.turns}, indent=2,
                                        ensure_ascii=False) + "\n"
                transcript_path(run_dir, row).write_bytes(scrub(transcript, secrets).encode("utf-8"))
            row.update(fields)
            row["notes"] = ""
            consecutive = 0
            write(f"[{n}/{len(todo)}] {row['row_id']}: ok ({es.word_count(result.text)} words; "
                  f"activation {fields['activation_observed']})")
        elif result.status == "arm_mismatch":
            row["activation_evidence"] = fields["activation_evidence"]
            row["notes"] = scrub(f"collect_cc: ARM MISMATCH: {result.detail}", secrets)
            save_sheet(sheet, header, rows)
            failed += 1
            write(f"[{n}/{len(todo)}] {row['row_id']}: FAILED, arm mismatch: {result.detail}")
            write("Stopping: an arm mismatch means the arm control is broken for this configuration.")
            return 3
        else:
            row["notes"] = scrub(f"collect_cc: incomplete ({result.status}): {result.detail}", secrets)[:300]
            incomplete += 1
            consecutive += 1
            write(f"[{n}/{len(todo)}] {row['row_id']}: incomplete ({result.status})")
        save_sheet(sheet, header, rows)
        if consecutive >= opts.max_consecutive_incomplete:
            write(f"Stopping after {consecutive} consecutive incomplete rows (quota is probably exhausted). "
                  "Rerun the same command later to resume.")
            break
    left = len(pending_rows(run_dir, rows))
    write(f"Finished: {incomplete} incomplete, {failed} failed, {left} row(s) without a response.")
    if not left:
        write(f"Next: python scripts/summarize_results.py {run_dir.as_posix()} --check-only")
    return 0 if not incomplete and not failed else 2


def check_arms(run_dir: Path | None, batches: list[str], claude: list[str], env: dict[str, str], opts: Options,
               write: Callable[[str], None] = print) -> int:
    """Verify each arm from the init event with the token withheld, so no request can be billed."""
    problems = environment_problems(env, need_token=False)
    if problems:
        raise HarnessError("\n".join(problems))
    bad = 0
    for batch in batches:
        arm = arm_for_batch(batch)
        manifest = load_manifest(arm)
        root = Path(tempfile.mkdtemp(prefix="cc_arm_"))
        try:
            work, config, settings = prepare_sandbox(root, arm, manifest)
            cmd = build_command(claude, settings, opts.model, opts.effort)
            result = run_invocation(cmd, ["Reply with the word ok."], work,
                                    child_env(env, config, with_token=False), arm.skill_enabled,
                                    min(opts.timeout, 120), stop_after_init=True)
        finally:
            shutil.rmtree(root, ignore_errors=True)
        verdict = "OK" if result.observed is not None and not result.problems else "MISMATCH"
        bad += verdict != "OK"
        write(f"{batch:<22} intended skill {'ON ' if arm.skill_enabled else 'OFF'} -> {verdict}: "
              f"{observed_evidence(arm.skill_enabled, result.observed, False)}")
        for problem in result.problems:
            write(f"    problem: {problem}")
    return 1 if bad else 0


def dry_run(run_dir: Path, claude: list[str], env: dict[str, str], opts: Options, only: set[str] | None,
            limit: int | None, write: Callable[[str], None] = print) -> int:
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    todo = pending_rows(run_dir, rows, only)
    if limit is not None:
        todo = todo[:limit]
    for problem in environment_problems(env, need_token=True):
        write(f"A real run would refuse to start: {problem}")
    for row in todo:
        arm = arm_for_batch(row["batch"])
        cmd = build_command(claude, Path("<sandbox>/settings.json"), opts.model, opts.effort)
        n_turns = len(es.read_turns(run_dir / row["message_file"]))
        write(f"{row['order']:>4} {row['row_id']}: skill {'ON ' if arm.skill_enabled else 'OFF'} "
              f"({arm.zip_path.name}); {n_turns} user turn(s) from {row['message_file']}")
        write(f"       {' '.join(cmd)}")
    write(f"Planned invocations: {len(todo)} (of {len(rows)} rows; up to {len(todo) * (opts.max_retries + 1)} "
          f"with retries). Nothing was called.")
    return 0


STDIN_PROBE = "naïve café — 日本語 — ½ °C — Ωμέγα — “quotes”"


CONTEXT_PROBE_WORD = "marmalade-417"


def probe(claude: list[str], env: dict[str, str], opts: Options, turns: list[str]) -> RowResult:
    arm = arm_for_batch("skill_off")
    root = Path(tempfile.mkdtemp(prefix="cc_probe_"))
    try:
        work, config, settings = prepare_sandbox(root, arm, load_manifest(arm))
        return run_invocation(build_command(claude, settings, opts.model, opts.effort), turns, work,
                              child_env(env, config, with_token=True), False, min(opts.timeout, 180))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def stdin_probe(claude: list[str], env: dict[str, str], opts: Options) -> tuple[bool, str]:
    """Ask the model to echo a non-ASCII string, to prove stdin keeps UTF-8."""
    result = probe(claude, env, opts, [f"Reply with exactly this text and nothing else:\n{STDIN_PROBE}\n"])
    if result.status != "ok":
        return False, f"probe call {result.status}: {result.detail}"
    return STDIN_PROBE in result.text, "round-trip intact" if STDIN_PROBE in result.text else "text altered in transit"


def context_probe(claude: list[str], env: dict[str, str], opts: Options) -> tuple[bool, str]:
    """Two live turns: the second can only be answered if the first is in the conversation."""
    result = probe(claude, env, opts, [f"Remember this code word: {CONTEXT_PROBE_WORD}. Reply only with: noted.",
                                       "What was the code word? Reply with the code word only."])
    if result.status != "ok":
        return False, f"probe call {result.status}: {result.detail}"
    kept = CONTEXT_PROBE_WORD in result.text and len(result.turns) == 2 and len(set(result.session_ids)) == 1
    return kept, (f"turn 2 recalled turn 1 in one session ({len(result.session_ids)} init events)" if kept
                  else f"context lost: turn 2 replied {result.text[:60]!r}")


def create_smoke_run(base: Path = SMOKE_DIR) -> Path:
    run_dir = base
    if run_dir.exists():
        shutil.rmtree(run_dir)
    make_run_sheet.main(["--run-id", run_dir.name, "--runs-dir", str(run_dir.parent), "--cases", SMOKE_CASE,
                         "--conditions", ",".join(SMOKE_CONDITIONS), "--samples", "1"])
    return run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect run-sheet responses with Claude Code.")
    parser.add_argument("run_dir", nargs="?")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--smoke", action="store_true", help="arm check + 2-row run (skill on, skill off)")
    mode.add_argument("--check-arms", action="store_true", help="verify arm control only; uses no quota")
    mode.add_argument("--dry-run", action="store_true", help="print planned invocations; call nothing")
    parser.add_argument("--create", action="store_true", help="create the run sheet first (make_run_sheet.py)")
    parser.add_argument("--subset", default="pilot16")
    parser.add_argument("--conditions", default=None)
    parser.add_argument("--samples", type=int, default=3, help="samples per cell when creating (default 3)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--rows", default=None, help="comma-separated row ids to run")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--effort", default=None)
    parser.add_argument("--claude", default=None, help="path to the claude executable")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--backoff", type=float, default=60.0, help="first backoff in seconds (doubles)")
    parser.add_argument("--keep-sandbox", action="store_true")
    args = parser.parse_args(argv)

    sys.stdout.reconfigure(line_buffering=True)
    env = dict(os.environ)
    if normalize_token(env):
        print(f"Note: surrounding whitespace was removed from {TOKEN_ENV} for this run.")
    opts = Options(model=args.model, effort=args.effort, timeout=args.timeout, max_retries=args.max_retries,
                   backoff=args.backoff, keep_sandbox=args.keep_sandbox)
    only = {r.strip() for r in args.rows.split(",") if r.strip()} if args.rows else None
    try:
        claude = find_claude(args.claude, env)
        if args.smoke:
            run_dir = create_smoke_run()
            _, rows = es.read_csv(run_dir / "run_sheet.csv")
            print("== Arm check (token withheld; no quota used) ==")
            if check_arms(run_dir, sorted({r["batch"] for r in rows}), claude, env, opts):
                print("Arm check failed; not generating.")
                return 1
            print("== Generation (2 rows) ==")
            code = collect(run_dir, claude, env, opts)
            if code:
                return code
            failures = 0
            for title, check in (("Non-ASCII stdin round-trip", stdin_probe),
                                 ("Multi-turn context retention", context_probe)):
                ok, detail = check(claude, env, opts)
                failures += not ok
                print(f"== {title} ==\n{'OK' if ok else 'FAILED'}: {detail}")
            return 1 if failures else 0
        if not args.run_dir:
            parser.error("run_dir is required unless --smoke is given")
        run_dir = Path(args.run_dir)
        if args.create:
            cmd = ["--run-id", run_dir.name, "--runs-dir", str(run_dir.parent), "--samples", str(args.samples),
                   "--seed", str(args.seed), "--subset", args.subset]
            if args.conditions:
                cmd += ["--conditions", args.conditions]
            make_run_sheet.main(cmd)
        if args.check_arms:
            _, rows = es.read_csv(run_dir / "run_sheet.csv")
            return check_arms(run_dir, sorted({r["batch"] for r in rows}), claude, env, opts)
        if args.dry_run:
            return dry_run(run_dir, claude, env, opts, only, args.limit)
        return collect(run_dir, claude, env, opts, only=only, limit=args.limit)
    except HarnessError as exc:
        print(f"collect_cc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
