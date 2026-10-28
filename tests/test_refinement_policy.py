"""Phase 4: tests for the communication-refinement policy that actually ships.

Phase 4 makes four behaviours selective instead of automatic — closing quizzes,
intro/section previews, redundant visuals, and interactive-demo offers — and
tightens epistemic scoping, without adding an operation, a marker, or a variant.

These assertions check the refined policy in the loaded SKILL.md and in both
installed artifacts (the claude.ai ZIP and the generated plugin). They verify that
the old *unconditional* directives are gone and the new *conditional* ones are
present, that every changed rule still names an action, and that the 12-operation /
15-variant contract and the SKILL.md line budgets are intact.

Offline string and structure assertions cannot show that Claude behaves this way in
real conversations. See docs/phase-4-implementation.md.
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
    """The marker block that carries operation `op`'s own heading."""
    blocks = re.findall(rf"<!-- op:{op} -->\n(.*?)<!-- /op:{op} -->", text, re.DOTALL)
    carrying = [b for b in blocks if f"## Operation:" in b]
    assert len(carrying) == 1, f"expected one {op} operation block, found {len(carrying)}"
    return carrying[0]


def bullets(block: str) -> list[str]:
    out: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            out.append(stripped[2:])
        elif out and stripped and not stripped.startswith(("#", "<!--", "-")):
            out[-1] += " " + stripped
    return [norm(b) for b in out]


def section(text: str, heading: str) -> str:
    assert heading in text, heading
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


# ---------------------------------------------------------------------------
# The contract is untouched (brief §2, §5.3, §7)
# ---------------------------------------------------------------------------

def test_no_new_operation_marker_or_variant():
    assert len(lib.OPERATIONS) == 12
    assert len(lib.VARIANTS) == 15
    assert lib.check_markers(skill_source(), "SKILL.md").errors == []
    headings = re.findall(r"^## Operation: .*$", skill_source(), re.MULTILINE)
    assert len(headings) == 12


def test_skill_stays_within_line_budgets():
    _, body, _ = lib.split_frontmatter(skill_source())
    rendered = lib.render_markers(body, lib.VARIANTS["full"])
    assert rendered.count("\n") + 1 < 460, "rendered SKILL.md exceeds the compactness guard"
    assert body.count("\n") + 1 <= lib.BODY_MAX_LINES, "raw SKILL.md exceeds the validator budget"


# ---------------------------------------------------------------------------
# Unconditional directives that produced the observed defects are gone
# ---------------------------------------------------------------------------

FORBIDDEN = [
    # P4-01: category-forced closing quiz.
    "a follow-up about confusion with one check question the reader can verify",
    # P4-02: mandatory retained section map / preview.
    "Keep the one-line section map that the presentation operation places",
    # P4-03: visual required for the final third of every answer.
    "Give the last third of the answer at least the visual support of the first",
    # P4-04: interactive offer appended by default.
    "End the answer with one line offering an interactive version",
]


def test_forbidden_unconditional_directives_are_removed():
    text = norm(skill_source())
    for phrase in FORBIDDEN:
        assert norm(phrase) not in text, f"unconditional directive still present: {phrase!r}"


# ---------------------------------------------------------------------------
# P4-01: the comprehension check is intent-driven, not categorical
# ---------------------------------------------------------------------------

def test_close_check_question_is_conditional():
    block = norm(op_block(skill_source(), "close"))
    for marker in ("asks to practise or be tested", "explicitly a tutorial",
                   "resolves a real uncertainty"):
        assert marker in block, marker
    # No forced quiz on non-teaching deliverables.
    assert "coding deliverable" in block
    # A confusion follow-up gets an explanation, not a quiz.
    assert "I don't understand X" in block and "not a prompt for a quiz" in block
    # The takeaway is optional.
    assert "Leave it out when the last sentence lands the point" in block


