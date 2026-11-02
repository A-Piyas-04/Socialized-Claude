"""Invariants for the Phase 1-4 skill upgrade (docs/SKILL_UPGRADE_PLAN.md).

Each rule is checked against the build that carries it, not against a pinned sentence: a rule
owned by an operation must appear in that operation's single-op build more often than in the core
build, and an always-on rule must appear in the core build. Anchors are the smallest tokens that
carry a rule, so rewording a rule stays cheap and deleting one fails here.
"""

import re

import pytest

import lint_markdown as lm
import lint_response
import skilllib as lib
import structural_metrics as sm

# (phase, name, operation or None for always-on, anchors)
RULES = [
    (1, "paragraph ceiling", "presentation", ["three sentences", "50 words"]),
    (1, "continuous-argument exception", "presentation", ["continuous argument"]),
    (1, "visible separation", "presentation", ["visible separation"]),
    (1, "emphasis ladder", "presentation", ["three distinct levels", "`####`", "blockquote"]),
    (1, "smaller sections", "presentation", ["twelve lines"]),
    (1, "bolded-label bullets", "presentation", ["bolded label"]),
    (2, "conversational operation", "conversational", ["## Operation: Write the reader's next question"]),
    (2, "reader's-question move", "conversational", ["its own bolded line"]),
    (2, "anti-chattiness", "conversational", ["praise", "persona"]),
    (2, "direct address", "conversational", ['"you"']),
    (2, "contractions", "conversational", ["contractions"]),
    (2, "Step 3 reader's-question check", "conversational", ["surface the reader's next question"]),
    (2, "scenario opening", "examples", ["concrete situation"]),
    (2, "analogy equal standing", "examples", ["equal standing"]),
    (2, "state, action, result", "examples", ["state, then action, then result"]),
    (2, "gloss before use", "terms", ["first appears or the one before it"]),
    (2, "conversation-grammar pointer", None, ["references/conversation-grammar.md"]),
    (3, "status layer", "visual", ["closed legend"]),
    (3, "navigation layer", "visual", ["navigation icon"]),
    (3, "palette pointer", "visual", ["or from `references/emoji-palette.md`"]),
    (3, "three colour techniques", "visual", ["`diff` fence", "`classDef` fills", "status emoji"]),
    (3, "diagram every branch or time order", "visual", ["branching or time-ordered"]),
    (3, "artifact keeps markdown complete", "visual", ["complete without it"]),
    (3, "icons out of code", "visual", ["icon out of code"]),
    (3, "palette reference entry", None, ["references/emoji-palette.md"]),
    (4, "markdown section", None, ["## Markdown that renders (always apply)"]),
    (4, "fence width", None, ["more backticks than any inside it"]),
    (4, "escaped pipes", None, ["`\\|`"]),
    (4, "row cell count", None, ["header's cell count"]),
    (4, "plain Mermaid labels", None, ["Mermaid label to plain words"]),
    (4, "no heading jumps", None, ["one level at a time"]),
    (4, "palette-only emoji", None, ["every emoji from the palette"]),
    (4, "Step 3 markdown check", None, ["every Mermaid label stay plain"]),
]


def norm(text: str) -> str:
    return " ".join(text.split())


def body(text: str) -> str:
    _, rest, _ = lib.split_frontmatter(text.replace("\r\n", "\n"))
    return rest


def missing_rules(text: str) -> list[str]:
    source = body(text)
    core = norm(lib.render_markers(source, frozenset()))
    missing = []
    for _, name, op, anchors in RULES:
        if op is None:
            ok = all(norm(a) in core for a in anchors)
        else:
            built = norm(lib.render_markers(source, frozenset({op})))
            ok = all(built.count(norm(a)) > core.count(norm(a)) for a in anchors)
        if not ok:
            missing.append(name)
    return missing


def units(lines: list[str]) -> list[tuple[int, int]]:
    """Line spans of each bullet, heading, or paragraph, continuation lines included."""
    spans, start = [], None
    for i, line in enumerate(lines + [""]):
        continues = start is not None and line.strip() and line.startswith(" ") and not line.lstrip().startswith("- ")
        if continues:
            continue
        if start is not None:
            spans.append((start, i))
            start = None
        if line.strip() and not lib.parse_marker(line):
            start = i
            if line.startswith("#"):
                spans.append((i, i + 1))
                start = None
    return spans


def remove_units_containing(text: str, anchor: str) -> str:
    lines = text.replace("\r\n", "\n").split("\n")
    drop = set()
    for start, end in units(lines):
        if norm(anchor) in norm(" ".join(lines[start:end])):
            drop.update(range(start, end))
    assert drop, f"anchor {anchor!r} is not in any unit"
    return "\n".join(line for i, line in enumerate(lines) if i not in drop)


def skill_text() -> str:
    return (lib.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


def test_every_upgrade_rule_is_present():
    assert missing_rules(skill_text()) == []


@pytest.mark.parametrize("phase, name, op, anchors", RULES, ids=[r[1] for r in RULES])
def test_removing_a_rule_is_caught(phase, name, op, anchors):
    assert name in missing_rules(remove_units_containing(skill_text(), anchors[0]))


def test_paragraph_ceiling_matches_the_dense_paragraph_gate():
    numbers = {"two": 2, "three": 3, "four": 4, "five": 5}
    match = re.search(r"at (\w+) sentences or about (\d+) words", norm(skill_text()))
    assert match, "the paragraph ceiling must state sentences and words"
    assert sm.DENSE_SENTENCES == numbers[match.group(1)] + 1
    assert sm.DENSE_PARAGRAPH_WORDS == int(match.group(2))


def test_table_width_rule_matches_both_linters():
    text = norm(skill_text())
    assert "at most four columns" in text and "keep tables to four columns" in text
    assert sm.TABLE_MAX_COLUMNS == 4
    five = "The table.\n\n| A | B | C | D | E |\n|---|---|---|---|---|\n| 1 | 2 | 3 | 4 | 5 |\n"
    assert "wide_table" in sm.decorative_structure_flags(five)
    assert [b.code for b in lm.check(five)] == ["wide_table"]


def test_heuristics_never_gate(monkeypatch, tmp_path):
    loud = {field: 999 for field in lint_response.HEURISTIC_FIELDS}
    monkeypatch.setattr(sm, "metrics", lambda text, question=None: {**loud, "decorative_structure_flags": []})
    path = tmp_path / "any.md"
    path.write_text("Anything.\n", encoding="utf-8")
    assert lint_response.main([str(path)]) == 0
    assert lint_response.main([str(path), "--json"]) == 0


def test_markdown_rules_ship_in_every_variant():
    source = body(skill_text())
    for variant, ops in lib.VARIANTS.items():
        assert "## Markdown that renders (always apply)" in lib.render_markers(source, ops), variant


def test_operation_and_palette_shape():
    assert "conversational" in lib.OPERATIONS and lib.VARIANTS["conv"] == frozenset({"conversational"})
    assert 140 <= len(sm.NAV_ICONS) <= 160
