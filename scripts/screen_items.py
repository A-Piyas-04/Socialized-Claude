"""Screen comprehension items for diagnostic power with the judge model (Track A0.4).

    python scripts/screen_items.py                    # writes evaluation/comprehension/ITEM_BANK_screened.json
    python scripts/screen_items.py --attempts 7

Experiment 5's proxy answered 15/15 items with no explanation at all, so it had no diagnostic
power. This screener asks the judge every multiple-choice item with NO explanation text,
several times with the options shuffled each time. An item the judge answers correctly in a
majority of attempts is non-diagnostic and is dropped from the screened bank.

Separately, the judge classifies each item as recall (choosable by remembering a fact any
explanation states) or application (requires using the mechanism on an unstated situation).
Recall items are flagged, not dropped; items declared transfer/prediction but judged recall are
flagged as mislabelled. Free-text items cannot be answered by option choice and are carried
through unscreened, outside the survival rate.

The source bank is never modified. If few or no items survive, that is the result.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evalschema as es  # noqa: E402
import judgelib as jl  # noqa: E402

OUT_PATH = es.ITEM_BANK_PATH.with_name("ITEM_BANK_screened.json")
CACHE_DIR = es.EVAL_DIR / "comprehension" / "screening_cache"
LETTERS = "ABCDEFGH"
APPLICATION_TYPES = {"transfer", "prediction"}


def answer_prompt(item: dict, order: list[int]) -> str:
    options = "\n".join(f"{LETTERS[pos]}. {item['options'][src]}" for pos, src in enumerate(order))
    return ("Answer this multiple-choice question using only what you already know. You have not been given "
            "any explanation or reading material.\n\n"
            f"{item['stem']}\n{options}\n\n"
            'Reply with JSON only: {"answer": "<letter>"}')


def classify_prompt(topic: dict, item: dict) -> str:
    options = "\n".join(f"- {o}" for o in item["options"])
    return ("You are auditing a comprehension test item for a short explanation of: "
            f"{topic['stimulus_question']}\n\nItem: {item['stem']}\nOptions:\n{options}\n"
            f"Correct option: {item['options'][item['correct_index']]}\n\n"
            "Classify the item. 'recall': the correct option can be chosen by remembering a fact or term that any "
            "explanation of the topic would state directly. 'application': choosing it requires applying the "
            "mechanism to a situation or consequence that such an explanation would not state.\n"
            'Reply with JSON only: {"class": "recall"} or {"class": "application"}')


def parse_answer(text: str, n_options: int) -> int | None:
    value = str(jl.parse_json_object(text).get("answer", "")).strip().upper()[:1]
    position = LETTERS.find(value) if value else -1
    return position if 0 <= position < n_options else None


def screen_item(judge: jl.CachedJudge, topic: dict, item: dict, attempts: int, seed: int) -> dict:
    rng = random.Random(f"{seed}:{item['item_id']}")
    correct = invalid = 0
    for attempt in range(attempts):
        order = list(range(len(item["options"])))
        rng.shuffle(order)
        position = parse_answer(judge.ask(answer_prompt(item, order), temperature=1.0, sample=attempt),
                                len(order))
        if position is None:
            invalid += 1
        elif order[position] == item["correct_index"]:
            correct += 1
    label = str(jl.parse_json_object(judge.ask(classify_prompt(topic, item))).get("class", "")).lower()
    judged = label if label in {"recall", "application"} else "unclassified"
    flags = []
    if judged == "recall":
        flags.append("recall")
    if judged == "recall" and item["type"] in APPLICATION_TYPES:
        flags.append(f"declared {item['type']} but judged recall")
    return {"item_id": item["item_id"], "topic_id": topic["topic_id"], "phase": item["phase"],
            "declared_type": item["type"], "attempts": attempts, "correct_without_text": correct,
            "invalid_answers": invalid, "diagnostic": correct * 2 <= attempts,
            "judged_class": judged, "flags": flags}


def screen_bank(bank: dict, backend: jl.Backend, attempts: int = 5, seed: int = 0,
                cache_dir: Path = CACHE_DIR) -> dict:
    judge = jl.CachedJudge(backend, cache_dir, progress=True)
    results, topics = [], []
    for topic in bank["topics"]:
        kept = []
        for item in topic["items"]:
            if item["format"] != "mc":
                kept.append({**item, "screening": "not screened (free text)"})
                continue
            result = screen_item(judge, topic, item, attempts, seed)
            results.append(result)
            if result["diagnostic"]:
                kept.append({**item, "screening": {k: result[k] for k in
                                                   ("correct_without_text", "attempts", "judged_class", "flags")}})
        topics.append({**{k: v for k, v in topic.items() if k != "items"}, "items": kept})
    survivors = [r for r in results if r["diagnostic"]]
    return {
        "notice": es.JUDGE_NOTICE,
        "source": es.ITEM_BANK_PATH.relative_to(es.REPO_ROOT).as_posix(),
        "source_version": bank.get("version"),
        "screening": {
            "judge_backend": backend.name, "judge_model": backend.model, "attempts_per_item": attempts,
            "rule": "dropped if answered correctly with no explanation in more than half of the attempts "
                    "(options shuffled per attempt, temperature 1.0)",
            "mc_items": len(results), "survivors": len(survivors),
            "survival_rate": len(survivors) / len(results) if results else None,
            "recall_flagged": sorted(r["item_id"] for r in results if "recall" in r["flags"]),
            "mislabelled": sorted(r["item_id"] for r in results if len(r["flags"]) > 1),
            "dropped": sorted(r["item_id"] for r in results if not r["diagnostic"]),
            "judge_calls": judge.calls, "cache_hits": judge.hits,
            "per_item": results,
        },
        "topics": topics,
    }


def report(screened: dict) -> str:
    s = screened["screening"]
    lines = [es.JUDGE_NOTICE, "",
             f"Diagnostic survival: {s['survivors']}/{s['mc_items']} multiple-choice items "
             f"({0 if s['survival_rate'] is None else s['survival_rate']:.0%}) were NOT answerable without an explanation.",
             f"Dropped (answerable with no text): {', '.join(s['dropped']) or 'none'}",
             f"Flagged as recall: {', '.join(s['recall_flagged']) or 'none'}",
             f"Declared transfer/prediction but judged recall: {', '.join(s['mislabelled']) or 'none'}"]
    if s["mc_items"] and s["survivors"] * 4 < s["mc_items"]:
        lines.append("Fewer than a quarter of items survive: the bank as written cannot detect a comprehension "
                     "difference with this judge. This is a result, not a reason to relax the rule.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Screen comprehension items for diagnostic power.")
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-interval", type=float, default=6.0)
    parser.add_argument("--out", default=str(OUT_PATH))
    args = parser.parse_args(argv)
    try:
        backend = jl.backend_from_env(min_interval=args.min_interval)
        screened = screen_bank(es.load_json(es.ITEM_BANK_PATH), backend, args.attempts, args.seed)
    except jl.JudgeUnavailable as exc:
        print(f"screen_items: {exc}. Progress is cached; rerun to resume.", file=sys.stderr)
        return 2
    except jl.JudgeError as exc:
        print(f"screen_items: {exc}", file=sys.stderr)
        return 1
    Path(args.out).write_bytes((json.dumps(screened, indent=2) + "\n").encode("utf-8"))
    print(report(screened))
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
