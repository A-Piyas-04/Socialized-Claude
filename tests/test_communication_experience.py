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
    block = norm(op_block(skill_source(), "presentation"))
    assert "One primary idea per paragraph" in block
    assert "End a paragraph at four sentences or about 80 words as a ceiling, not a target" in block
    assert "Two independently important claims never share a paragraph" in block
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
    sequencing = norm(op_block(skill_source(), "sequencing"))
    assert "Prioritise internally as core understanding, then the supporting mechanism, then optional advanced detail" in sequencing
    assert "keep those layers in separate units" in sequencing
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
    visual = norm(op_block(skill_source(), "visual"))
    assert "Use a semantic icon as a navigation aid" in visual
    assert "in a heading, a diagram node, a callout, or a compact label" in visual
    assert "🗄️ storage" in visual
    assert "Match use to intent" in visual
    assert "never as a template or a requirement" in visual
    assert "keep icons out of executable code, identifiers, JSON, and logs" in visual
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
    visual = norm(op_block(skill_source(), "visual"))
    assert "Give a figure and its text different jobs" in visual
    assert "A comparison table summarises distinctions; it does not retell the diagram" in visual


# ---------------------------------------------------------------------------
# Task 7: examples trace a run, not a restated definition
# ---------------------------------------------------------------------------

def test_examples_trace_state_action_mechanism_result():
    block = norm(op_block(skill_source(), "examples"))
    assert "Show the initial state, the action, the internal mechanism, the resulting state, and why that result matters" in block
    assert "Trace it to the moment the behaviour in question shows" in block
    assert "invented numbers consistent with each other" in block
    check = norm(step_3(skill_source()))
    assert "show the initial state, the action, the result, and why that result matters" in check


# ---------------------------------------------------------------------------
# Step 3 notices the new faults
# ---------------------------------------------------------------------------

def test_step_3_checks_mixed_claims_and_decorative_icons():
    check = norm(step_3(skill_source()))
    assert "Does any paragraph mix two independently important claims?" in check
    assert "Are icons navigation, not decoration?" in check


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
    "One primary idea per paragraph",
    "as a ceiling, not a target",
    "Prioritise internally as core understanding",
    "Use a semantic icon as a navigation aid",
    "the components of a system and how they connect",
    "A comparison table summarises distinctions",
    "Show the initial state, the action, the internal mechanism",
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
    assert "A meaning-matched icon may label a heading, node or component" in selection
    assert "tracing initial state, action, mechanism, resulting state" in selection
    assert "**Decorative icons.**" in selection
    examples = norm(read(lib.SKILL_DIR / "references" / "explanation-examples.md"))
    assert "### Semantic icons as navigation" in examples


def test_policy_modules_agree_with_the_experience_rules(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        assert "Version 0.6.0" in read(comms / name), name
    controls = norm(read(comms / "controls.md"))
    assert "Use a meaning-matched icon as a navigation aid" in controls
    assert "Match use to intent" in controls
    assert "architecture diagrams show components and connections" in controls
    core = norm(read(comms / "core.md"))
    assert "Order internally as core understanding" in core
    strategies = norm(read(comms / "strategies.md"))
    assert "meaning-matched icon as navigation" in strategies
    readme = norm(read(comms / "README.md"))
    assert "Change summary (v0.6.0" in readme
    assert "Semantic icons | Add" in readme
