"""Validity of the evaluation test set, the comprehension item bank, and their documentation."""

from __future__ import annotations

import re
from collections import Counter

import pytest

import evalschema as es
import skilllib

CASES = es.load_cases()
BANK = es.load_item_bank()

REQUIRED_FIELDS = {
    "id": str, "category": str, "domain": str, "difficulty": str, "question": str, "audience": str,
    "skill_expectation": str, "expected_length": str, "expected_properties": list,
    "common_misconceptions": list, "critical_facts": list, "reasoning_gaps": list,
}
CATEGORY_PREFIX = {
    "foundational": "found_", "mechanism": "mech_", "abstract": "abst_", "multi_step_process": "proc_",
    "comparison": "comp_", "follow_up": "follow_", "advanced": "adv_", "concise_factual": "fact_",
    "negative_control": "neg_", "mixed_task": "mixed_", "register": "reg_", "repair": "rep_",
    "decorative_structure": "deco_", "persistence": "pers_", "work_report": "work_",
}
MULTI_TURN_CATEGORIES = {"repair", "persistence"}
CONSTRAINT_KEYS = {"check_turns", "max_words", "no_lists", "no_math"}
DIFFICULTIES = {"beginner", "intermediate", "advanced"}
LENGTHS = {"one_sentence", "short", "medium", "long_ok"}

# Topics of the research archive and of every example inside the skill. Evaluation prompts must
# not reuse them, to limit contamination between design material and the held-out test.
EXCLUDED_TOPIC_KEYWORDS = [
    "write-through", "write-back", "cache", "redis", "b-tree", "three-way handshake", "tcp",
    "vaccin", "compound interest", "simple interest",
    "connection pool", "hash table", "hash-table", "derivative", "fraction", "reciprocal",
    "pressure cooker", "https", "rc<t>", "debounce", "ice float", "leap", "port 443",
]
# Leap years are a test case; make sure the skill examples do not cover them instead.
EXCLUDED_TOPIC_KEYWORDS.remove("leap")


def test_case_count_in_target_range():
    assert 24 <= len(CASES) <= 48


def test_ids_are_unique_and_stable():
    raw = es.load_json(es.TEST_CASES_PATH)["cases"]
    ids = [c["id"] for c in raw]
    assert len(ids) == len(set(ids))
    for case in raw:
        assert re.fullmatch(r"[a-z]+_\d{3}", case["id"])
        assert case["id"].startswith(CATEGORY_PREFIX[case["category"]])


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_case_schema(case_id):
    case = CASES[case_id]
    for name, kind in REQUIRED_FIELDS.items():
        assert isinstance(case.get(name), kind), f"{case_id}.{name}"
    assert case["question"].strip()
    assert case["difficulty"] in DIFFICULTIES
    assert case["skill_expectation"] in es.SKILL_EXPECTATIONS
    assert case["expected_length"] in LENGTHS
    assert "context" in case
    for fact in case["critical_facts"]:
        assert set(fact) == {"id", "fact"}
        assert fact["id"].startswith(f"{case_id}_cf")
        assert fact["fact"].strip()
    fact_ids = [f["id"] for f in case["critical_facts"]]
    assert len(fact_ids) == len(set(fact_ids))
    assert set(case) <= set(REQUIRED_FIELDS) | {"context", "turns", "standing_constraints"}, case_id


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_multi_turn_cases_are_real_conversations(case_id):
    case = CASES[case_id]
    if case["category"] in MULTI_TURN_CATEGORIES:
        assert "turns" in case, f"{case_id}: {case['category']} cases must be real multi-turn conversations"
    if "turns" in case:
        turns = case["turns"]
        assert len(turns) >= 2 and all(isinstance(t, str) and t.strip() for t in turns)
        assert case["question"] == turns[-1], "question repeats the final turn"
        assert case["context"] is None, "earlier turns are sent as turns, never folded into context"
    if case["category"] == "persistence":
        constraints = case["standing_constraints"]
        assert set(constraints) <= CONSTRAINT_KEYS and len(constraints) >= 2
        assert len(case["turns"]) >= 5
        assert all(2 <= t <= len(case["turns"]) for t in constraints["check_turns"])
    else:
        assert "standing_constraints" not in case


def test_register_cases_share_one_question_at_three_levels():
    reg = sorted((c for c in CASES.values() if c["category"] == "register"), key=lambda c: c["id"])
    assert [c["difficulty"] for c in reg] == ["beginner", "intermediate", "advanced"]
    assert len({c["domain"] for c in reg}) == 1


def test_decorative_structure_controls_are_short_prose():
    deco = [c for c in CASES.values() if c["category"] == "decorative_structure"]
    assert len(deco) == 2
    for case in deco:
        assert case["expected_length"] in {"one_sentence", "short"}
        assert any("no heading, bullet" in p for p in case["expected_properties"]), case["id"]


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_eligible_cases_are_fully_specified(case_id):
    case = CASES[case_id]
    if case["skill_expectation"] == "should_apply":
        assert len(case["expected_properties"]) >= 3
        assert len(case["common_misconceptions"]) >= 1
        assert len(case["critical_facts"]) >= 2
        assert len(case["reasoning_gaps"]) >= 1


def test_category_coverage():
    counts = Counter(c["category"] for c in CASES.values())
    assert set(counts) == set(CATEGORY_PREFIX)
    for category, n in counts.items():
        assert n >= 1, category
    assert counts["negative_control"] >= 3
    assert counts["follow_up"] >= 2


