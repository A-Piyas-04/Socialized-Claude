"""Recompute every number cited in research/EVIDENCE_AUDIT.md from the raw archive.

Reads only files under research-results-2026-10-26/. No network, no model calls.

    python research/recompute_archive_stats.py            # print Markdown tables
    python research/recompute_archive_stats.py --json     # machine-readable output
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "research-results-2026-10-26"
EXP = ARCHIVE / "experiments"

IDENTICAL_SIMILARITY = 0.999

# Phrases the T2 and T3 instruction templates explicitly asked the rewriter to produce
# (see strategies.py in the ExplanationLab repository). Counted to show instruction artifacts.
ARTIFACT_PATTERNS = {
    "signposting": r"\b(Now that|With the .{0,40} (established|defined|in place)|Building (up)?on)\b",
    "source_meta": r"[Tt]he source (does not|doesn't|text)",
    "causal_connectives": r"\b(because|so that|which means|as a result|therefore|causes?)\b",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def transform_records() -> list[dict]:
    paths = sorted((EXP / "experiment-3" / "transforms").glob("*/*.json"))
    paths += sorted((EXP / "experiment-4" / "cross").glob("*.json"))
    records = []
    for path in paths:
        raw = load_json(path)
        change = raw["changes"][0]
        stats = change["stats"]
        rewriter = next(s["model_id"] for s in raw["stages"] if s["stage"] == "C")
        warnings = raw["fidelity"]["warnings"]
        records.append({
            "file": path.name,
            "experiment": "E4" if path.name.startswith("cross-") else "E3",
            "treatment": change["treatment"],
            "treatment_name": change["name"],
            "rewriter": rewriter,
            "verdict": raw["fidelity"]["verdict"],
            "similarity": stats["word_similarity"],
            "word_delta": stats["word_delta"],
            "headings_added": stats["headings_added"],
            "list_items_added": stats["list_items_added"],
            "table_rows_added": stats["table_rows_added"],
            "warning_types": [w.get("type") for w in warnings],
            "llm_warnings": [w for w in warnings if w.get("detector") == "llm_reviewer"],
            "numeric_drift": raw["fidelity"].get("numeric_drift") or [],
            "text": raw["text"],
        })
    return records


def summarize_group(group: list[dict]) -> dict:
    verdicts = Counter(r["verdict"] for r in group)
    identical = [r for r in group if r["similarity"] >= IDENTICAL_SIMILARITY]
    clean = [r for r in group if r["verdict"] == "clean"]
    clean_changed = [r for r in clean if r["similarity"] < IDENTICAL_SIMILARITY]
    serious = [r for r in group if r["verdict"] == "serious_concerns"]
    serious_numeric_only = [
        r for r in serious
        if not r["llm_warnings"] and set(r["warning_types"]) <= {"numeric_change", "boundary_violation",
                                                                   "unjustified_certainty", "omitted_caveat"}
        and "numeric_change" in r["warning_types"]
    ]
    warning_counts = Counter(t for r in group for t in r["warning_types"])
    return {
        "runs": len(group),
        "clean": verdicts["clean"],
        "warnings": verdicts["warnings"],
        "serious_concerns": verdicts["serious_concerns"],
        "identical_to_source": len(identical),
        "clean_and_identical": len([r for r in clean if r in identical]),
        "clean_and_changed": len(clean_changed),
        "serious_without_llm_reviewer_finding": len(serious_numeric_only),
        "llm_reviewer_findings": sum(len(r["llm_warnings"]) for r in group),
        "median_similarity": round(statistics.median(r["similarity"] for r in group), 3),
        "median_word_delta": statistics.median(r["word_delta"] for r in group),
        "warning_type_counts": dict(sorted(warning_counts.items())),
    }


def artifact_counts(records: list[dict]) -> dict:
    dataset = load_json(ARCHIVE / "inputs" / "input-dataset.json")
    baselines = [a["text"] for a in dataset["imported_answers"] if "base" in a["label"].lower()]
    out: dict[str, dict] = {"source_baselines (n=%d)" % len(baselines): {}}
    for name, pattern in ARTIFACT_PATTERNS.items():
        out["source_baselines (n=%d)" % len(baselines)][name] = sum(len(re.findall(pattern, t)) for t in baselines)
    groups = defaultdict(list)
    for r in records:
        groups[f"{r['experiment']}-{r['treatment']}-{r['rewriter']}"].append(r["text"])
    for key in sorted(groups):
        out[f"{key} (n={len(groups[key])})"] = {
            name: sum(len(re.findall(p, t)) for t in groups[key]) for name, p in ARTIFACT_PATTERNS.items()
        }
    return out


def csv_consistency(records: list[dict]) -> list[str]:
    """Cross-check the published CSV verdicts against the raw JSON verdicts."""
    issues = []
    by_file = defaultdict(list)
    for r in records:
        by_file[r["file"]].append(r)
    for csv_path in (EXP / "experiment-3" / "experiment-3-results.csv", EXP / "experiment-4" / "experiment-4-results.csv"):
        for row in load_csv(csv_path):
            raw = by_file.get(row["raw_file"])
            if not raw:
                issues.append(f"{csv_path.name}: raw file {row['raw_file']} not found")
                continue
            if raw[0]["verdict"] != row["fidelity_verdict"]:
                issues.append(f"{csv_path.name}: verdict mismatch for {row['raw_file']}")
    return issues


def experiment5() -> dict:
    rows = load_csv(EXP / "experiment-5" / "experiment-5-results.csv")
    proxies = {p.name: load_json(p) for p in sorted((EXP / "experiment-5" / "proxy").glob("proxy-*.json"))}
    quote_misses = []
    for name, proxy in proxies.items():
        for cond in proxy["conditions"]:
            for item in cond["items"]:
                if item["correct"] and not item["quote_found"]:
                    quote_misses.append(f"{name} / {cond['label']} / {item['dimension']}")
    return {
        "conditions": len(rows),
        "topics": len({r["topic"] for r in rows}),
        "items_total": sum(p["item_count"] for p in proxies.values()),
        "no_explanation_correct_total": sum(p["baseline_correct_count"] for p in proxies.values()),
        "diagnostic_items_total": sum(p["diagnostic_item_count"] for p in proxies.values()),
        "correct_but_quote_not_found": quote_misses,
        "proxy_models": sorted({p["model_id"] for p in proxies.values()}),
    }


def inputs() -> dict:
    dataset = load_json(ARCHIVE / "inputs" / "input-dataset.json")
    labels = Counter((a["provider"], a["label"].lower()) for a in dataset["imported_answers"])
    words = defaultdict(list)
    for a in dataset["imported_answers"]:
        style = a["label"].lower().split("-")[-1].strip()
        words[style].append(len(a["text"].split()))
    return {
        "questions": [q["text"] for q in dataset["questions"]],
        "imported_answers": len(dataset["imported_answers"]),
        "answers_by_provider_and_label": {f"{p} / {l}": n for (p, l), n in sorted(labels.items())},
        "median_words_by_prompt_style": {k: statistics.median(v) for k, v in sorted(words.items())},
        "models": sorted({a["model_id"] for a in dataset["imported_answers"]}),
    }


def build() -> dict:
    records = transform_records()
    groups = defaultdict(list)
    for r in records:
        groups[(r["experiment"], r["rewriter"], r["treatment"])].append(r)
    e4_unique = [r for r in records if r["experiment"] == "E4"]
    return {
        "treatment_names": dict(sorted({r["treatment"]: r["treatment_name"] for r in records}.items())),
        "groups": {f"{e} | {w} | {t}": summarize_group(g) for (e, w, t), g in sorted(groups.items())},
        "experiment4_new_rewrites": len(e4_unique),
        "experiment4_reused_experiment3_rows": 10,
        "llm_reviewer_findings": [
            {"file": r["file"], "type": w.get("type"), "severity": w.get("severity"), "detail": w.get("detail")}
            for r in records for w in r["llm_warnings"]
        ],
        "artifact_pattern_counts": artifact_counts(records),
        "csv_consistency_issues": csv_consistency(records),
        "experiment5": experiment5(),
        "inputs": inputs(),
    }


def print_markdown(data: dict) -> None:
    print("## Treatment names (from raw transform records)\n")
    for k, v in data["treatment_names"].items():
        print(f"- {k}: {v}")
    print("\n## Fidelity screen by group\n")
    cols = ["runs", "clean", "warnings", "serious_concerns", "identical_to_source", "clean_and_identical",
            "clean_and_changed", "serious_without_llm_reviewer_finding", "median_similarity", "median_word_delta"]
    print("| Group | " + " | ".join(cols) + " |")
    print("|---|" + "---:|" * len(cols))
    for key, g in data["groups"].items():
        print(f"| {key} | " + " | ".join(str(g[c]) for c in cols) + " |")
    print("\n## Warning types by group\n")
    for key, g in data["groups"].items():
        print(f"- {key}: {g['warning_type_counts']}")
    print("\n## LLM-reviewer findings (the only semantic check in the pipeline)\n")
    for f in data["llm_reviewer_findings"]:
        print(f"- `{f['file']}` [{f['type']}, {f['severity']}]: {f['detail']}")
    print("\n## Instruction-artifact phrase counts\n")
    names = list(ARTIFACT_PATTERNS)
    print("| Group | " + " | ".join(names) + " |")
    print("|---|" + "---:|" * len(names))
    for key, counts in data["artifact_pattern_counts"].items():
        print(f"| {key} | " + " | ".join(str(counts[n]) for n in names) + " |")
    print("\n## CSV vs raw JSON consistency\n")
    print("- " + ("; ".join(data["csv_consistency_issues"]) if data["csv_consistency_issues"] else "No mismatches."))
    print("\n## Experiment 5\n")
    for k, v in data["experiment5"].items():
        print(f"- {k}: {v}")
    print("\n## Inputs\n")
    for k, v in data["inputs"].items():
        print(f"- {k}: {v}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    args = parser.parse_args()
    if not ARCHIVE.exists():
        print(f"Archive not found: {ARCHIVE}", file=sys.stderr)
        return 1
    data = build()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
