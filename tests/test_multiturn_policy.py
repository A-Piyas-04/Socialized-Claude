"""Phase 3: tests for the multi-turn (across-turns) policy that actually ships.

These assert the policy is present in the *loaded* SKILL.md and in both installed
artifacts (the claude.ai skill ZIP and the generated plugin), that it extends the
existing op:repair / op:persistence rather than adding a parallel engine, and that
the established operation contract is untouched.

Offline string and structure assertions cannot show that Claude behaves this way
in real conversations. See docs/phase-3-implementation.md.
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


def rendered(variant: str = "full") -> str:
    _, body, _ = lib.split_frontmatter(skill_source())
    return lib.render_markers(body, lib.VARIANTS[variant])


def op_blocks(text: str, op: str) -> list[str]:
    """Every marker block for `op`, in order."""
    return re.findall(rf"<!-- op:{op} -->\n(.*?)<!-- /op:{op} -->", text, re.DOTALL)


def operation_block(text: str, op: str, heading: str) -> str:
    """The one marker block for `op` that carries its operation heading."""
    matching = [b for b in op_blocks(text, op) if heading in b]
    assert len(matching) == 1, f"expected exactly one {op} block with {heading!r}"
    return matching[0]


def norm(text: str) -> str:
    """Collapse whitespace so assertions survive prose line-wrapping."""
    return re.sub(r"\s+", " ", text)


def bullets(block: str) -> list[str]:
    """Top-level '- ' bullets, with wrapped continuation lines joined back on."""
    out: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            out.append(stripped[2:])
        elif out and stripped and not stripped.startswith(("#", "<!--")):
            out[-1] += " " + stripped
    return [norm(b) for b in out]


def section(text: str, heading: str) -> str:
    """Text from `heading` up to the next top-level heading."""
    assert heading in text, heading
    after = text.split(heading, 1)[1]
    return after.split("\n## ", 1)[0]


# ---------------------------------------------------------------------------
# The established contract is untouched
# ---------------------------------------------------------------------------

def test_operation_contract_is_unchanged():
    """Phase 3 adds no new operation, marker, or variant."""
    assert len(lib.OPERATIONS) == 12
    assert len(lib.VARIANTS) == 15
    assert "repair" in lib.OPERATIONS and "persistence" in lib.OPERATIONS
    assert lib.check_markers(skill_source(), "SKILL.md").errors == []


def test_repair_and_persistence_operations_stay_unique():
    """Each has exactly one operation heading -- no duplicate competing rule set."""
    text = skill_source()
    for heading in ("## Operation: Repair after a clarification or correction",
                    "## Operation: Keep standing instructions in force"):
        assert text.count(heading) == 1, heading


def test_no_parallel_conversation_engine_operation():
    """Multi-turn guidance must live in existing sections, not a new operation."""
    headings = re.findall(r"^## Operation: .*$", skill_source(), re.MULTILINE)
    assert len(headings) == len(lib.OPERATIONS)
    for h in headings:
        assert not re.search(r"(?i)\b(conversation|follow-up|multi-turn|memory)\b", h), h


# ---------------------------------------------------------------------------
# A. Reading what a follow-up is doing (always-on, silent)
# ---------------------------------------------------------------------------

def test_step1_reads_the_conversation_so_far():
    step1 = section(skill_source(), "## Step 1: Read the request (silently)")
    numbered = re.findall(r"^\d+\. \*\*(.+?)\.\*\*", step1, re.MULTILINE)
    assert len(numbered) == 5, f"Step 1 should have 5 items, found {numbered}"
    assert "conversation so far" in numbered[-1].lower()
    item = norm(step1.split("5. **")[1])
    # Purposes a follow-up can have (brief §3A).
    for purpose in ("new task", "confusion", "correction", "feedback", "preference"):
        assert purpose in item.lower(), purpose
    # Silent planning, not a printed label or a classifier.
    assert "silently" in item.lower()


def test_followup_reading_is_always_on():
    """It must survive even the zero-operation build, so it is never ablated away."""
    core = rendered("core")
    assert "conversation so far" in core
    assert "op:" not in core
    # ...while the repair operation's own rules are correctly gated.
    assert "## Operation: Repair after a clarification or correction" not in core


# ---------------------------------------------------------------------------
# B + D. Repair the exact gap; correction vs disagreement
# ---------------------------------------------------------------------------

def test_repair_operation_covers_the_multiturn_cases():
    block = operation_block(skill_source(), "repair",
                            "## Operation: Repair after a clarification or correction")
    rules = bullets(block)
    assert len(rules) >= 7, rules
    # Every rule names an action (project skill-text rule).
    for rule in rules:
        assert not rule.lower().startswith(("do not", "don't", "never", "avoid")), rule
    joined = " ".join(rules).lower()
    # Non-repetition: answer the unresolved part, drop what is settled or demonstrated.
    assert "unresolved part" in joined
    assert "shown they know" in joined
    # Change the explanatory method, not just the wording.
    assert "change the method" in joined and "wording" in joined
    # Disagreement: evaluate before conceding, and fix dependent conclusions.
    assert "before conceding" in joined
    assert "whatever followed from it" in joined
    # The four correction cases remain distinguished.
    assert "earlier reading of it was wrong" in joined   # misread request
    assert "reports a mistake" in joined                  # real error


# ---------------------------------------------------------------------------
# C + F. Preference scope across turns
# ---------------------------------------------------------------------------

def test_persistence_operation_scopes_one_reply_preferences():
    block = operation_block(skill_source(), "persistence",
                            "## Operation: Keep standing instructions in force")
    joined = " ".join(bullets(block)).lower()
    # Standing preferences still carry forward...
    assert "until" in joined and "change it" in joined
    # ...and a one-reply instruction must not become permanent.
    assert "for this answer" in joined and "this time" in joined
    assert "that reply alone" in joined


# ---------------------------------------------------------------------------
# E. Continuity only within real capabilities
# ---------------------------------------------------------------------------

def test_accuracy_rules_bound_conversation_continuity():
    accuracy = section(skill_source(), "## Accuracy rules (always apply)")
    joined = norm(accuracy).lower()
    assert "only to what this conversation contains" in joined
    assert "missing" in joined
    # No claim of durable or cross-session memory.
    assert "recall another conversation" in joined


# ---------------------------------------------------------------------------
# Pre-send checks
# ---------------------------------------------------------------------------

def test_step3_checks_non_repetition_and_preference_scope():
    step3 = section(skill_source(), "## Step 3: Check before sending (silently)")
    repair_checks = norm(" ".join(op_blocks(step3, "repair"))).lower()
    assert "unresolved part" in repair_checks
    assert "already settled" in repair_checks
    persistence_checks = norm(" ".join(op_blocks(step3, "persistence"))).lower()
    assert "one-reply instruction" in persistence_checks


# ---------------------------------------------------------------------------
# The policy reaches BOTH installation paths
# ---------------------------------------------------------------------------

MULTITURN_MARKERS = (
    "conversation so far",          # Step 1.5: read the follow-up
    "unresolved part",              # repair the exact gap
    "change the method",            # switch explanatory method
    "for this answer",              # one-reply preference scope
    "only to what this conversation contains",  # continuity honesty
)


def test_multiturn_policy_ships_in_the_claude_ai_skill_zip(tmp_path):
    out, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        skill_md = archive.read("socialized/SKILL.md").decode("utf-8")
    assert "op:" not in skill_md
    for marker in MULTITURN_MARKERS:
        assert marker in norm(skill_md), marker


def test_multiturn_policy_ships_in_the_plugin():
    skill_md = read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md")
    assert "op:" not in skill_md
    for marker in MULTITURN_MARKERS:
        assert marker in norm(skill_md), marker


def test_both_installation_paths_stay_in_sync():
    assert bp.check() == [], "run: python scripts/build_plugin.py"


# ---------------------------------------------------------------------------
# Versioned policy modules (source of truth)
# ---------------------------------------------------------------------------

def test_policy_modules_are_versioned_and_document_across_turns(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        assert "Version 0.4.0" in read(comms / name), name
    strategies = read(comms / "strategies.md")
    across = norm(section(strategies, "## Across turns")).lower()
    # The brief's required cases are documented in the reusable module.
    for concept in ("confusion", "correction", "preference", "code", "missing"):
        assert concept in across, concept
    # No false claim of durable memory.
    assert "no stored memory" in across
    # Follow-ups get no mandatory closing structure (Phase 4 stays Phase 4).
    assert "no mandatory takeaway" in across


def test_plugin_version_tracks_the_shipped_content(repo_root):
    import json
    meta = json.loads(read(repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"))
    # Bumped because `version` pins installs: new skill content needs a new version.
    assert meta["version"] == "0.5.0"
    assert not meta["version"].startswith("1.")
