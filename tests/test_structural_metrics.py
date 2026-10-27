"""Structural metrics and the response linter.

The fixtures in tests/fixtures/structural/ are shared with the browser extension's TypeScript
port; expected.json is the single source of expected outputs for both implementations.
"""

import json
from pathlib import Path

import pytest

import lint_response
import structural_metrics as sm

FIXTURES = Path(__file__).parent / "fixtures" / "structural"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))


def fixture(name: str) -> str:
    return (FIXTURES / f"{name}.md").read_text(encoding="utf-8")


def m(name: str) -> dict:
    return sm.metrics(fixture(name), EXPECTED[name]["question"])


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_fixture_matches_shared_expected_output(name):
    assert m(name) == EXPECTED[name]["expected"]


def test_every_fixture_has_an_expected_entry():
    assert {p.stem for p in FIXTURES.glob("*.md")} == set(EXPECTED)


@pytest.mark.parametrize("name", ["prose_two_sentences", "prose_causal_chain", "process_steps",
                                  "comparison_table", "labelled_list", "code_block", "branching_diagram"])
def test_legitimate_answers_produce_no_flags(name):
    assert m(name)["decorative_structure_flags"] == []


@pytest.mark.parametrize("name, flag", [
    ("decorative_headings", "heading_thin"),
    ("thin_table", "table_thin"),
    ("bullets_unconnected", "bullets_unconnected"),
    ("emoji_structure", "emoji_structure"),
    ("whitespace_padding", "whitespace_padding"),
    ("empty_transition", "empty_transition"),
    ("emphasis_overuse", "emphasis_overuse"),
])
def test_each_flag_fires_on_its_fixture(name, flag):
    assert flag in m(name)["decorative_structure_flags"]


def test_counts():
    steps = m("process_steps")
    assert steps["numbered_count"] == 5 and steps["bullet_count"] == 0 and steps["block_count"] == 6
    table = m("comparison_table")
    assert table["table_count"] == 1 and table["word_count"] == 50 and table["mean_sentence_words"] == 13.5
    assert m("decorative_headings")["heading_count"] == 2
    assert m("bullets_unconnected")["bullet_count"] == 4
    assert m("code_block")["code_block_count"] == 1
    assert m("branching_diagram")["word_count"] == 25, "words inside the fenced diagram are not counted"


def test_block_sizes():
    chain = m("prose_causal_chain")
    assert chain["block_count"] == 3 and chain["max_block_words"] == 40
    assert m("prose_two_sentences")["mean_block_words"] == 19.0


def test_sentence_level_descriptors():
    assert m("prose_causal_chain")["max_sentence_words"] == 20
    assert m("code_block")["passive_sentence_count"] == 1, "'Nothing has been changed yet'"
    assert m("process_steps")["passive_sentence_count"] == 0
    assert sm.metrics("The server rejects the request.")["passive_sentence_count"] == 0
    assert sm.metrics("The request is rejected by the server.")["passive_sentence_count"] == 1


def test_emphasis_ignores_list_labels():
    assert m("labelled_list")["emphasis_count"] == 0
    assert m("emphasis_overuse")["emphasis_count"] == 4


def test_answer_first_offset():
    assert m("preamble_restatement")["answer_first_offset"] == 13
    assert sm.answer_first_offset(fixture("preamble_restatement")) == 2, "without the question only the preamble counts"
    assert m("decorative_headings")["answer_first_offset"] == 1
    assert m("prose_causal_chain")["answer_first_offset"] == 0


def test_connective_rescues_a_bullet_run():
    assert "bullets_unconnected" not in sm.decorative_structure_flags(
        "Causes:\n\n- Demand rises, so prices rise\n- Energy costs more\n")


def test_two_sentence_heading_section_is_not_thin():
    assert sm.decorative_structure_flags("## Why it fogs\n\nThe lens is cold. Vapour condenses on it.\n") == []


def test_cli_exit_status_and_json(capsys):
    assert lint_response.main([str(FIXTURES / "prose_two_sentences.md")]) == 0
    assert "not a comprehension score" in capsys.readouterr().out
    assert lint_response.main([str(FIXTURES / "thin_table.md"), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["decorative_structure_flags"] == ["table_thin"]


def test_cli_help_carries_the_disclaimer(capsys):
    with pytest.raises(SystemExit):
        lint_response.main(["--help"])
    assert "not a comprehension score" in capsys.readouterr().out


def test_regenerate_reads_only_the_archive_claude_answers(tmp_path):
    result = lint_response.regenerate(tmp_path / "baseline.json")
    assert len(result["answers"]) == 15
    assert {a["style"] for a in result["answers"]} == {"base", "tutor", "pedagogical"}
    assert all(a["model_id"].startswith("claude") for a in result["answers"])
    assert "not a comprehension score" in result["disclaimer"]
