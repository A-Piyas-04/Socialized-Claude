"""Structural linter for a response: form descriptors and decorative-structure flags.

    python scripts/lint_response.py response.md                 # human-readable
    python scripts/lint_response.py response.md --json          # machine-readable
    type response.md | python scripts/lint_response.py -        # stdin
    python scripts/lint_response.py --question "Why ...?" response.md
    python scripts/lint_response.py --regenerate                # research/baseline_structural_metrics.json

Exit status is 1 when any decorative-structure flag fires, 0 otherwise.

These are structural descriptors, not a comprehension score. A response can score perfectly on
every metric here and still be wrong, and the linter cannot tell.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import structural_metrics as sm  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_INPUT = REPO_ROOT / "research-results-2026-10-26" / "inputs" / "input-dataset.json"
BASELINE_PATH = REPO_ROOT / "research" / "baseline_structural_metrics.json"
DISCLAIMER = ("Structural descriptors, not a comprehension score. A response can score perfectly on every "
              "metric here and still be wrong, and the linter cannot tell.")


def regenerate(out: Path = BASELINE_PATH) -> dict:
    """Metrics for the archive's 10 base answers (5 questions x 2 providers), read-only."""
    data = json.loads(ARCHIVE_INPUT.read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in data["questions"]}
    answers = []
    for a in data["imported_answers"]:
        if a["label"].split(" - ", 1)[1].strip().lower() != "base":
            continue
        q = questions[a["question_id"]]
        answers.append({"topic": q["topic"], "provider": a["provider"], "model_id": a["model_id"],
                        "metrics": sm.metrics(a["text"], q["text"])})
    answers.sort(key=lambda r: (r["topic"], r["provider"]))
    result = {"disclaimer": DISCLAIMER,
              "source": ARCHIVE_INPUT.relative_to(REPO_ROOT).as_posix() + " (base answers; read-only)",
              "caveat": "The archive answers were copied from web chat with unknown settings. No heading survives "
                        "in any of them, so markdown structure was probably lost in copying; heading counts here "
                        "understate what the reader saw.",
              "answers": answers}
    out.write_bytes((json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    return result


def render(result: dict) -> str:
    lines = [f"{k}: {v}" for k, v in result.items() if k != "decorative_structure_flags"]
    flags = result["decorative_structure_flags"]
    lines.append("decorative_structure_flags: " + (", ".join(flags) if flags else "none"))
    lines.append(f"({DISCLAIMER})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Structural linter for a markdown response.\n" + DISCLAIMER,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", help="response file, or - for stdin")
    parser.add_argument("--question", default=None, help="the question, for the answer-first restatement test")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--regenerate", action="store_true", help=f"rewrite {BASELINE_PATH.relative_to(REPO_ROOT)}")
    args = parser.parse_args(argv)
    if args.regenerate:
        result = regenerate()
        print(f"Wrote {BASELINE_PATH.relative_to(REPO_ROOT)} ({len(result['answers'])} answers)")
        return 0
    if not args.path:
        parser.error("a response path (or -) is required")
    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    result = sm.metrics(text, args.question)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 1 if result["decorative_structure_flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
