"""Communication priority correction (policy 0.7.0, plugin 0.8.0).

v0.6.0 failed behavioural acceptance on two real CPU cache-coherence answers: dense,
repetitive, no semantic icons, and one MESI diagram drew a read-triggered
Modified -> Invalid transition. The cause was competing instructions, so this
version removed and merged rules rather than adding them; see
docs/communication-priority-correction.md.

These are static assertions over the loaded SKILL.md, its references and both
installed artifacts. They show which instructions ship and which conflicting ones
are gone. They cannot show that answers became easier to understand; behavioural
acceptance stays with the owner.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import build_plugin as bp
import skilllib as lib
import structural_metrics as sm
import token_budget as tb
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


ICONS = ("🧠", "⚙️", "📡", "🗄️", "🔄", "📊", "💡", "🛡️")

# Instructions that each pushed the same mechanism to be told again.
REPETITION_DRIVERS = (
    "repeat this for every later mechanism",
    "in every section that teaches",
    "a state table what each step changes",
    "in the last third as much as the first",
    "keep that support even across the answer",
    "Does the one example reach every teaching section",
    "does every non-obvious mechanism show the obvious approach failing",
)

# Step 3 had 14 checks before this change.
STEP_3_BEFORE = 14


def test_planning_order_lives_once_in_step_2():
    step_2 = norm(section(skill_source(), "## Step 2: Size the answer"))
    assert ("Plan silently in this order: the ideas this reader must leave with, and for a "
            "mechanism a simple concrete run that shows it working") in step_2
    assert "then the forms that show those ideas best, each with its own job" in step_2
    assert "then only the detail this reader needs, after the core is complete" in step_2


def test_repetition_drivers_are_gone():
    text = norm(skill_source())
    for phrase in REPETITION_DRIVERS:
        assert norm(phrase) not in text, phrase


def test_obvious_approach_move_is_stated_once():
    text = skill_source()
    assert text.count("how it fails") == 1
    assert "only when it would otherwise look arbitrary" in norm(op_block(text, "mechanism"))


def test_one_representation_stays_a_preference_not_a_cap():
    visual = norm(op_block(skill_source(), "visual"))
    assert "Prefer one representation per mechanism, and add another whenever it shows something the first cannot" in visual
    for cap in ("at most one", "only one figure", "never more than", "one figure per answer",
                "never draw a second"):
        assert cap not in visual.lower(), cap


def test_visual_grammar_survives():
    visual = op_block(skill_source(), "visual")
    for form in ("A → B → C", "`flowchart`", "`sequenceDiagram`", "one row per moment",
                 "bars of block characters", "`classDef`", "one colour code", "two-column table"):
        assert form in visual, form


def test_icons_are_a_default_preference_with_exclusions():
    visual = norm(op_block(skill_source(), "visual"))
    assert "Prefer meaning-matched icons as navigation in a substantive explanation or technical discussion" in visual
    assert "(not every one)" in visual
    for icon in ICONS:
        assert icon in visual, icon
    assert "Keep icons out of code, identifiers, JSON, logs, formal writing, and short or casual replies" in visual
    for gate in ("never as a template or a requirement", "Add colour, an icon, or a legend"):
        assert gate not in visual, gate


def test_linter_accepts_every_default_icon_on_a_heading():
    for icon in ICONS:
        assert icon.replace("\ufe0f", "") in sm.NAV_ICONS, icon
        answer = f"## {icon} Writes reach storage on eviction\n\nOne sentence. Another sentence.\n"
        assert "emoji_structure" not in sm.decorative_structure_flags(answer), icon


def test_diagram_accuracy_is_always_on(tmp_path):
    """The figure check sits in the accuracy rules, so even the core variant has it."""
    out, report = build_skill("core", out_dir=tmp_path)
    assert report.ok, report.errors
    with zipfile.ZipFile(out) as archive:
        core = norm(archive.read("socialized/SKILL.md").decode("utf-8"))
    accuracy = section(core, "## Accuracy rules (always apply)")
    assert "Hold every arrow, state, transition, and table cell in a figure to the same standard" in accuracy
    assert "label each transition with its trigger and whose action causes it" in accuracy
    assert "draw a simpler figure rather than include a transition you cannot confirm" in accuracy


def test_step_3_got_shorter():
    _, body, _ = lib.split_frontmatter(skill_source())
    rendered = lib.render_markers(body, lib.VARIANTS["full"])
    check = rendered.split("## Step 3: Check before sending (silently)", 1)[1]
    bullets = [line for line in check.splitlines() if line.startswith("- ")]
    assert len(bullets) < STEP_3_BEFORE


def test_activation_shrank():
    """v0.6.0 activation was 6124 heuristic tokens (6085 legacy)."""
    report = tb.build_report(tb.HeuristicCounter(), tb.load_budgets(), tb.load_baseline())
    activation = next(c for c in report["components"] if c["id"] == "activation")
    assert activation["tokens"] < 6124


def test_both_installs_carry_the_same_corrected_skill(repo_root):
    with zipfile.ZipFile(repo_root / "dist" / "socialized.zip") as archive:
        zipped = archive.read("socialized/SKILL.md").decode("utf-8")
    plugin = (bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md").read_bytes().decode("utf-8")
    assert zipped == plugin
    for marker in ("Plan silently in this order", "Prefer meaning-matched icons as navigation",
                   "Give every figure, table, and paragraph a different job"):
        assert marker in norm(zipped), marker
