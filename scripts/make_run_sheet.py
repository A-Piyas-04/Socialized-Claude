"""Create a run folder with a randomized run sheet and the exact message for each response.

    python scripts/make_run_sheet.py --run-id pilot-2026-11-01 --seed 1
    python scripts/make_run_sheet.py --run-id pilot16 --subset pilot16
    python scripts/make_run_sheet.py --run-id var --subset variance12 --samples 2
    python scripts/make_run_sheet.py --run-id ablation --conditions V_core,V_seq,V_mech,V_seq_mech,V_full

Nothing is sent to Claude. The operator pastes each messages/<row_id>.txt into a new chat.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402


def freeze_build(run_dir: Path, batches: set[str], dist: Path | None = None) -> list[str]:
    """Copy the ZIPs and manifests this run needs into <run>/skill_build/, so later skill edits
    cannot change what the run measures. Returns the copied file names."""
    dist = dist or es.REPO_ROOT / "dist"
    names = set()
    for batch in batches:
        if batch in {"skill_off", "skill_on", "variant:full"}:
            names.add("explanation-lab")
        elif batch.startswith("variant:"):
            names.add(f"ablation/explanation-lab--{batch.split(':', 1)[1]}")
    copied = []
    for name in sorted(names):
        for suffix in (".zip", ".manifest.json"):
            source = dist / f"{name}{suffix}"
            if source.is_file():
                target = run_dir / "skill_build" / f"{name}{suffix}"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
                copied.append(f"{name}{suffix}")
    return copied


def batch_rank(batch: str) -> tuple[int, str]:
    return ({"skill_off": 0, "skill_on": 1}.get(batch, 2), batch)


def manifest_sha(batch: str) -> str:
    if batch == "skill_on":
        manifest = es.REPO_ROOT / "dist" / "explanation-lab.manifest.json"
    elif batch.startswith("variant:"):
        variant = batch.split(":", 1)[1]
        name = "explanation-lab" if variant == "full" else f"explanation-lab--{variant}"
        folder = es.REPO_ROOT / "dist" if variant == "full" else es.REPO_ROOT / "dist" / "ablation"
        manifest = folder / f"{name}.manifest.json"
    else:
        return ""
    if not manifest.is_file():
        return ""
    return json.loads(manifest.read_text(encoding="utf-8"))["zip_sha256"]


def select_cases(cases: dict[str, dict], subset: str, explicit: str | None) -> list[str]:
    if explicit:
        ids = [c.strip() for c in explicit.split(",") if c.strip()]
    elif subset == "all":
        ids = list(cases)
    else:
        ids = es.SUBSETS[subset]
    unknown = [c for c in ids if c not in cases]
    if unknown:
        raise SystemExit(f"Unknown case id(s): {', '.join(unknown)}")
    return ids


def build_rows(run_id: str, case_ids: list[str], condition_names: list[str], samples: int,
               seed: int, conditions: dict, multi_turn: frozenset[str] = frozenset()) -> list[dict]:
    rows = []
    for case_id in case_ids:
        for condition in condition_names:
            for sample in range(1, samples + 1):
                batch = conditions["conditions"][condition]["batch"]
                row_id = f"{case_id}__{condition}__s{sample}"
                suffix = ".json" if case_id in multi_turn else ".txt"
                rows.append({
                    "run_id": run_id, "row_id": row_id, "batch": batch, "case_id": case_id,
                    "condition": condition, "sample_index": str(sample),
                    "message_file": f"messages/{row_id}{suffix}", "response_file": f"responses/{row_id}.md",
                    "skill_zip_sha256": manifest_sha(batch),
                    "activation_observed": "na" if batch == "skill_off" else "",
                })
    rng = random.Random(seed)
    batches: dict[str, list[dict]] = {}
    for row in rows:
        batches.setdefault(row["batch"], []).append(row)
    ordered = []
    for batch in sorted(batches, key=batch_rank):
        group = batches[batch]
        rng.shuffle(group)
        ordered.extend(group)
    for index, row in enumerate(ordered, start=1):
        row["order"] = str(index)
    return ordered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an evaluation run folder.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--conditions", default=None, help="comma-separated; default = pilot conditions")
    parser.add_argument("--subset", default="all", choices=["all", *sorted(es.SUBSETS)])
    parser.add_argument("--cases", default=None, help="comma-separated case ids (overrides --subset)")
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--runs-dir", default=str(es.RUNS_DIR))
    parser.add_argument("--force", action="store_true", help="overwrite an existing run sheet")
    args = parser.parse_args(argv)

    cases = es.load_cases()
    conditions = es.load_conditions()
    condition_names = ([c.strip() for c in args.conditions.split(",")] if args.conditions
                       else conditions["default_pilot_conditions"])
    unknown = [c for c in condition_names if c not in conditions["conditions"]]
    if unknown:
        raise SystemExit(f"Unknown condition(s): {', '.join(unknown)}")
    if args.samples < 1:
        raise SystemExit("--samples must be at least 1")

    run_dir = Path(args.runs_dir) / args.run_id
    sheet = run_dir / "run_sheet.csv"
    if sheet.exists() and not args.force:
        raise SystemExit(f"{sheet} exists; use --force to overwrite (responses are never deleted)")

    skill_body = None
    if any(conditions["conditions"][c].get("prefix") == "@SKILL_BODY" for c in condition_names):
        if not es.DIST_ZIP.is_file():
            raise SystemExit("Condition D needs dist/explanation-lab.zip; run scripts/package_skill.py first")
        skill_body = es.skill_body_from_zip()

    case_ids = select_cases(cases, args.subset, args.cases)
    multi_turn = frozenset(c for c in case_ids if cases[c].get("turns"))
    rows = build_rows(args.run_id, case_ids, condition_names, args.samples, args.seed, conditions, multi_turn)

    (run_dir / "messages").mkdir(parents=True, exist_ok=True)
    (run_dir / "responses").mkdir(parents=True, exist_ok=True)
    for row in rows:
        turns = es.build_turns(cases[row["case_id"]], row["condition"], conditions, skill_body)
        es.write_turns(run_dir / row["message_file"], turns)
    es.write_csv(sheet, es.RESULTS_COLUMNS, rows)
    freeze_build(run_dir, {r["batch"] for r in rows})

    batches = sorted({r["batch"] for r in rows}, key=batch_rank)
    print(f"Created {sheet} with {len(rows)} rows ({len(case_ids)} cases x {len(condition_names)} conditions "
          f"x {args.samples} sample(s)). Batches in order: {', '.join(batches)}")
    missing_sha = sorted({r["batch"] for r in rows if r["batch"] != "skill_off" and not r["skill_zip_sha256"]})
    if missing_sha:
        print(f"Note: no manifest found for {', '.join(missing_sha)}; build the ZIP(s) and fill skill_zip_sha256.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
