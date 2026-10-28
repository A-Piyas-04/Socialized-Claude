"""Local token-budget report for every Socialized-Claude instruction surface.

    python scripts/token_budget.py                         # markdown report
    python scripts/token_budget.py --check                 # exit 1 when a component exceeds its budget
    python scripts/token_budget.py --json report.json      # machine-readable report
    python scripts/token_budget.py --budget activation=4800
    python scripts/token_budget.py --tokenizer heuristic   # force the stdlib estimator
    python scripts/token_budget.py --write-baseline        # record current counts as the baseline

Counts are local estimates. They are not measured Claude API usage: Anthropic does
not publish the tokenizer of current Claude models. Two counters are available:

  claude-legacy  Anthropic's public pre-Claude-3 tokenizer, read from the local
                 Hugging Face cache (Xenova/claude-tokenizer, tokenizer.json) or
                 from --tokenizer-file / SOCIALIZED_TOKENIZER_FILE. Never downloads.
  heuristic      Standard library only. Counts word, digit and symbol pieces and
                 scales them by PIECES_PER_TOKEN, calibrated against claude-legacy
                 on this repository's instruction files (within about 5% per file).

"auto" uses claude-legacy when the file and the `tokenizers` package are present,
otherwise heuristic. Budgets live in scripts/token_budgets.json: `max` gates
--check, `target` is advisory and only reported, and null means no limit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402
from package_skill import render_files  # noqa: E402

BUDGETS_FILE = Path(__file__).resolve().parent / "token_budgets.json"
BASELINE_FILE = Path(__file__).resolve().parent / "token_baseline.json"
PLUGIN_SKILL_DIR = lib.REPO_ROOT / "plugins" / "socialized" / "skills" / "socialized"
PERSISTENT_DOC = lib.REPO_ROOT / "docs" / "phase-2-implementation.md"
COMMUNICATION_DIR = lib.REPO_ROOT / "communication"
AGENTS_FILE = lib.REPO_ROOT / "AGENTS.md"

COMPACTION_KEEP = 5000  # Claude Code re-attaches the first 5,000 tokens of a skill after compaction
LEGACY_REPO = "models--Xenova--claude-tokenizer"
PIECE_RE = re.compile(r"[A-Za-z]+|\d|[^\sA-Za-z\d]")
PIECES_PER_TOKEN = 0.935

ALWAYS = "always: skill listing, every turn while the skill is enabled"
ON_ACTIVATION = "on activation: enters the conversation and stays for later turns"
ON_DEMAND = "on demand: only when Claude reads the file"
OPT_IN = "every turn, only where the person pastes it (opt-in)"
NOT_SHIPPED = "never at runtime: repository source, not shipped"
DEV_ONLY = "development sessions in this repository only; not shipped"


# ---------------------------------------------------------------------------
# Tokenizers
# ---------------------------------------------------------------------------

class Counter:
    name = "base"

    def count(self, text: str) -> int:
        raise NotImplementedError


class HeuristicCounter(Counter):
    name = "heuristic"

    def count(self, text: str) -> int:
        return round(len(PIECE_RE.findall(text)) / PIECES_PER_TOKEN)


class LegacyCounter(Counter):
    name = "claude-legacy"

    def __init__(self, path: Path):
        from tokenizers import Tokenizer  # imported lazily: optional dependency
        self.path = path
        self._tok = Tokenizer.from_file(str(path))

    def count(self, text: str) -> int:
        return len(self._tok.encode(text).ids)


def find_legacy_file(explicit: str | None = None) -> Path | None:
    candidates: list[Path] = []
    for value in (explicit, os.environ.get("SOCIALIZED_TOKENIZER_FILE")):
        if value:
            candidates.append(Path(value))
    hub = os.environ.get("HF_HUB_CACHE")
    if not hub:
        home = os.environ.get("HF_HOME") or str(Path.home() / ".cache" / "huggingface")
        hub = str(Path(home) / "hub")
    candidates.extend(sorted((Path(hub) / LEGACY_REPO / "snapshots").glob("*/tokenizer.json")))
    return next((p for p in candidates if p.is_file()), None)


def make_counter(kind: str = "auto", tokenizer_file: str | None = None) -> Counter:
    if kind == "heuristic":
        return HeuristicCounter()
    path = find_legacy_file(tokenizer_file)
    if path is not None:
        try:
            return LegacyCounter(path)
        except ImportError:
            if kind == "claude-legacy":
                raise SystemExit("claude-legacy needs the `tokenizers` package: pip install tokenizers")
    elif kind == "claude-legacy":
        raise SystemExit("claude-legacy tokenizer.json not found locally; pass --tokenizer-file "
                         "or set SOCIALIZED_TOKENIZER_FILE (this tool never downloads)")
    return HeuristicCounter()


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

@dataclass
class Component:
    id: str
    group: str
    loading: str
    text: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def persistent_snippets(doc: Path = PERSISTENT_DOC) -> dict[str, str]:
    """The opt-in standing-guidance snippets published in the Phase 2 guide."""
    text = read(doc)
    snippets: dict[str, str] = {}
    project = re.search(r"### claude\.ai Projects.*?```text\n(.*?)```", text, re.DOTALL)
    if project:
        snippets["persistent:project-instructions"] = project.group(1)
    block = re.search(r"(<!-- BEGIN socialized-claude -->.*?<!-- END socialized-claude -->)", text, re.DOTALL)
    if block:
        snippets["persistent:claude-md"] = block.group(1) + "\n"
    return snippets


def collect(skill_dir: Path = lib.SKILL_DIR) -> list[Component]:
    shipped = {rel: data.decode("utf-8") for rel, data in render_files(skill_dir, lib.VARIANTS["full"]).items()}
    meta, _, _ = lib.split_frontmatter(shipped["SKILL.md"])
    components = [
        Component("metadata", "runtime", ALWAYS, f"{meta['name']}: {meta['description']}"),
        Component("activation", "runtime", ON_ACTIVATION, shipped["SKILL.md"]),
    ]
    for rel in sorted(r for r in shipped if r != "SKILL.md"):
        components.append(Component(f"ref:{Path(rel).name}", "runtime", ON_DEMAND, shipped[rel]))
    for cid, text in persistent_snippets().items():
        components.append(Component(cid, "persistent", OPT_IN, text))
    for path in sorted(COMMUNICATION_DIR.glob("*.md")):
        components.append(Component(f"repo:communication/{path.name}", "repository", NOT_SHIPPED, read(path)))
    for path in lib.iter_skill_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        components.append(Component(f"repo:skill-source/{rel}", "repository", NOT_SHIPPED, read(path)))
    if AGENTS_FILE.is_file():
        components.append(Component("dev:AGENTS.md", "development", DEV_ONLY, read(AGENTS_FILE)))
    return components


def sections_past(text: str, counter: Counter, keep: int = COMPACTION_KEEP) -> list[str]:
    """`##` headings of `text` that end past the first `keep` tokens; '(partly)' if they start before."""
    starts = [m.start() for m in re.finditer(r"(?m)^## ", text)] + [len(text)]
    past = []
    for begin, end in zip(starts, starts[1:]):
        if counter.count(text[:end]) <= keep:
            continue
        heading = text[begin:end].splitlines()[0][3:]
        past.append(heading + (" (partly)" if counter.count(text[:begin]) < keep else ""))
    return past


def plugin_in_sync(skill_dir: Path = lib.SKILL_DIR, plugin_skill_dir: Path = PLUGIN_SKILL_DIR) -> bool:
    shipped = render_files(skill_dir, lib.VARIANTS["full"])
    on_disk = {p.relative_to(plugin_skill_dir).as_posix(): p.read_bytes()
               for p in plugin_skill_dir.rglob("*") if p.is_file()} if plugin_skill_dir.is_dir() else {}
    return shipped == on_disk


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def load_budgets(path: Path = BUDGETS_FILE, overrides: list[str] | None = None) -> dict[str, dict]:
    """Map component id to {"max": int | None, "target": int | None}."""
    data = json.loads(read(path)) if path.is_file() else {"budgets": {}}
    budgets = {cid: {"max": spec.get("max"), "target": spec.get("target")}
               for cid, spec in data.get("budgets", {}).items()}
    for item in overrides or []:
        cid, _, value = item.partition("=")
        if not cid or not value:
            raise SystemExit(f"--budget expects component=N or component=none, got {item!r}")
        budgets.setdefault(cid, {"max": None, "target": None})["max"] = (
            None if value.lower() in {"none", "null"} else int(value))
    return budgets


def load_baseline(path: Path = BASELINE_FILE) -> dict:
    return json.loads(read(path)) if path.is_file() else {}


def build_report(counter: Counter, budgets: dict[str, dict], baseline: dict,
                 skill_dir: Path = lib.SKILL_DIR) -> dict:
    components = collect(skill_dir)
    base = baseline.get("counts", {}).get(counter.name, {})
    rows = []
    for comp in components:
        tokens = counter.count(comp.text)
        before = base.get(comp.id)
        limits = budgets.get(comp.id, {})
        budget, target = limits.get("max"), limits.get("target")
        rows.append({
            "id": comp.id, "group": comp.group, "loading": comp.loading,
            "tokens": tokens, "chars": len(comp.text),
            "baseline": before,
            "change_pct": None if not before else round(100 * (tokens - before) / before, 1),
            "budget": budget,
            "over_budget": budget is not None and tokens > budget,
            "target": target,
            "above_target": target is not None and tokens > target,
        })
    by_id = {r["id"]: r["tokens"] for r in rows}

    def total(prefix: str = "", group: str | None = None) -> int:
        return sum(r["tokens"] for r in rows
                   if r["id"].startswith(prefix) and (group is None or r["group"] == group))

    refs = total("ref:")
    totals = {
        "repository_instructions": total("repo:") + total("persistent:") + total("dev:"),
        "distributable_skill": by_id["activation"] + refs,
        "loaded_on_activation": by_id["activation"],
        "references_on_demand": refs,
        "always_on_metadata": by_id["metadata"],
        "persistent_opt_in": total("persistent:"),
    }
    base_totals = baseline.get("totals", {}).get(counter.name, {})
    activation_text = next(c.text for c in components if c.id == "activation")
    return {
        "tokenizer": counter.name,
        "disclaimer": "Local token estimates. Not measured Claude API usage.",
        "plugin_copy_identical": plugin_in_sync(skill_dir),
        "past_compaction_keep": sections_past(activation_text, counter),
        "components": rows,
        "totals": totals,
        "baseline_source": baseline.get("source"),
        "baseline_totals": base_totals,
        "over_budget": [r["id"] for r in rows if r["over_budget"]],
        "above_target": [r["id"] for r in rows if r["above_target"]],
    }


def pct(now: int, before: int | None) -> str:
    if not before:
        return "n/a"
    return f"{100 * (now - before) / before:+.1f}%"


def render_markdown(report: dict) -> str:
    lines = [
        f"# Token budget report ({report['tokenizer']})",
        "",
        report["disclaimer"],
        f"Plugin skill copy identical to the claude.ai package: "
        f"{'yes' if report['plugin_copy_identical'] else 'NO (run scripts/build_plugin.py)'}.",
        f"Baseline: {report['baseline_source'] or 'none recorded'}.",
        f"SKILL.md sections past the first {COMPACTION_KEEP} tokens (not re-attached by Claude Code "
        f"after auto-compaction): {', '.join(report['past_compaction_keep']) or 'none'}.",
        "",
        "| Component | Loads | Baseline | Now | Change | Max (gates) | Target |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in report["components"]:
        budget = "—" if r["budget"] is None else f"{r['budget']}{' OVER' if r['over_budget'] else ''}"
        target = "—" if r["target"] is None else f"{r['target']}{' above' if r['above_target'] else ''}"
        base = "—" if r["baseline"] is None else str(r["baseline"])
        lines.append(f"| `{r['id']}` | {r['loading']} | {base} | {r['tokens']} | "
                     f"{pct(r['tokens'], r['baseline'])} | {budget} | {target} |")
    lines += ["", "| Total | Baseline | Now | Change |", "|---|---:|---:|---:|"]
    for key, value in report["totals"].items():
        before = report["baseline_totals"].get(key)
        lines.append(f"| {key.replace('_', ' ')} | {before if before is not None else '—'} | {value} | "
                     f"{pct(value, before)} |")
    return "\n".join(lines) + "\n"


def write_baseline(report: dict, source: str, path: Path = BASELINE_FILE) -> None:
    data = load_baseline(path)
    data["source"] = source
    data.setdefault("counts", {})[report["tokenizer"]] = {r["id"]: r["tokens"] for r in report["components"]}
    data.setdefault("totals", {})[report["tokenizer"]] = report["totals"]
    path.write_bytes((json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report local token counts for the instruction surfaces.")
    parser.add_argument("--tokenizer", choices=("auto", "claude-legacy", "heuristic"), default="auto")
    parser.add_argument("--tokenizer-file", help="path to a Hugging Face tokenizer.json")
    parser.add_argument("--budgets", default=str(BUDGETS_FILE), help="budget config (JSON)")
    parser.add_argument("--budget", action="append", default=[], metavar="ID=N",
                        help="override one budget; N may be 'none'")
    parser.add_argument("--baseline", default=str(BASELINE_FILE))
    parser.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    parser.add_argument("--check", action="store_true", help="exit 1 when any component exceeds its budget")
    parser.add_argument("--write-baseline", metavar="SOURCE",
                        help="record current counts as the baseline, labelled SOURCE")
    args = parser.parse_args(argv)

    counter = make_counter(args.tokenizer, args.tokenizer_file)
    report = build_report(counter, load_budgets(Path(args.budgets), args.budget), load_baseline(Path(args.baseline)))
    if args.write_baseline:
        write_baseline(report, args.write_baseline, Path(args.baseline))
        print(f"Recorded {counter.name} baseline in {Path(args.baseline).name}")
        return 0
    if args.json:
        Path(args.json).write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))
    sys.stdout.write(render_markdown(report))
    if report["above_target"]:
        print(f"Above advisory target (does not fail): {', '.join(report['above_target'])}")
    if args.check and report["over_budget"]:
        print(f"Over budget: {', '.join(report['over_budget'])}")
        return 1
    if args.check:
        print("All budgeted components are within budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