def test_follow_up_cases_have_context_and_others_do_not():
    for case in CASES.values():
        if case["category"] == "follow_up":
            assert case["context"] and case["context"].strip()
        else:
            assert case["context"] is None


def test_negative_controls_should_not_apply():
    for case in CASES.values():
        if case["category"] == "negative_control":
            assert case["skill_expectation"] == "should_not_apply"


def test_domain_diversity():
    domains = Counter(c["domain"] for c in CASES.values())
    assert len(domains) >= 8
    software = domains["software_engineering"] + domains["computer_science"]
    assert software / len(CASES) <= 0.4, "evaluation must not be dominated by software topics"


def test_difficulty_mix():
    difficulties = Counter(c["difficulty"] for c in CASES.values())
    assert set(difficulties) == DIFFICULTIES


def test_cases_are_held_out():
    for case in CASES.values():
        text = f"{case['question']} {case['context'] or ''} {' '.join(case.get('turns', []))}".lower()
        for keyword in EXCLUDED_TOPIC_KEYWORDS:
            assert keyword not in text, f"{case['id']} reuses a design or research topic: {keyword}"


def test_skill_examples_do_not_cover_test_topics():
    skill_text = " ".join(p.read_text(encoding="utf-8").lower() for p in skilllib.iter_skill_files(skilllib.SKILL_DIR))
    distinctive = ["dna", "inflation", "compiler", "voltage", "metal spoon", "antibiotic", "salt", "bond price",
                   "uncountabl", "p-value", "recursion", "tapping my card", "neuron", "git merge", "process and a thread",
                   "alternating current", "correlation", "lossy", "negative times", "satellite", "hypothalamus",
                   "postgresql bloat", "learning rate", "cas9", "fahrenheit", "origin of species", "leap year",
                   "fibonacci", "last_n", "sourdough", "tomato", "confidence interval", "fog up", "onion",
                   "maillard", "mri", "grapefruit", "fewer calories", "httpx", "design effect"]
    for keyword in distinctive:
        assert keyword not in skill_text, f"skill examples mention a test topic: {keyword}"


def test_subsets_are_valid():
    for name, ids in es.SUBSETS.items():
        assert len(ids) == len(set(ids)), name
        assert set(ids) <= set(CASES), name
    assert len(es.SUBSETS["pilot16"]) == 16
    categories = {CASES[i]["category"] for i in es.SUBSETS["pilot16"]}
    assert {"negative_control", "follow_up", "advanced", "mechanism"} <= categories
    assert set(es.SUBSETS["variance12"]) <= set(es.SUBSETS["pilot16"])


def test_plan_counts_match_the_data():
    plan = (es.EVAL_DIR / "EVALUATION_PLAN.md").read_text(encoding="utf-8")
    assert f"contains {len(CASES)} held-out cases" in plan
    domains = len({c["domain"] for c in CASES.values()})
    assert f"cover {domains} domains" in plan
    for category, n in Counter(c["category"] for c in CASES.values()).items():
        assert re.search(rf"\| {category} \| {n} \|", plan), f"plan table count for {category}"


# ---------------------------------------------------------------------------
# Comprehension item bank
# ---------------------------------------------------------------------------

def test_item_bank_has_three_topics_for_the_latin_square():
    assert len(BANK) == 3


@pytest.mark.parametrize("topic_id", sorted(BANK))
def test_item_bank_topic_structure(topic_id):
    topic = BANK[topic_id]
    assert topic["stimulus_question"].strip() and topic["audience"].strip()
    items = topic["items"]
    pre = [i for i in items if i["phase"] == "pre"]
    post_mc = [i for i in items if i["phase"] == "post" and i["format"] == "mc"]
    explain = [i for i in items if i["format"] == "free_text"]
    assert len(pre) >= 3 and all(i["format"] == "mc" for i in pre)
    assert len(post_mc) >= 4
    assert len(explain) == 1 and explain[0]["phase"] == "post"
    assert {"transfer", "misconception"} <= {i["type"] for i in post_mc}
    pre_ids = {i["item_id"] for i in pre}
    prefix = {"noise_cancel": "nc_", "fridge": "fr_", "gps": "gps_"}[topic_id]
    for item in items:
        assert item["item_id"].startswith(prefix)
        if item["format"] == "mc":
            assert len(item["options"]) >= 3
            assert 0 <= item["correct_index"] < len(item["options"])
            for index in item.get("misconceptions", {}):
                assert 0 <= int(index) < len(item["options"])
                assert int(index) != item["correct_index"]
        else:
            assert set(item["rubric"]) == {"0", "1", "2"}
        if "parallel_of" in item:
            assert item["parallel_of"] in pre_ids


def test_item_ids_are_unique():
    ids = [i["item_id"] for t in BANK.values() for i in t["items"]]
    assert len(ids) == len(set(ids))


def test_protocol_requires_option_shuffling():
    # Options are stored with the key first for authoring convenience, so the stored order is not
    # neutral. The protocol and the item bank must both require shuffling at presentation.
    protocol = (es.EVAL_DIR / "comprehension" / "PROTOCOL.md").read_text(encoding="utf-8").lower()
    assert "shuffle the answer options" in protocol
    rules = " ".join(es.load_json(es.ITEM_BANK_PATH)["design_rules"]).lower()
    assert "shuffle" in rules


def test_comprehension_topics_are_separate_from_rating_cases():
    questions = " ".join(c["question"].lower() for c in CASES.values())
    for keyword in ("headphone", "fridge", "refrigerator", "gps"):
        assert keyword not in questions
