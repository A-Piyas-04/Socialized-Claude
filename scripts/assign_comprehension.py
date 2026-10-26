"""Counterbalanced (Latin-square) assignment for the human comprehension pilot.

    python scripts/assign_comprehension.py --participants 18 --seed 3 --out evaluation/runs/<run_id>/comprehension/assignment.csv

Each participant reads one explanation per condition, each on a different topic. Condition
orders cycle through all permutations; topic order rotates every full cycle. With a multiple of
6 participants, each condition appears equally often with each topic and in each position.
"""

from __future__ import annotations

import argparse
import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402

DEFAULT_CONDITIONS = ["A_normal", "B_prompt", "C_skill_explicit"]


def assignment(participants: int, topics: list[str], conditions: list[str], seed: int) -> list[dict]:
    if len(topics) != len(conditions):
        raise ValueError("the Latin square needs as many topics as conditions")
    rng = random.Random(seed)
    orders = list(itertools.permutations(conditions))
    rng.shuffle(orders)
    rows = []
    for index in range(participants):
        cycle, slot = divmod(index, len(orders))
        rotation = cycle % len(topics)
        topic_order = topics[rotation:] + topics[:rotation]
        for position, (topic, condition) in enumerate(zip(topic_order, orders[slot]), start=1):
            rows.append({"participant_id": f"P{index + 1:02d}", "position": str(position),
                         "topic_id": topic, "condition": condition})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a counterbalanced comprehension assignment.")
    parser.add_argument("--participants", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--conditions", default=",".join(DEFAULT_CONDITIONS))
    parser.add_argument("--topics", default=None, help="comma-separated topic ids; default = item bank order")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    bank = es.load_item_bank()
    topics = [t.strip() for t in args.topics.split(",")] if args.topics else list(bank)
    unknown = [t for t in topics if t not in bank]
    if unknown:
        raise SystemExit(f"Unknown topic(s): {', '.join(unknown)}")
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    rows = assignment(args.participants, topics, conditions, args.seed)
    es.write_csv(Path(args.out), es.ASSIGNMENT_COLUMNS, rows)
    cycle = len(list(itertools.permutations(conditions)))
    print(f"Wrote {len(rows)} assignments for {args.participants} participants to {args.out}")
    if args.participants % cycle:
        print(f"Note: {args.participants} is not a multiple of {cycle}; counterbalancing is incomplete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
