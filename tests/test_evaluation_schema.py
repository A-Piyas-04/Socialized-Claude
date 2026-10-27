"""Schema consistency and end-to-end behaviour of the evaluation tools.

All run data here is synthetic and generated inside temporary directories. It exists only to
exercise the scripts and is never written into the repository.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

import assign_comprehension
import evalschema as es
import make_run_sheet
import prepare_blind_packet
import skilllib
import summarize_results

CONDITIONS = es.load_conditions()
CASES = es.load_cases()
PILOT = ["A_normal", "B_prompt", "C_skill", "C_skill_explicit"]
PREFERENCE = {"C_skill_explicit": 1, "C_skill": 2, "B_prompt": 3, "A_normal": 4}


# ---------------------------------------------------------------------------
# Templates and documents agree with the schema
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("template, columns", [
    (es.EVAL_DIR / "RESULTS_TEMPLATE.csv", es.RESULTS_COLUMNS),
    (es.EVAL_DIR / "RATINGS_TEMPLATE.csv", es.RATINGS_COLUMNS),
    (es.EVAL_DIR / "comprehension" / "RESPONSES_TEMPLATE.csv", es.COMPREHENSION_RESPONSE_COLUMNS),
    (es.EVAL_DIR / "comprehension" / "EXPOSURE_TEMPLATE.csv", es.EXPOSURE_COLUMNS),
])
def test_templates_match_schema(template, columns):
    header, rows = es.read_csv(template)
    assert header == columns
    assert rows == [], "templates must not contain example data"


def test_rubric_documents_every_dimension_and_code():
    rubric = (es.EVAL_DIR / "RUBRIC.md").read_text(encoding="utf-8")
    for dim in es.DIMENSIONS:
        assert f"`{dim}`" in rubric
    for code in es.ADHERENCE_CODES:
        assert f"`{code}`" in rubric
    for dim in es.DIMENSIONS_ALLOWING_NA:
        section = rubric.split(f"`{dim}`", 1)[1].split("### ", 1)[0]
        assert "NA" in section, f"rubric must say when {dim} allows NA"


def fenced_block_after(text: str, heading: str) -> str:
    section = text.split(heading, 1)[1]
    match = re.search(r"```\n(.*?)\n```", section, re.DOTALL)
    assert match, heading
    return match.group(1)


def test_baseline_markdown_matches_conditions_json():
    doc = (es.EVAL_DIR / "BASELINE_INSTRUCTIONS.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    b = fenced_block_after(doc, "## Condition B — exact message")
    assert b == CONDITIONS["conditions"]["B_prompt"]["prefix"] + "\n\n{question}"
    explicit = fenced_block_after(doc, "## Condition C_skill_explicit — exact message")
    assert explicit == CONDITIONS["conditions"]["C_skill_explicit"]["prefix"] + "\n\n{question}"
    assert fenced_block_after(doc, "## Condition A — exact message") == "{question}"


def test_conditions_are_consistent():
    names = set(CONDITIONS["conditions"])
    assert set(CONDITIONS["default_pilot_conditions"]) <= names
    for x, y in CONDITIONS["comparisons"]:
        assert x in names and y in names
    for name, spec in CONDITIONS["conditions"].items():
        batch = spec["batch"]
        assert batch in {"skill_off", "skill_on"} or batch.split(":", 1)[1] in skilllib.VARIANTS, name
    assert all(CONDITIONS["conditions"][c]["prefix"] == CONDITIONS["conditions"]["C_skill_explicit"]["prefix"]
               for c in names if c.startswith("V_")), "ablation must hold the invocation line constant"


def test_baseline_b_does_not_mention_the_skill():
    prefix = CONDITIONS["conditions"]["B_prompt"]["prefix"].lower()
    assert "skill" not in prefix and "socialized" not in prefix and "explanation-lab" not in prefix


# ---------------------------------------------------------------------------
# Run sheet
# ---------------------------------------------------------------------------

def make_run(tmp_path: Path, case_ids: list[str], conditions: list[str] = PILOT, samples: int = 1,
             seed: int = 1, run_id: str = "synthetic") -> Path:
    args = ["--run-id", run_id, "--cases", ",".join(case_ids), "--conditions", ",".join(conditions),
            "--samples", str(samples), "--seed", str(seed), "--runs-dir", str(tmp_path)]
    assert make_run_sheet.main(args) == 0
    return tmp_path / run_id


def test_run_sheet_rows_batches_and_messages(tmp_path):
    run = make_run(tmp_path, ["mech_001", "follow_002", "neg_001"])
    header, rows = es.read_csv(run / "run_sheet.csv")
    assert header == es.RESULTS_COLUMNS
    assert len(rows) == 3 * 4
    orders = {r["row_id"]: int(r["order"]) for r in rows}
    off = [orders[r["row_id"]] for r in rows if r["batch"] == "skill_off"]
    on = [orders[r["row_id"]] for r in rows if r["batch"] == "skill_on"]
    assert max(off) < min(on), "all skill-off rows come before the skill toggle"
    for r in rows:
        assert (r["activation_observed"] == "na") == (r["batch"] == "skill_off")
        message = (run / r["message_file"]).read_text(encoding="utf-8")
        case = CASES[r["case_id"]]
        assert message.rstrip().endswith(case["question"])
        if case["context"]:
            assert case["context"] in message
        if r["condition"] == "B_prompt":
            assert message.startswith(CONDITIONS["conditions"]["B_prompt"]["prefix"])
        if r["condition"] == "C_skill_explicit":
            assert message.startswith("Use the socialized skill for this.")
        if r["condition"] in {"A_normal", "C_skill"} and not case["context"]:
            assert message == case["question"] + "\n"


def test_run_sheet_is_deterministic_and_protected(tmp_path):
    a = make_run(tmp_path / "a", ["mech_001", "abst_002"], seed=5)
    b = make_run(tmp_path / "b", ["mech_001", "abst_002"], seed=5)
    assert es.read_csv(a / "run_sheet.csv")[1] == es.read_csv(b / "run_sheet.csv")[1]
    with pytest.raises(SystemExit):
        make_run(tmp_path / "a", ["mech_001"], seed=5)


def test_condition_d_pastes_the_packaged_skill_body(tmp_path):
    run = make_run(tmp_path, ["mech_001"], conditions=["D_skill_text"])
    _, rows = es.read_csv(run / "run_sheet.csv")
    message = (run / rows[0]["message_file"]).read_text(encoding="utf-8")
    assert message.startswith("# Socialized-Claude")
    assert "name: socialized" not in message
    assert "op:" not in message
    assert "\n---\n" in message and message.rstrip().endswith(CASES["mech_001"]["question"])


def test_unknown_case_or_condition_is_rejected(tmp_path):
    with pytest.raises(SystemExit):
        make_run(tmp_path, ["no_such_case"])
    with pytest.raises(SystemExit):
        make_run(tmp_path, ["mech_001"], conditions=["Z_unknown"])


# ---------------------------------------------------------------------------
# Synthetic end-to-end run
# ---------------------------------------------------------------------------

def fill_run(run: Path, words: dict[str, int], activation: str = "yes", mention_skill: str | None = None) -> None:
    header, rows = es.read_csv(run / "run_sheet.csv")
    for r in rows:
        n = words.get(r["condition"], 20)
        text = " ".join(["synthetic"] * (n - 1) + [f"item{r['order']}"])
        if mention_skill and r["condition"] == mention_skill:
            text += " socialized"
        (run / r["response_file"]).write_text(text + "\n", encoding="utf-8")
        r.update({"date": "2026-11-01", "surface": "test", "model_label": "test-model", "thinking_setting": "off"})
        if r["batch"] != "skill_off":
            r["activation_observed"] = activation
    es.write_csv(run / "run_sheet.csv", header, rows)


def fill_ratings(run: Path, scores: dict[str, int], hijack: set[str] = frozenset(), blank: tuple | None = None,
                 overrides: dict[tuple[str, str], str] | None = None) -> None:
    _, key = es.read_csv(run / "blind" / "blind_key.csv")
    condition = {k["blind_id"]: k["condition"] for k in key}
    case_of = {k["blind_id"]: k["case_id"] for k in key}
    for path in sorted((run / "blind" / "ratings").glob("*.csv")):
        header, rows = es.read_csv(path)
        for r in rows:
            cond = condition[r["blind_id"]]
            for dim in es.DIMENSIONS:
                r[dim] = str(scores.get(cond, 3))
            r["example_effectiveness"] = "NA"
            for column in es.COUNT_COLUMNS:
                r[column] = "0"
            r["adherence_violations"] = "HIJACK" if (cond in hijack and
                                                     CASES[case_of[r["blind_id"]]]["skill_expectation"] == "should_not_apply") else ""
            r["rank_within_case"] = str(PREFERENCE.get(cond, 5))
            if blank and (path.stem, r["blind_id"]) == blank:
                r["accuracy"] = ""
            for (column, bid), value in (overrides or {}).items():
                if bid == r["blind_id"] and path.stem == "ratings_r1":
                    r[column] = value
        es.write_csv(path, header, rows)


@pytest.fixture
def rated_run(tmp_path):
    cases = ["mech_001", "mech_003", "abst_002", "comp_002", "neg_001", "fact_001"]
    run = make_run(tmp_path, cases)
    fill_run(run, words={"A_normal": 20, "B_prompt": 22, "C_skill": 22, "C_skill_explicit": 22})
    assert prepare_blind_packet.main([str(run), "--raters", "r1,r2", "--seed", "3"]) == 0
    fill_ratings(run, scores={"C_skill_explicit": 4, "C_skill": 4, "B_prompt": 3, "A_normal": 2})
    return run


def test_blind_packet_contents(rated_run):
    blind = rated_run / "blind"
    _, key = es.read_csv(blind / "blind_key.csv")
    assert len(key) == 6 * 4
    assert len({k["blind_id"] for k in key}) == len(key)
    packets = sorted((blind / "packet").glob("*.md"))
    assert len(packets) == 6
    combined = "\n".join(p.read_text(encoding="utf-8") for p in packets)
    for k in key:
        assert combined.count(f"## Response {k['blind_id']}") == 1
    for condition in PILOT:
        assert condition not in combined, "packet must not reveal conditions"
    for rater in ("r1", "r2"):
        _, rows = es.read_csv(blind / "ratings" / f"ratings_{rater}.csv")
        assert {r["blind_id"] for r in rows} == {k["blind_id"] for k in key}


def test_blind_packet_refuses_to_overwrite(rated_run):
    with pytest.raises(SystemExit):
        prepare_blind_packet.main([str(rated_run)])


def test_blind_packet_requires_all_responses(tmp_path):
    run = make_run(tmp_path, ["mech_001"])
    with pytest.raises(SystemExit):
        prepare_blind_packet.main([str(run)])
    assert prepare_blind_packet.main([str(run), "--allow-missing"]) == 0


def test_blinding_warnings_flag_skill_mentions(tmp_path):
    run = make_run(tmp_path, ["mech_001"])
    fill_run(run, words={}, mention_skill="C_skill")
    prepare_blind_packet.main([str(run), "--seed", "1"])
    warnings = (run / "blind" / "blinding_warnings.txt").read_text(encoding="utf-8")
    assert "socialized" in warnings and warnings.count("\n") == 1


def test_summary_paired_differences_are_exact(rated_run):
    summary, issues = summarize_results.summarize(rated_run, n_boot=500, seed=1)
    assert issues.errors == []
    comp = summary["comparisons"]["C_skill_explicit vs B_prompt"]
    for dim in ("mechanistic_clarity", "prerequisite_sequencing", "accuracy"):
        assert comp[dim]["n"] == 6
        assert comp[dim]["mean_diff"] == pytest.approx(1.0)
        assert comp[dim]["ci95"] == [pytest.approx(1.0), pytest.approx(1.0)]
        assert (comp[dim]["wins"], comp[dim]["ties"], comp[dim]["losses"]) == (6, 0, 0)
    assert comp["example_effectiveness"]["n"] == 0, "NA scores must not be treated as numbers"
    assert summary["comparisons"]["C_skill_explicit vs C_skill"]["accuracy"]["mean_diff"] == pytest.approx(0.0)
    assert summary["rank_wins_should_apply"]["C_skill_explicit vs B_prompt"] == {"n": 4, "wins": 4, "ties": 0, "losses": 0}
    assert summary["agreement"]["accuracy"]["exact"] == pytest.approx(1.0)


def test_criteria_are_gated_on_sample_size_by_default(rated_run):
    summary, _ = summarize_results.summarize(rated_run, n_boot=100)
    status = {c["id"]: c for c in summary["criteria"]}
    assert status["S6"]["status"] == "INSUFFICIENT_DATA"
    assert "at least 10 needed" in status["S6"]["detail"]
    assert status["S2"]["status"] == "INSUFFICIENT_DATA"


def test_summary_criteria(rated_run):
    summary, _ = summarize_results.summarize(rated_run, n_boot=200, min_cases=1)
    status = {c["id"]: c["status"] for c in summary["criteria"]}
    assert status["S1"] == "NOT_EVALUATED"
    assert status["S2"] == "MET"
    assert status["S3"] == "MET"
    assert status["S4"] == "MET"
    assert status["S5"] == "MET"
    assert status["S6"] == "MET"
    assert status["S7"] == "NOT_EVALUATED"
    ratio = summary["words"]["ratios"]["C_skill_explicit / A_normal"]
    assert ratio["should_apply"] == pytest.approx(1.1)


def test_hijack_and_verbosity_fail_criteria(tmp_path):
    run = make_run(tmp_path, ["mech_001", "neg_001", "neg_002", "fact_001"])
    fill_run(run, words={"A_normal": 20, "C_skill_explicit": 40, "C_skill": 40, "B_prompt": 20}, activation="no")
    prepare_blind_packet.main([str(run), "--raters", "r1"])
    fill_ratings(run, scores={}, hijack={"C_skill", "C_skill_explicit"})
    summary, _ = summarize_results.summarize(run, n_boot=100, min_cases=1)
    status = {c["id"]: c["status"] for c in summary["criteria"]}
    assert status["S2"] == "NOT_MET"
    assert status["S3"] == "NOT_MET"
    assert status["S5"] == "NOT_MET"
    # Equal dimension scores, but the synthetic ranks still prefer C, so S6 is met via the rank path.
    s6 = next(c for c in summary["criteria"] if c["id"] == "S6")
    assert s6["status"] == "MET" and "ranked above B in 1/1" in s6["detail"]
    assert summary["comparisons"]["C_skill_explicit vs B_prompt"]["mechanistic_clarity"]["mean_diff"] == 0


def test_missing_and_invalid_ratings_are_reported_not_fatal(rated_run, tmp_path):
    _, key = es.read_csv(rated_run / "blind" / "blind_key.csv")
    first, second = key[0]["blind_id"], key[1]["blind_id"]
    fill_ratings(rated_run, scores={"C_skill_explicit": 4}, blank=("ratings_r2", first),
                 overrides={("mechanistic_clarity", second): "7", ("directness", second): "great",
                            ("adherence_violations", second): "SIGNPOST;NOTACODE",
                            ("critical_facts_present", second): "made_up_cf9",
                            ("accuracy", first): "NA"})
    summary, issues = summarize_results.summarize(rated_run, n_boot=100)
    text = "\n".join(issues.errors)
    assert "'accuracy' is empty" in text
    assert "outside 1-5" in text
    assert "not an integer" in text
    assert "NOTACODE" in text
    assert "made_up_cf9" in text
    assert "does not allow NA" in text
    assert summary["dimension_means"], "summary is still produced"
    assert summarize_results.main([str(rated_run), "--check-only"]) == 1
    assert summarize_results.main([str(rated_run), "--bootstrap", "50"]) == 0
    assert (rated_run / "summary.md").read_text(encoding="utf-8").startswith("# Evaluation summary")


def test_missing_responses_and_columns_are_reported(tmp_path):
    run = make_run(tmp_path, ["mech_001"])
    summary, issues = summarize_results.summarize(run, n_boot=10)
    assert summary["responses_present"] == 0
    assert sum("response file missing" in e for e in issues.errors) == 4
    assert summary["criteria"][0]["id"] == "S1"


def test_summary_without_run_sheet(tmp_path):
    summary, issues = summarize_results.summarize(tmp_path / "nothing", n_boot=10)
    assert any("run sheet not found" in e for e in issues.errors)
    assert summary["rows"] == 0


def test_bootstrap_is_deterministic_and_handles_small_n():
    values = [0.0, 1.0, 2.0, 3.0, 4.0]
    first = summarize_results.bootstrap_ci(values, 1000, 4)
    assert first == summarize_results.bootstrap_ci(values, 1000, 4)
    assert first[0] <= 2.0 <= first[1]
    assert summarize_results.bootstrap_ci([1.0], 1000, 4) is None
    assert summarize_results.bootstrap_ci([], 1000, 4) is None


# ---------------------------------------------------------------------------
# Comprehension
# ---------------------------------------------------------------------------

def test_latin_square_is_balanced(tmp_path):
    out = tmp_path / "assignment.csv"
    assert assign_comprehension.main(["--participants", "6", "--seed", "2", "--out", str(out)]) == 0
    header, rows = es.read_csv(out)
    assert header == es.ASSIGNMENT_COLUMNS
    by_participant = {}
    for r in rows:
        by_participant.setdefault(r["participant_id"], []).append(r)
    assert len(by_participant) == 6
    for group in by_participant.values():
        assert len({r["condition"] for r in group}) == 3
        assert len({r["topic_id"] for r in group}) == 3
    pairs = Counter((r["topic_id"], r["condition"]) for r in rows)
    assert set(pairs.values()) == {2}
    positions = Counter((r["position"], r["condition"]) for r in rows)
    assert set(positions.values()) == {2}


def write_comprehension(run: Path, assignment: list[dict], ceiling_for: str | None = None,
                        inattentive: str | None = None, extra_rows: list[dict] | None = None) -> None:
    bank = es.load_item_bank()
    rows, exposure = [], []
    for a in assignment:
        cond, topic = a["condition"], a["topic_id"]
        for item in bank[topic]["items"]:
            if item["phase"] == "pre":
                score = 1 if a["participant_id"] == ceiling_for else 0
            elif item["format"] == "free_text":
                score = {"C_skill_explicit": 2, "B_prompt": 1}.get(cond, 0)
            elif cond == "C_skill_explicit":
                score = 1
            elif cond == "B_prompt":
                score = 1 if item["type"] == "mechanism" else 0
            else:
                score = 0
            rows.append({"participant_id": a["participant_id"], "topic_id": topic, "condition": cond,
                         "position": a["position"], "phase": item["phase"], "item_id": item["item_id"],
                         "response": "synthetic", "score": str(score), "grader_id": "g1"})
        exposure.append({"participant_id": a["participant_id"], "topic_id": topic, "condition": cond,
                         "position": a["position"], "familiarity": "1", "reading_seconds": "90",
                         "stimulus_words": "300", "confidence_after": "3", "perceived_clarity": "4",
                         "attention_flag": "yes" if (a["participant_id"], topic) == (inattentive, topic) and a["position"] == "1" else "no"})
    rows += extra_rows or []
    es.write_csv(run / "comprehension" / "responses.csv", es.COMPREHENSION_RESPONSE_COLUMNS, rows)
    es.write_csv(run / "comprehension" / "exposure.csv", es.EXPOSURE_COLUMNS, exposure)


def test_comprehension_contrasts_and_exclusions(rated_run):
    out = rated_run / "comprehension" / "assignment.csv"
    assign_comprehension.main(["--participants", "6", "--seed", "2", "--out", str(out)])
    _, assignment = es.read_csv(out)
    write_comprehension(rated_run, assignment, ceiling_for="P01", inattentive="P02")
    summary, issues = summarize_results.summarize(rated_run, n_boot=200, min_cases=1, min_participants=5)
    assert not [e for e in issues.errors if "comprehension" in e]
    comp = summary["comprehension"]
    assert comp["participants"] == 6
    assert comp["excluded_attention"] == 1
    assert comp["ceiling_excluded_from_gain"] == 3
    cb = comp["contrasts"]["C_skill_explicit - B_prompt"]["transfer_misconception"]
    assert cb["n"] >= 5 and cb["mean_diff"] > 0 and cb["losses"] == 0
    explain = comp["contrasts"]["C_skill_explicit - A_normal"]["explain"]
    assert explain["mean_diff"] == pytest.approx(2.0)
    status = {c["id"]: c["status"] for c in summary["criteria"]}
    assert status["S7"] == "MET"


def test_comprehension_validation_errors(rated_run):
    out = rated_run / "comprehension" / "assignment.csv"
    assign_comprehension.main(["--participants", "6", "--out", str(out)])
    _, assignment = es.read_csv(out)
    bad = [
        {"participant_id": "P01", "topic_id": "gps", "condition": "A_normal", "position": "1", "phase": "post",
         "item_id": "no_such_item", "score": "1"},
        {"participant_id": "P01", "topic_id": "gps", "condition": "A_normal", "position": "1", "phase": "pre",
         "item_id": "gps_post_1", "score": "1"},
        {"participant_id": "P01", "topic_id": "fridge", "condition": "A_normal", "position": "1", "phase": "post",
         "item_id": "gps_post_1", "score": "1"},
        {"participant_id": "P01", "topic_id": "gps", "condition": "A_normal", "position": "1", "phase": "post",
         "item_id": "gps_explain", "score": "3"},
    ]
    write_comprehension(rated_run, assignment, extra_rows=bad)
    _, issues = summarize_results.summarize(rated_run, n_boot=50)
    text = "\n".join(issues.errors)
    assert "unknown item_id 'no_such_item'" in text
    assert "is a post item but phase is 'pre'" in text
    assert "belongs to topic gps" in text
    assert "outside 0-2" in text