def test_close_rules_still_name_actions():
    rules = bullets(op_block(skill_source(), "close"))
    assert len(rules) >= 5
    for rule in rules:
        assert not rule.lower().startswith(("do not", "don't", "never", "avoid")), rule


# ---------------------------------------------------------------------------
# P4-02: previews / section maps are optional
# ---------------------------------------------------------------------------

def test_section_preview_is_optional():
    plain = norm(op_block(skill_source(), "plain"))
    assert "delete every sentence whose only job is to introduce, preview" in plain
    presentation = norm(op_block(skill_source(), "presentation"))
    assert "add a one-line map of them only when" in presentation


# ---------------------------------------------------------------------------
# P4-03 + P4-04: visuals are selective; demo offers are not automatic
# ---------------------------------------------------------------------------

def test_visuals_are_value_based():
    block = norm(op_block(skill_source(), "visual"))
    assert "Prefer one strong representation per idea" in block
    assert "add a second only when it carries a materially different dimension" in block
    assert "do not require a visual for every shaped idea, every section, or the final third" in block
    # Colour / status markers only when they help a comparison.
    assert "makes a comparison genuinely faster" in block


def test_interactive_offer_is_not_default():
    block = norm(op_block(skill_source(), "visual"))
    assert "never append the offer by default" in block
    assert "Offer an interactive version only when" in block
    # Artifacts remain opt-in.
    assert "only when the person explicitly asks" in block


def test_diagram_claims_are_scoped():
    block = norm(op_block(skill_source(), "visual"))
    assert "do not let a diagram imply a guarantee the mechanism does not actually provide" in block


# ---------------------------------------------------------------------------
# P4-05: epistemic precision without a fact-checking service
# ---------------------------------------------------------------------------

def test_accuracy_rules_scope_implementation_and_concurrency():
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)"))
    assert "Scope a product-specific implementation" in accuracy
    assert "common not universal" in accuracy
    assert "simplified mental model from precise internals" in accuracy
    assert "not a categorical guarantee" in accuracy
    # No external validator / network dependency was introduced anywhere in the skill.
    for path in lib.iter_skill_files(lib.SKILL_DIR):
        assert lib.scan_text(read(path), path.name).errors == []


# ---------------------------------------------------------------------------
# P4-06: task intent still leads (strategies preserved, quick not rigid)
# ---------------------------------------------------------------------------

def test_quick_answer_is_natural_not_a_rigid_cap():
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    assert "not a rigid cap" in strategies
    # The five strategies survive.
    for strat in ("Teaching or explanation", "Coding or implementation", "Debugging",
                  "Discussion or decision", "Quick answer or everyday"):
        assert strat in strategies


# ---------------------------------------------------------------------------
# The refined policy reaches BOTH installation paths
# ---------------------------------------------------------------------------

REFINED_MARKERS = (
    "asks to practise or be tested",                 # conditional quiz
    "do not require a visual for every shaped idea",  # selective visuals
    "never append the offer by default",              # no automatic demo
    "Scope a product-specific implementation",        # epistemic scoping
)


def test_refined_policy_ships_in_the_claude_ai_zip(tmp_path):
    out, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        skill_md = archive.read("socialized/SKILL.md").decode("utf-8")
    assert "op:" not in skill_md
    normalized = norm(skill_md)
    for marker in REFINED_MARKERS:
        assert marker in normalized, marker
    for phrase in FORBIDDEN:
        assert norm(phrase) not in normalized, phrase


def test_refined_policy_ships_in_the_plugin():
    skill_md = read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md")
    assert "op:" not in skill_md
    normalized = norm(skill_md)
    for marker in REFINED_MARKERS:
        assert marker in normalized, marker
    for phrase in FORBIDDEN:
        assert norm(phrase) not in normalized, phrase


def test_reusable_policy_modules_track_phase_4(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        assert "Version 0.3.0" in read(comms / name), name
    controls = norm(read(comms / "controls.md"))
    assert "asks to practise or be tested" in controls
    assert "offered when" not in controls or "only when asked or clearly useful" in controls
