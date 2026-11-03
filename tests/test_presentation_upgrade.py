"""Invariants for the skill upgrade, Phases 1-4 (docs/SKILL_UPGRADE_PLAN.md) and Phases 5-6
(docs/SKILL_UPGRADE_PLAN_V2.md).

Each rule is checked against the build that carries it, not against a pinned sentence: a rule
owned by an operation must appear in that operation's single-op build more often than in the core
build, and an always-on rule must appear in the core build. Anchors are the smallest tokens that
carry a rule, so rewording a rule stays cheap and deleting one fails here.

Phase 6 moved rules out of SKILL.md into a reference. Each moved rule is checked the same way in
the reference, and its pointer in SKILL.md is checked like any other rule.
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
    (1, "emphasis styles", "presentation", ["Use bold, italic, `code`, and blockquote for style"]),
    (1, "smaller sections", "presentation", ["twelve lines"]),
    (1, "bolded-label bullets", "presentation", ["bolded label"]),
    (2, "conversational operation", "conversational", ["## Operation: Write the reader's next question"]),
    (2, "reader's-question move", "conversational", ["alone as a `> 🙋 **…?**` line, then a blank line"]),
    (2, "anti-chattiness", "conversational", ["praise", "persona"]),
    (2, "direct address", "conversational", ['"you"']),
    (2, "contractions", "conversational", ["contractions"]),
    (2, "Step 3 reader's-question check", "conversational", ["surface the reader's next question"]),
    (2, "scenario opening", "examples", ["concrete situation"]),
    (2, "analogy beside the case", "examples", ["beside that case and never in its place"]),
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
    (7, "page shape section", None, ["## Page shape (answers of two or more sections)"]),
    (7, "shape fixed, wording free", None, ["The shape is fixed; the wording never is"]),
    (7, "title before the answer", None, ["any heading except the title"]),
    (7, "blank line before a rule", None, ["or the text becomes a heading"]),
    (7, "title slot", "presentation", ["**Title:** one `#` line, a blank line, then `---`"]),
    (7, "title and sections", "presentation", ["`#` title of about eight words, use `##`"]),
    (7, "no depth from ### or ####", "presentation", ["not from `###` or `####`"]),
    (7, "two-sentence opener", "presentation", ["opener to two sentences, a bold lead-in included"]),
    (7, "bold stays in body text", "presentation", ["in body text rather than a callout"]),
    (7, "overview slot", "visual", ["**Overview:**"]),
    (7, "question slot", "conversational", ["**Question:** at least one"]),
    (7, "decision answers ask too", "conversational", ["Use this for teaching and decision answers"]),
    (7, "separator row stays plain", None, ["keep the `|---|` row plain"]),
    (8, "exemplar pointer", None, ["references/layout-exemplars.md"]),
    (8, "glosses outside the ceiling", "presentation", ["not counting a gloss of six words or fewer"]),
    (9, "overview flowchart", "visual", ["a `flowchart LR` after the answer, before the map"]),
    (9, "long linear flow in Mermaid", "visual", ["one of five or more as a Mermaid `flowchart LR`"]),
    (9, "sequence highlight", "visual", ["`rect rgb(...)`"]),
    (9, "callout kinds", "visual", ["Open each callout with its kind", "🛑 pitfall", "💡 key idea"]),
    (9, "icon-led labels in longer lists", "visual", ["bullet in a list of three or more"]),
    (9, "compared numbers as visuals", "visual", ["any two numbers a sentence compares"]),
    (9, "takeaway of three or four links", "close", ["three or four links"]),
    (7, "analogy slot", "examples", ["**Analogy:** one"]),
    (7, "scenario after the answer", "examples", ["first section after the answer"]),
    (7, "gloss slot", "terms", ["**Terms:** a short gloss"]),
    (7, "close slot", "close", ["**Close:** a"]),
    (7, "takeaway callout", "close", ["callout that compresses the mechanism"]),
    (7, "check-yourself callout", "close", ["`> 🧪 **Check yourself:**` callout holding"]),
    (7, "practitioner glosses and analogy", "register", ["parenthesis of six words or fewer", "Keep one analogy in any"]),
    (7, "expert drops both", "register", ["drop both the glosses and the analogy"]),
    (7, "Step 3 title", "presentation", ["is there a `#` title over"]),
    (7, "Step 3 section icon", "visual", ["an icon on every section heading"]),
    (7, "Step 3 question line", "conversational", ["as a 🙋 line"]),
    (7, "Step 3 analogy", "examples", ["is there a 🧠 analogy callout"]),
    (7, "Step 3 close callouts", "close", ["compressed 🎯 takeaway"]),
]

# Phrases of rules that Phase 7 replaced because they switched another rule off.
RETIRED = [
    "not on definitions or analogies",
    "none of them is a template",
    "three distinct levels",
    "its own bolded line or short heading",
    "An example beats an analogy",
]

METHODOLOGY = "references/explanation-methodology.md"

# (name, operation or None for always-on, anchors in the reference, pointer anchor in SKILL.md)
MOVED = [
    ("strategy per intent", None,
     ["## 15. Communication strategy by intent", "Rank causes instead of listing them",
      "Keep a requested deliverable in its own form"],
     "section 15 of"),
    ("repair detail", "repair",
     ["## 16. Repair after a clarification or correction", "decide whether your earlier reading of it was wrong",
      "still think the earlier answer was right"],
     "section 16 of"),
    ("work-report detail", "work-report",
     ["## 17. Reporting work that was done", "State what you did not verify", "Mark a planned step not done"],
     "section 17 of"),
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


def reference_text() -> str:
    return (lib.SKILL_DIR / METHODOLOGY).read_text(encoding="utf-8")


def carried(source: str, op: str | None, anchors: list[str]) -> bool:
    core = norm(lib.render_markers(source, frozenset()))
    if op is None:
        return all(norm(a) in core for a in anchors)
    built = norm(lib.render_markers(source, frozenset({op})))
    return all(built.count(norm(a)) > core.count(norm(a)) for a in anchors)


def missing_moves(skill: str, reference: str) -> list[str]:
    return [name for name, op, anchors, pointer in MOVED
            if not (carried(reference, op, anchors) and carried(body(skill), op, [pointer]))]


def test_every_moved_rule_is_reachable():
    assert METHODOLOGY in skill_text()
    assert missing_moves(skill_text(), reference_text()) == []


@pytest.mark.parametrize("name, op, anchors, pointer", MOVED, ids=[m[0] for m in MOVED])
def test_removing_a_pointer_or_a_moved_rule_is_caught(name, op, anchors, pointer):
    assert name in missing_moves(remove_units_containing(skill_text(), pointer), reference_text())
    for anchor in anchors:
        assert name in missing_moves(skill_text(), remove_units_containing(reference_text(), anchor))


def test_moved_rules_left_skill_md():
    text = norm(skill_text())
    for _, _, anchors, _ in MOVED:
        for anchor in anchors[1:]:
            assert norm(anchor) not in text, f"{anchor!r} should live only in {METHODOLOGY}"


def test_retired_conflicting_rules_stay_gone():
    for path in lib.iter_skill_files(lib.SKILL_DIR):
        text = norm(path.read_text(encoding="utf-8")).lower()
        for phrase in RETIRED:
            assert norm(phrase).lower() not in text, f"{path.name} brings back {phrase!r}"


def test_page_shape_slots_follow_their_operations():
    source = body(skill_text())
    shape = lambda ops: lib.render_markers(source, ops).split("## Page shape", 1)[1].split("\n## ", 1)[0]
    core = shape(frozenset())
    assert "**Answer:**" in core and "**Title:**" not in core and "🙋" not in core and "🎯" not in core
    full = shape(lib.VARIANTS["full"])
    for slot in ("**Title:**", "**Answer:**", "**Overview:**", "**Map and sections:**", "**Question:**",
                 "**Analogy:**", "**Terms:**", "**Close:**"):
        assert slot in full, slot


def test_paragraph_ceiling_matches_the_dense_paragraph_gate():
    numbers = {"two": 2, "three": 3, "four": 4, "five": 5}
    match = re.search(r"at (\w+) sentences or about (\d+) words", norm(skill_text()))
    assert match, "the paragraph ceiling must state sentences and words"
    assert sm.DENSE_SENTENCES == numbers[match.group(1)] + 1
    assert sm.DENSE_PARAGRAPH_WORDS == int(match.group(2))


def test_gloss_allowance_matches_the_metric():
    match = re.search(r"not counting a gloss of (\w+) words or fewer", norm(skill_text()))
    assert match, "the paragraph ceiling must state the gloss allowance"
    assert sm.GLOSS_MAX_WORDS == {"five": 5, "six": 6, "seven": 7}[match.group(1)]


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
