"""Phase 4C: tests for the visual-communication rules Phase 4 removed.

Phase 4 made four behaviours selective (closing quizzes, section previews,
redundant visuals, interactive-demo offers). Three of those were right. The fourth
went too far: it replaced the visual-coverage floor with a negative rule ("do not
require a visual for every shaped idea, every section, or the final third") and
turned the Step 3 visual check from a coverage question into a pruning-only one.
Phase 4C restored the coverage expectation, the paragraph-density rule and the
section separator, and added form selection to the non-teaching strategies, while
keeping everything Phase 4 was right to remove.

The final calibration (same phase, after live tests) turned those restored rules from
unconditional requirements into strong, context-sensitive preferences: no visual
quota, no mandatory final-third figure, no prohibition on sentences in table cells.
The preference has to stay strong, so these tests assert that the pull toward a
figure, a table and a paragraph break is still in the text, and that no quota
wording is.

These are static assertions over the loaded SKILL.md, the reusable policy modules
and both installed artifacts. They show which instructions ship. They cannot show
that Claude formats a real answer better; no behavioural comparison was run. See
docs/phase-4c-visual-restoration.md.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import build_plugin as bp
import skilllib as lib
from package_skill import build as build_skill


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def skill_source() -> str:
    return read(lib.SKILL_DIR / "SKILL.md")


def norm(text: str) -> str:
    """Collapse whitespace so assertions survive prose line-wrapping."""
    return re.sub(r"\s+", " ", text)


def op_block(text: str, op: str) -> str:
    blocks = re.findall(rf"<!-- op:{op} -->\n(.*?)<!-- /op:{op} -->", text, re.DOTALL)
    carrying = [b for b in blocks if "## Operation:" in b]
    assert len(carrying) == 1, f"expected one {op} operation block, found {len(carrying)}"
    return carrying[0]


def section(text: str, heading: str) -> str:
    assert heading in text, heading
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def step_3(text: str) -> str:
    return section(text, "## Step 3: Check before sending (silently)")


def bullets(block: str) -> list[str]:
    out: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            out.append(stripped[2:])
        elif out and stripped and not stripped.startswith(("#", "<!--", "-")):
            out[-1] += " " + stripped
    return [norm(b) for b in out]


# ---------------------------------------------------------------------------
# P4C-01: the visual-coverage floor is back in op:visual
# ---------------------------------------------------------------------------

# Phase 4 wording that suppressed coverage. None of it may return.
SUPPRESSING = [
    "do not require a visual for every shaped idea, every section, or the final third",
    "Draw a visual for each such idea when it clarifies the relationship",
    "a visual would show that relationship better than three or more sentences",
]

# Quota wording the final calibration removed. None of it may return either.
QUOTA = [
    "Draw a visual for each such idea",
    "there is no cap per answer",
    "give the last third of the answer at least the visual support of the first",
    "never a sentence",
]


def test_coverage_suppressing_wording_is_gone():
    text = norm(skill_source())
    for phrase in SUPPRESSING:
        assert norm(phrase) not in text, f"coverage-suppressing wording is back: {phrase!r}"


def test_no_visual_or_formatting_quota():
    """Calibration: strong preferences, never a count the answer has to hit."""
    text = norm(skill_source())
    for phrase in QUOTA:
        assert norm(phrase) not in text, f"quota wording is back: {phrase!r}"


def test_visual_is_the_preferred_treatment_for_a_shaped_idea():
    """The pull toward a figure survives; the requirement does not."""
    block = norm(op_block(skill_source(), "visual"))
    assert "Prefer a visual for such an idea" in block
    assert "delete the sentences it replaces" in block
    # And it is a preference: the escape clause is explicit.
    assert "Leave one out where the prose already makes the relationship plain" in block


def test_visual_support_stays_even_across_a_long_answer():
    block = norm(op_block(skill_source(), "visual"))
    assert "Give the hardest section its visual first" in block
    assert "keep that support even across the answer" in block
    assert "a later section that needs a figure gets one" in block


def test_visual_cue_is_the_three_sentence_test_not_a_second_judgement_gate():
    """One cue, the length of the prose description, not Phase 4 stacked gates."""
    block = norm(op_block(skill_source(), "visual"))
    assert "prose would take three or more sentences to describe that relationship" in block


def test_visual_redundancy_rules_from_phase_4_are_kept():
    block = norm(op_block(skill_source(), "visual"))
    assert "Keep to one representation per idea" in block
    assert "add a second only when it carries a materially different dimension" in block
    assert "makes a comparison genuinely faster" in block


def test_short_answers_still_get_sentences():
    block = norm(op_block(skill_source(), "visual"))
    assert "Give a short answer or a practitioner lookup as sentences" in block


# ---------------------------------------------------------------------------
# P4C-02: the pre-send check can add a missing visual again
# ---------------------------------------------------------------------------

def test_step_3_asks_about_missing_visuals_not_only_redundant_ones():
    check = norm(step_3(skill_source()))
    # A missing figure can still be noticed, in the last third as much as the first.
    assert "Does a mechanism a figure would clarify still have one" in check
    assert "in the last third as much as the first" in check
    # The pruning half stays.
    assert "carry a real relationship" in check
    assert "its replaced prose gone" in check


def test_step_3_prunes_decorative_structure_including_diagrams():
    check = norm(step_3(skill_source()))
    assert "Does every heading, list, table, diagram, and bold sentence mark a real division" in check
    assert "only decorate" in check


# ---------------------------------------------------------------------------
# P4C-03: paragraph density and section separation
# ---------------------------------------------------------------------------

def test_paragraph_breaks_follow_the_idea_not_the_word_count():
    block = norm(op_block(skill_source(), "presentation"))
    assert "Start a new unit when the idea changes, even when the current one is short" in block
    assert "End a paragraph at four sentences or about 80 words" in block
    assert "Give a list item one idea and about 25 words" in block


def test_major_topics_are_separated():
    block = norm(op_block(skill_source(), "presentation"))
    assert ("a horizontal rule (`---`) where an answer of three or more sections "
            "turns to a new topic") in block


def test_step_3_checks_paragraph_and_list_density_and_table_scannability():
    check = norm(step_3(skill_source()))
    for limit in ("four sentences or about 80 words", "any list item about 25 words"):
        assert limit in check, limit
    assert "Does every table cell stay scannable" in check


def test_table_cells_scan_without_banning_sentences():
    """Calibration: a cell prefers a phrase but may be a sentence."""
    block = norm(op_block(skill_source(), "presentation"))
    assert "about six words where a phrase will do" in block
    assert "a short sentence where the comparison needs one" in block
    assert "never a sentence" not in block


# ---------------------------------------------------------------------------
# P4C-04: form follows content in every strategy, not only teaching replies
# ---------------------------------------------------------------------------

def test_strategies_pick_the_form_from_the_content():
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    assert "In every strategy, pick the form from the content" in strategies
    for cue in ("a table for options against", "a diagram for a flow or an interaction",
                "steps for a procedure", "a fenced block for code",
                "prose for a single chain or a casual reply"):
        assert cue in strategies, cue


def test_the_five_strategies_and_their_priorities_are_untouched():
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    for strat in ("Teaching or explanation", "Coding or implementation", "Debugging",
                  "Discussion or decision", "Quick answer or everyday"):
        assert strat in strategies, strat
    # No response template was introduced.
    assert "not templates" in strategies or "They set priorities, not templates" in strategies


def test_form_selection_is_not_a_mandatory_visual():
    """The form cues are choices; none of them demands a diagram for every topic."""
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    for forced in ("always include a diagram", "every answer needs a diagram",
                   "draw a diagram for every"):
        assert forced not in strategies.lower(), forced


# ---------------------------------------------------------------------------
# P4C-05: nothing Phase 4 removed on purpose comes back
# ---------------------------------------------------------------------------

# Phase 4 removed these unconditional directives; Phase 4C must not reinstate them.
STILL_FORBIDDEN = [
    "a follow-up about confusion with one check question the reader can verify",
    "Keep the one-line section map that the presentation operation places",
    "End the answer with one line offering an interactive version",
]


def test_quizzes_previews_and_demo_offers_stay_conditional():
    text = norm(skill_source())
    for phrase in STILL_FORBIDDEN:
        assert norm(phrase) not in text, f"Phase 4 regression reinstated: {phrase!r}"
    close = norm(op_block(skill_source(), "close"))
    assert "asks to practise or be tested" in close
    assert "not a prompt for a quiz" in close
    assert "Leave it out when the last sentence lands the point" in close
    visual = norm(op_block(skill_source(), "visual"))
    assert "never append the offer by default" in visual
    assert "only when the person explicitly asks" in visual
    presentation = norm(op_block(skill_source(), "presentation"))
    assert "add a one-line map of them only when" in presentation


def test_no_word_cap_was_added_to_the_explanation_itself():
    """Task 4: presentation limits bound a unit, never the whole answer."""
    text = norm(skill_source())
    for cap in ("keep the answer under", "no more than 200 words",
                "limit the response to", "shorten the explanation"):
        assert cap not in text.lower(), cap
    # Depth is still sized by the reader's need.
    assert "Add length only when this reader needs it to understand" in text


def test_accuracy_rules_discourage_absolute_and_unsupported_claims():
    """Calibration task 3: refined in place, with no new operation."""
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)"))
    assert "Name the settings a guarantee depends on rather than stating it absolutely" in accuracy
    assert "State any workload, scale, or traffic pattern the answer assumes" in accuracy
    assert "carry no database" in accuracy and "behaviour over to another unchecked" in accuracy
    # Phase 4 scoping is kept, not replaced.
    assert "Scope a product-specific implementation" in accuracy
    assert "not a categorical guarantee" in accuracy
    assert len(lib.OPERATIONS) == 12


def test_technical_depth_is_preserved_by_splitting_not_cutting():
    text = norm(skill_source())
    assert "keep the causal steps a requested mechanism needs" in text
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)"))
    assert "Simplify the expression, not the substance" in accuracy


# ---------------------------------------------------------------------------
# P4C-06: Phase 3 multi-turn behaviour is untouched
# ---------------------------------------------------------------------------

def test_multi_turn_operations_survive():
    text = skill_source()
    for op in ("repair", "persistence", "work-report"):
        assert len(bullets(op_block(text, op))) >= 4, op
    persistence = norm(op_block(text, "persistence"))
    assert "apply it to every later reply until they change it" in persistence
    assert 'Apply an instruction scoped to one reply ("for this answer", "this time")' in persistence
    repair = norm(op_block(text, "repair"))
    assert "change the method rather than the wording" in repair
    # The scope section still routes correction and work-report turns into the skill.
    scope = norm(section(text, "## Scope: decide first whether this applies"))
    assert "use the repair operation" in scope
    assert "use the work-report operation" in scope
    assert "Keep standing instructions in force in every reply" in scope


# ---------------------------------------------------------------------------
# P4C-07: the contract, the validators and both install paths
# ---------------------------------------------------------------------------

def test_contract_is_unchanged():
    assert len(lib.OPERATIONS) == 12
    assert len(lib.VARIANTS) == 15
    assert lib.check_markers(skill_source(), "SKILL.md").errors == []
    assert len(re.findall(r"^## Operation: .*$", skill_source(), re.MULTILINE)) == 12


def test_line_budgets_hold():
    _, body, _ = lib.split_frontmatter(skill_source())
    rendered = lib.render_markers(body, lib.VARIANTS["full"])
    assert rendered.count("\n") + 1 < 460, "rendered SKILL.md exceeds the compactness guard"
    assert body.count("\n") + 1 <= lib.BODY_MAX_LINES, "raw SKILL.md exceeds the validator budget"


def test_every_restored_rule_names_an_action():
    """AGENTS.md skill-text rule: a rule satisfiable by a plain paragraph is wrong."""
    for op in ("visual", "presentation"):
        for rule in bullets(op_block(skill_source(), op)):
            assert not rule.lower().startswith(("do not", "don't", "never", "avoid")), rule


RESTORED_MARKERS = (
    "Prefer a visual for such an idea",
    "keep that support even across the answer",
    "Does a mechanism a figure would clarify still have one",
    "even when the current one is short",
    "horizontal rule (`---`) where an answer of three or more sections",
    "In every strategy, pick the form from the content",
    "Name the settings a guarantee depends on",
)


def test_restored_policy_ships_in_the_claude_ai_zip(tmp_path):
    out, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        skill_md = archive.read("socialized/SKILL.md").decode("utf-8")
    assert "op:" not in skill_md
    normalized = norm(skill_md)
    for marker in RESTORED_MARKERS:
        assert marker in normalized, marker
    for phrase in SUPPRESSING + QUOTA + STILL_FORBIDDEN:
        assert norm(phrase) not in normalized, phrase


def test_restored_policy_ships_in_the_plugin():
    skill_md = read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md")
    assert "op:" not in skill_md
    normalized = norm(skill_md)
    for marker in RESTORED_MARKERS:
        assert marker in normalized, marker
    for phrase in SUPPRESSING + QUOTA + STILL_FORBIDDEN:
        assert norm(phrase) not in normalized, phrase


# ---------------------------------------------------------------------------
# P4C-08: the reference files agree with the skill
# ---------------------------------------------------------------------------

def test_treatment_selection_agrees_with_the_calibrated_visual_rule():
    text = norm(read(lib.SKILL_DIR / "references" / "treatment-selection.md"))
    assert "A visual** fits an idea whose content has a shape" in text
    assert "There is no quota and no cap" in text
    assert "draw as many as the ideas earn" in text
    assert "keep the support even across the answer rather than front-loading it" in text
    # The anti-redundancy half is stated there too.
    assert "add a second only when it carries a materially different dimension" in text
    assert "leave one out where the prose already makes the relationship plain" in text


def test_policy_modules_agree_with_the_restored_rules(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        assert "Version 0.5.0" in read(comms / name), name
    controls = norm(read(comms / "controls.md"))
    assert "Prefer a visual for an idea whose shape" in controls
    assert "keep the support even across the answer" in controls
    assert "There is no quota and no cap" in controls
    assert "Start a new paragraph when the idea changes" in controls
    assert "Keep a table cell scannable" in controls
    assert "an architecture or tool comparison earns a table" in controls
    assert "Name the settings a guarantee depends on" in norm(read(comms / "core.md"))
    core = norm(read(comms / "core.md"))
    assert "## 11. Readable presentation" in core
    assert "never" not in core.split("## 11. Readable presentation")[1].split("Enforced by")[0].lower() \
        or "rather than shortening it by dropping one" in core
    strategies = norm(read(comms / "strategies.md"))
    assert "long undifferentiated prose where the content has a shape" in strategies


def test_policy_readme_records_the_regression_and_the_fix(repo_root):
    readme = norm(read(repo_root / "communication" / "README.md"))
    assert "v0.4.0" in readme
    assert "Change summary (Phase 4C" in readme
    assert "Visual coverage | Restore" in readme
    assert "Quizzes, previews, demo offers, artifacts | Preserve" in readme
