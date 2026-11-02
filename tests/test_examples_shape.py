"""Phase 8 (docs/SKILL_UPGRADE_PLAN_V2.md): the worked examples follow the rules they teach.

Every complete answer in the two example references passes both linters with no break and no flag.
The gold answers in layout-exemplars.md carry every page-shape slot and ship only in the full build.
The "better" answers in explanation-examples.md carry the layout but no voice or close callouts, so
a single-operation build never shows another operation's callout.
"""

import re

import pytest

import lint_markdown as lm
import skilllib as lib
import structural_metrics as sm

REFERENCES = lib.SKILL_DIR / "references"
EXEMPLARS = REFERENCES / "layout-exemplars.md"
EXAMPLES = REFERENCES / "explanation-examples.md"
ANSWER_RE = re.compile(r"^````markdown\n(.*?)\n````$", re.MULTILINE | re.DOTALL)
CALLOUTS = ("🙋", "🧠", "🎯", "🧪")
# Pairs whose better answer stays short on purpose ("a short answer stays short"), and the section
# whose pairs demonstrate one visual form each rather than a whole answer.
SHORT_BY_DESIGN = {"Follow-up confusion: repairing one link", "Visual forms"}


def answers(path) -> list[str]:
    return ANSWER_RE.findall(path.read_text(encoding="utf-8"))


def pair_sections(text: str) -> dict[str, str]:
    """Each '## ' section of explanation-examples.md, outside fenced answers, keyed by its title."""
    sections: dict[str, str] = {}
    title = None
    for chunk in re.split(r"(?m)^(## .+)$", ANSWER_RE.sub("````ANSWER````", text)):
        if chunk.startswith("## "):
            title = chunk[3:].strip()
        elif title:
            sections[title] = chunk
    return sections


ALL_ANSWERS = [(p.name, i, a) for p in (EXEMPLARS, EXAMPLES) for i, a in enumerate(answers(p), start=1)]


@pytest.mark.parametrize("name, index, answer", ALL_ANSWERS, ids=[f"{n}#{i}" for n, i, _ in ALL_ANSWERS])
def test_every_answer_renders_and_raises_no_flag(name, index, answer):
    assert lm.check(answer) == []
    assert sm.decorative_structure_flags(answer) == []


@pytest.mark.parametrize("answer", answers(EXEMPLARS), ids=lambda a: a.splitlines()[0][2:40])
def test_gold_answers_fill_every_slot(answer):
    lines = answer.splitlines()
    assert lines[0].startswith("# ") and lines[1] == "" and lines[2] == "---"
    assert len(re.findall(r"(?m)^## ", answer)) >= 3
    assert re.search(r"(?m)^> 🙋 \*\*.+\?\*\*\n\n[^>\s]", answer), "a 🙋 line, a blank line, then body text"
    assert re.search(r"(?m)^> 🧠 \*\*Think of it like:\*\*", answer)
    assert re.search(r"(?m)^> 🎯 \*\*Takeaway:\*\*", answer)
    assert re.search(r"(?m)^> 🧪 \*\*Check yourself:\*\*", answer) and re.search(r"(?m)^> \*\*Answer:\*\*", answer)
    assert "###" not in answer


def test_there_are_three_gold_answers():
    assert len(answers(EXEMPLARS)) == 3


def test_every_better_answer_is_laid_out_except_the_short_ones():
    sections = pair_sections(EXAMPLES.read_text(encoding="utf-8"))
    pairs = {t: s for t, s in sections.items() if "**Better" in s}
    laid_out = {t for t, s in pairs.items() if "````ANSWER````" in s}
    assert set(pairs) - laid_out == SHORT_BY_DESIGN
    assert len(laid_out) == len(answers(EXAMPLES)) == 6


@pytest.mark.parametrize("answer", answers(EXAMPLES), ids=lambda a: a.splitlines()[0][2:40])
def test_better_answers_carry_layout_but_no_callouts(answer):
    lines = answer.splitlines()
    assert lines[0].startswith("# ") and lines[2] == "---"
    assert re.search(r"(?m)^## ", answer)
    for icon in CALLOUTS:
        assert f"> {icon}" not in answer, f"{icon} belongs to another operation's build"


def test_gold_answers_ship_only_in_the_full_build():
    source = EXEMPLARS.read_text(encoding="utf-8")
    marker = "Why more replicas can slow down writes"
    assert marker in lib.render_markers(source, lib.VARIANTS["full"])
    for variant, ops in lib.VARIANTS.items():
        if variant != "full":
            assert marker not in lib.render_markers(source, ops), variant
