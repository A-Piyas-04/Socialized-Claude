"""Communication-experience upgrade: tests for presentation rules that ship.

The owner asked for a better communication experience from the installed skill:
less dense prose, less congested tables, less diagram/prose repetition, clearer
separation of essential from optional detail, more visual variety, and semantic
icon-style emojis as navigation aids. The upgrade refined existing operations in
place; see docs/communication-experience-upgrade.md.

These are static assertions over the loaded SKILL.md, its references, the policy
modules and both installed artifacts. They show which instructions ship. They
cannot show that Claude's answers improved; behavioural acceptance stays with the
owner.
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


# ---------------------------------------------------------------------------
# Task 1: paragraphs stay readable without a fixed sentence quota
# ---------------------------------------------------------------------------

def test_one_primary_idea_per_paragraph_and_a_ceiling_not_a_target():
    # v0.7.0 priority correction: "one primary idea" and "two claims never share a
    # paragraph" merged into one idea-based rule that also separates cause, mechanism
    # and consequence (docs/communication-priority-correction.md).
    block = norm(op_block(skill_source(), "presentation"))
    assert "Give each independently important idea its own unit" in block
    assert "End a paragraph at four sentences or about 80 words as a ceiling, not a target" in block
    assert "Give cause, mechanism, and consequence separate sentences" in block
    assert "Use a list only when the points are genuinely distinct" in block


# ---------------------------------------------------------------------------
# Task 2: comparison tables stay scannable
# ---------------------------------------------------------------------------

def test_table_cells_make_the_primary_decision_visible():
    block = norm(op_block(skill_source(), "presentation"))
    assert "so the primary decision is visible at a glance" in block
    assert "keep the verdict in the cell and give the reasoning in a list under the table" in block


# ---------------------------------------------------------------------------
# Task 3: core → supporting mechanism → optional detail, not a template
# ---------------------------------------------------------------------------

def test_hierarchy_is_internal_priority_not_a_template():
    # v0.7.0: the internal hierarchy moved out of op:sequencing into one planning
    # order in always-on Step 2, so it is stated once.
    step_2 = norm(section(skill_source(), "## Step 2: Size the answer"))
    assert "Plan silently in this order" in step_2
    assert "then only the detail this reader needs, after the core is complete" in step_2
    assert "Prioritise internally" not in skill_source()
    text = skill_source()
    for template in ("## Core understanding", "## Necessary supporting", "every answer must have three sections"):
        assert template not in text


# ---------------------------------------------------------------------------
# Task 4: visual variety without a quota
# ---------------------------------------------------------------------------

def test_visual_forms_include_architecture_and_existing_grammar():
    visual = norm(op_block(skill_source(), "visual"))
    assert "the components of a system and how they connect" in visual
    assert "sequenceDiagram" in visual
    assert "flowchart" in visual
    assert "A → B → C" in visual
    presentation = norm(op_block(skill_source(), "presentation"))
    assert "components and how they connect, or order in time" in presentation
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    assert "a diagram for a flow or an interaction" in strategies
    assert "how components" in strategies


# ---------------------------------------------------------------------------
# Task 5: semantic icons as navigation, intent-sensitive, never required
# ---------------------------------------------------------------------------

def test_semantic_icons_are_navigation_not_decoration():
    # v0.7.0: the gated icon rule became a default preference for substantive
    # explanations; the exclusions stay.
    visual = norm(op_block(skill_source(), "visual"))
    assert "Prefer meaning-matched icons as navigation in a substantive explanation" in visual
    assert "open the key headings, callouts, or diagram labels (not every one)" in visual
    assert "🗄️ storage" in visual
    assert "Keep icons out of code, identifiers, JSON, logs, formal writing, and short or casual replies" in visual
    assert "no other symbols" not in visual
    assert "Keep headings and step numbers as words" not in skill_source()


def test_status_legend_survives_beside_semantic_icons():
    visual = norm(op_block(skill_source(), "visual"))
    assert "✅ works" in visual and "❌ broken" in visual
    assert "or a meaning-matched icon" in visual


# ---------------------------------------------------------------------------
# Task 6: visuals and prose stay complementary
# ---------------------------------------------------------------------------

def test_a_comparison_table_does_not_retell_the_diagram():
    # v0.7.0: the figure/table/text jobs are one rule covering all three forms.
    visual = norm(op_block(skill_source(), "visual"))
    assert "Give every figure, table, and paragraph a different job" in visual
    assert "a table compares options or tracks state" in visual


# ---------------------------------------------------------------------------
# Task 7: examples trace a run, not a restated definition
# ---------------------------------------------------------------------------

def test_examples_trace_state_action_mechanism_result():
    # v0.7.0: the mechanism and "why it matters" beats belong to the figure and the
    # text, so the example traces state, action and result without retelling them.
    block = norm(op_block(skill_source(), "examples"))
    assert "Show the initial state, the action, and the resulting state" in block
    assert "Trace it to the moment the behaviour in question shows" in block
    assert "invented numbers consistent with each other" in block
    check = norm(step_3(skill_source()))
    assert "show the initial state, the action, and the result" in check


# ---------------------------------------------------------------------------
# Step 3 notices the new faults
# ---------------------------------------------------------------------------

def test_step_3_checks_mixed_claims_and_decorative_icons():
    # v0.7.0: the icon check is additive (does a substantive answer use them?), and
    # decoration is caught by the one-job-per-part check.
    check = norm(step_3(skill_source()))
    assert "Does any paragraph or list item mix two independently important ideas" in check
    assert "mark its key parts with meaning-matched icons" in check
    assert "icon do a job nothing else in the reply does" in check


# ---------------------------------------------------------------------------
# Preservation: the contract and every earlier fix stay intact
# ---------------------------------------------------------------------------

FORBIDDEN = [
    "a follow-up about confusion with one check question the reader can verify",
    "Keep the one-line section map that the presentation operation places",
    "End the answer with one line offering an interactive version",
    "do not require a visual for every shaped idea, every section, or the final third",
    "Draw a visual for each such idea",
    "there is no cap per answer",
    "never a sentence",
]


def test_contract_and_earlier_fixes_are_preserved():
    text = norm(skill_source())
    assert len(lib.OPERATIONS) == 12 and len(lib.VARIANTS) == 15
    assert lib.check_markers(skill_source(), "SKILL.md").errors == []
    assert len(re.findall(r"^## Operation: .*$", skill_source(), re.MULTILINE)) == 12
    for phrase in FORBIDDEN:
        assert norm(phrase) not in text, phrase
    visual = norm(op_block(skill_source(), "visual"))
    assert "Prefer a visual for such an idea" in visual
    assert "Leave one out where the prose already makes the relationship plain" in visual


def test_new_rules_name_actions():
    """AGENTS.md skill-text rule: every rule names an action the model takes."""
    for op in ("visual", "presentation", "sequencing", "examples"):
        block = op_block(skill_source(), op)
        rules = [line.strip()[2:] for line in block.splitlines() if line.strip().startswith("- ")]
        for rule in rules:
            assert not rule.lower().startswith(("do not", "don't", "never", "avoid")), rule


EXPERIENCE_MARKERS = (
    "Give each independently important idea its own unit",
    "as a ceiling, not a target",
    "Plan silently in this order",
    "Prefer meaning-matched icons as navigation",
    "the components of a system and how they connect",
    "Give every figure, table, and paragraph a different job",
    "Show the initial state, the action, and the resulting state",
)


def test_experience_rules_ship_in_the_claude_ai_zip(tmp_path):
    out, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        skill_md = norm(archive.read("socialized/SKILL.md").decode("utf-8"))
    for marker in EXPERIENCE_MARKERS:
        assert marker in skill_md, marker


def test_experience_rules_ship_in_the_plugin():
    skill_md = norm(read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md"))
    for marker in EXPERIENCE_MARKERS:
        assert marker in skill_md, marker


# ---------------------------------------------------------------------------
# References and policy modules agree
# ---------------------------------------------------------------------------

def test_references_agree_with_the_experience_rules():
    selection = norm(read(lib.SKILL_DIR / "references" / "treatment-selection.md"))
    assert "architecture diagrams for components and connections" in selection
    assert "a meaning-matched icon may label a heading, node or component" in selection
    assert "tracing initial state, action, and resulting state" in selection
    assert "**Decorative icons.**" in selection
    examples = norm(read(lib.SKILL_DIR / "references" / "explanation-examples.md"))
    assert "### Semantic icons as navigation" in examples


def test_policy_modules_agree_with_the_experience_rules(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        assert "Version 0.7.0" in read(comms / name), name
    controls = norm(read(comms / "controls.md"))
    assert "use a meaning-matched icon as a navigation aid by default" in controls
    assert "Match use to intent" in controls
    assert "architecture diagrams show components and connections" in controls
    core = norm(read(comms / "core.md"))
    assert "essential understanding first" in core
    strategies = norm(read(comms / "strategies.md"))
    assert "meaning-matched icon as navigation" in strategies
    readme = norm(read(comms / "README.md"))
    assert "Change summary (v0.6.0" in readme
    assert "Semantic icons | Add" in readme
