"""Build a blinded rating packet from a completed run.

    python scripts/prepare_blind_packet.py evaluation/runs/<run_id> --raters r1,r2 --seed 7

Creates <run_dir>/blind/ with one Markdown file per case (responses shuffled under random
blind IDs), a pre-filled ratings CSV per rater, the blind key (keep it from raters), and a
list of responses containing condition-revealing text.
"""

from __future__ import annotations

import argparse
import random
import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402

REVEALING = re.compile(
    r"(?i)explanation[- ]lab|socialized|SKILL\.md|\b(this|the) skill\b|\btreatment\s*T\d|\bT[1-6]\b")


def blind_ids(n: int, rng: random.Random) -> list[str]:
    alphabet = string.ascii_uppercase + string.digits
    seen: set[str] = set()
    while len(seen) < n:
        seen.add("".join(rng.choice(alphabet) for _ in range(6)))
    ids = sorted(seen)
    rng.shuffle(ids)
    return ids


def case_header(case: dict) -> list[str]:
    lines = [f"# Case {case['id']}", "", f"**Audience:** {case['audience']}", ""]
    if case.get("context"):
        lines += ["**Context the user provided:**", "", f"> {case['context']}", ""]
    lines += ["**Question:**", "", *[f"> {line}" if line else ">" for line in case["question"].split("\n")], ""]
    lines += ["## Reference for raters", "", "Expected properties:", ""]
    lines += [f"- {p}" for p in case["expected_properties"]] or ["- (none)"]
    lines += ["", "Critical facts:", ""]
    lines += [f"- `{f['id']}`: {f['fact']}" for f in case["critical_facts"]] or ["- (none)"]
    lines += ["", "Common misconceptions:", ""]
    lines += [f"- {m}" for m in case["common_misconceptions"]] or ["- (none)"]
    lines += ["", f"Expected length: {case['expected_length']}", ""]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a blinded rating packet.")
    parser.add_argument("run_dir")
    parser.add_argument("--raters", default="r1,r2")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--allow-missing", action="store_true", help="skip rows without a response file")
    parser.add_argument("--force", action="store_true", help="overwrite an existing blind folder")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    sheet = run_dir / "run_sheet.csv"
    if not sheet.is_file():
        raise SystemExit(f"run sheet not found: {sheet}")
    blind_dir = run_dir / "blind"
    if (blind_dir / "blind_key.csv").exists() and not args.force:
        raise SystemExit(f"{blind_dir} already has a blind key; use --force to rebuild (ratings would no longer match)")

    cases = es.load_cases()
    _, rows = es.read_csv(sheet)
    available, missing = [], []
    for row in rows:
        path = run_dir / row["response_file"]
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            available.append(row)
        else:
            missing.append(row["row_id"])
    if missing and not args.allow_missing:
        raise SystemExit(f"{len(missing)} response file(s) missing or empty, e.g. {missing[:3]}. "
                         "Fill them or pass --allow-missing.")

    rng = random.Random(args.seed)
    ids = blind_ids(len(available), rng)
    key_rows, warnings = [], []
    by_case: dict[str, list[tuple[str, str]]] = {}
    for blind_id, row in zip(ids, available):
        text = (run_dir / row["response_file"]).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
        key_rows.append({"blind_id": blind_id, "row_id": row["row_id"], "case_id": row["case_id"],
                         "condition": row["condition"], "sample_index": row["sample_index"]})
        by_case.setdefault(row["case_id"], []).append((blind_id, text))
        hits = sorted({m.group(0) for m in REVEALING.finditer(text)})
        if hits:
            warnings.append(f"{blind_id} (case {row['case_id']}): mentions {', '.join(hits)}")

    packet_dir = blind_dir / "packet"
    packet_dir.mkdir(parents=True, exist_ok=True)
    rating_order = []
    for case_id in sorted(by_case):
        responses = by_case[case_id]
        rng.shuffle(responses)
        lines = case_header(cases[case_id])
        for blind_id, text in responses:
            lines += ["---", "", f"## Response {blind_id}", "", text, ""]
            rating_order.append((case_id, blind_id))
        (packet_dir / f"{case_id}.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    es.write_csv(blind_dir / "blind_key.csv", es.BLIND_KEY_COLUMNS, key_rows)
    raters = [r.strip() for r in args.raters.split(",") if r.strip()]
    for rater in raters:
        es.write_csv(blind_dir / "ratings" / f"ratings_{rater}.csv", es.RATINGS_COLUMNS,
                     [{"rater_id": rater, "blind_id": b, "case_id": c} for c, b in rating_order])
    (blind_dir / "blinding_warnings.txt").write_bytes(
        ("\n".join(warnings) + "\n" if warnings else "No condition-revealing text found.\n").encode("utf-8"))

    print(f"Packet: {len(available)} responses across {len(by_case)} cases -> {packet_dir}")
    print(f"Ratings sheets: {', '.join(raters)}. Blind key: {blind_dir / 'blind_key.csv'} (keep from raters)")
    if missing:
        print(f"Skipped {len(missing)} row(s) without responses.")
    if warnings:
        print(f"{len(warnings)} response(s) contain condition-revealing text; see blinding_warnings.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
