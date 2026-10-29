"""Pre-release communication-quality recovery: tests for where information belongs.

The owner rejected v0.5.2's answers on three real prompts (database replication, an
architecture decision, CPU cache coherence). The observed faults were paragraph-length
table cells, diagrams retold as numbered steps, one database's internals taught as the
general mechanism, and assumptions repeated until paragraphs went dense. The recovery
refined existing rules in place; see docs/communication-recovery.md.

These are static assertions over the loaded SKILL.md, its references, the policy
modules and both installed artifacts. They show which instructions ship. They cannot
show that Claude's answers improved; behavioural acceptance stays with the owner
(docs/COMMUNICATION_BASELINE.md).
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
# Test B: decision tables keep the verdict in the cell and the argument under it
# ---------------------------------------------------------------------------

def test_table_rows_keep_the_verdict_and_move_the_argument_under_the_table():
    block = norm(op_block(skill_source(), "presentation"))
    assert "When a row needs a condition, a second reason, or an argument" in block
    assert "keep the verdict in the cell and give the reasoning in a list under the table" in block


def test_table_cells_still_have_no_absolute_word_limit():
    """The owner asked for scannable cells without an absolute word limit."""
    block = norm(op_block(skill_source(), "presentation"))
    assert "a short sentence where the comparison needs one" in block
    assert "never a sentence" not in norm(skill_source())


def test_causal_links_are_no_longer_routed_into_table_cells():
    """The old rule told a table to carry its 'because' inside the cell."""
    text = norm(skill_source())
    assert "When a list or table separates two causally linked facts" not in text
    assert "When a list separates two causally linked facts, write the link inside the item" in text


def test_decisions_lead_with_the_recommendation():
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    assert "lead with the recommendation and the reason that decides it" in strategies
    assert "then weigh the tradeoffs behind it" in strategies
    assert "name what would make a rejected one worth adopting" in strategies


def test_assumed_scale_is_stated_once_with_what_would_change_the_answer():
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)"))
    assert "and what would change the answer" in accuracy
    assert "State each assumption once, where it first matters" in accuracy
    # The Phase 4 and 4C accuracy requirements stay intact.
    assert "Name the settings a guarantee depends on" in accuracy
    assert "not a categorical guarantee" in accuracy


# ---------------------------------------------------------------------------
# Tests A and C: a figure and its text do different jobs
# ---------------------------------------------------------------------------

def test_figure_and_text_have_different_jobs():
    block = norm(op_block(skill_source(), "visual"))
    assert "Give a figure and its text different jobs" in block
    assert "the diagram shows who acts in what order" in block
    assert "a state table what each step changes" in block
    assert "the sentences after them why each step happens" in block


def test_retelling_becomes_reasons_without_banning_a_walkthrough():
    """Reinforcement stays allowed; mechanical repetition does not."""
    block = norm(op_block(skill_source(), "visual"))
    assert "Turn numbered steps or prose that only retell the arrows into that why" in block
    assert "unless this reader needs the steps in words as well" in block


def test_step_3_checks_the_text_beside_a_figure_and_the_table_reasoning():
    check = norm(step_3(skill_source()))
    assert "text after it adding the why rather than a retelling" in check
    assert "Does every table cell stay scannable, with its argument under the table" in check


# ---------------------------------------------------------------------------
# Test A: general mechanism first, one system's version labelled
# ---------------------------------------------------------------------------

def test_general_mechanism_precedes_a_labelled_system_version():
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)"))
    assert "Teach the general mechanism first, then label one system's own version" in accuracy
    assert "carry no database" in accuracy


def test_depth_layer_names_what_counts_as_specialist_depth():
    block = norm(op_block(skill_source(), "presentation"))
    assert "Put specialist depth (variants, tuning, one system's edge cases) in a blockquote" in block
    assert "keep the narrative complete for a reader who skips it" in block


# ---------------------------------------------------------------------------
# Explanation design: problem -> concept -> mechanism -> demonstration -> implications
# ---------------------------------------------------------------------------

def test_learnable_order_includes_a_demonstration_but_stays_optional():
    block = norm(op_block(skill_source(), "sequencing"))
    assert "how it works, a concrete case that shows it working, then consequences or tradeoffs" in block
    assert "Use only the stages this answer needs" in block


def test_running_example_reaches_the_behaviour_in_question():
    block = norm(op_block(skill_source(), "examples"))
    assert "Trace it to the moment the behaviour in question shows" in block


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


RECOVERY_MARKERS = (
    "keep the verdict in the cell and give the reasoning in a list under the table",
    "Give a figure and its text different jobs",
    "lead with the recommendation and the reason that decides it",
    "Teach the general mechanism first, then label one system's own version",
    "State each assumption once, where it first matters",
)


def test_recovery_rules_ship_in_the_claude_ai_zip(tmp_path):
    out, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        skill_md = norm(archive.read("socialized/SKILL.md").decode("utf-8"))
    for marker in RECOVERY_MARKERS:
        assert marker in skill_md, marker


def test_recovery_rules_ship_in_the_plugin():
    skill_md = norm(read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md"))
    for marker in RECOVERY_MARKERS:
        assert marker in skill_md, marker


# ---------------------------------------------------------------------------
# References, policy modules and the behavioural reference agree
# ---------------------------------------------------------------------------

def test_references_agree_with_the_recovery_rules():
    selection = norm(read(lib.SKILL_DIR / "references" / "treatment-selection.md"))
    assert "Give the figure and its text different jobs" in selection
    assert "**A diagram retold in steps.**" in selection
    assert "**One system taught as the rule.**" in selection
    assert "**Qualifiers on every sentence.**" in selection
    assert "A short sentence in a cell is fine" in selection
    assert "Sentences in cells, more than four columns" not in selection
    examples = norm(read(lib.SKILL_DIR / "references" / "explanation-examples.md"))
    assert "### A decision table with its reasoning underneath" in examples
    assert "### A figure and the text beside it" in examples


def test_policy_modules_agree_with_the_recovery_rules(repo_root):
    comms = repo_root / "communication"
    controls = norm(read(comms / "controls.md"))
    assert "keep the verdict in the cell and put the reasoning in a list under the table" in controls
    assert "Give a figure and its text different jobs" in controls
    strategies = norm(read(comms / "strategies.md"))
    assert "lead with the recommendation and the reason that decides it" in strategies
    core = norm(read(comms / "core.md"))
    assert "Teach the general mechanism first" in core
    readme = norm(read(comms / "README.md"))
    assert "Change summary (v0.5.0" in readme
    assert "Change summary (v0.6.0" in readme


def test_behavioural_reference_separates_evidence_from_intent(repo_root):
    doc = read(repo_root / "docs" / "COMMUNICATION_BASELINE.md")
    for prompt_start in ("Explain how database replication works internally.",
                         "I'm building a task management application for around 500 users.",
                         "Teach me how CPU cache coherence works in a multicore processor."):
        assert prompt_start in doc, prompt_start
    for heading in ("Captured model responses", "Desired behaviour", "Structural tests",
                    "Unverified assumptions"):
        assert heading in doc, heading
    # No v0.5.2 output is claimed as captured in the repository.
    assert "not stored in this repository" in doc
