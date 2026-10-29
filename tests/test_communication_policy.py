"""Communication policy invariants (policy 0.8.0, plugin 0.9.0).

This file replaces five round-specific suites — test_refinement_policy.py (Phase 4),
test_visual_restoration.py (Phase 4C), test_communication_recovery.py (v0.5.0),
test_communication_experience.py (v0.6.0) and test_communication_priority.py (v0.7.0).
Each of those pinned the exact wording its own round had just written, so the next
round could only add text beside it; by v0.7.0 the suite was the mechanism keeping
the instruction count rising. See docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md §4 for
the inventory of what each dropped assertion covered and where its behaviour is now
asserted.

What is tested here is what should hold whatever the current wording is:

  A. Nothing is a quota        - no counting rules, no mandatory form
  B. One source per rule       - the modules index the skill, they do not restate it
  C. Rules name actions        - the project's skill-text rule
  D. Behaviour that must survive - accuracy, scope, intent strategies, multi-turn
  E. Both installs agree       - the shipped artifacts carry the source skill

These are static assertions over the loaded SKILL.md, its references, the policy
modules and both installed artifacts. They show which instructions ship. They
cannot show that answers became easier to understand; behavioural acceptance stays
with the owner (docs/COMMUNICATION_BASELINE.md).
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import build_plugin as bp
import skilllib as lib
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


def step_3(text: str) -> str:
    return section(text, "## Step 3: Check before sending (silently)")


def bullets(block: str) -> list[str]:
    return [line.strip()[2:] for line in block.splitlines() if line.strip().startswith("- ")]


def policy_files(repo_root: Path) -> dict[str, str]:
    files = {"SKILL.md": skill_source()}
    for ref in sorted((lib.SKILL_DIR / "references").glob("*.md")):
        files[f"references/{ref.name}"] = read(ref)
    for name in ("core.md", "strategies.md", "controls.md"):
        files[f"communication/{name}"] = read(repo_root / "communication" / name)
    return files


# ---------------------------------------------------------------------------
# A. Nothing is a quota
# ---------------------------------------------------------------------------

# Each of these shipped at some point between Phase 4C and v0.7.0 and made the
# model count output elements instead of judging the content (owner brief §2, §5).
COUNTING_RULES = (
    "four sentences",
    "80 words",
    "25 words",
    "six words",
    "four columns",
    "ten nodes",
    "four words or fewer",
    "four steps or fewer",
    "three or more sentences",
    "at most two per answer",
    "three or more items across two or more dimensions",
)


def test_no_counting_rule_ships_in_the_skill_or_its_references():
    for name, text in {"SKILL.md": skill_source(),
                       **{f"references/{p.name}": read(p)
                          for p in (lib.SKILL_DIR / "references").glob("*.md")}}.items():
        low = norm(text).lower()
        for rule in COUNTING_RULES:
            assert rule not in low, f"{name} still counts: {rule!r}"


def test_the_no_quota_statement_is_made_once_up_front():
    text = skill_source()
    preamble = text.split("## Scope", 1)[0]
    assert "Nothing here is a quota" in preamble
    joined = norm(preamble).lower()
    for form in ("table", "figure", "heading", "icon", "example", "takeaway"):
        assert form in joined, form
    assert joined.count("nothing here is a quota") == 1


# Formatting that must stay conditional: a rule making any of these automatic is
# the overengineering the owner brief §5 rules out.
def test_no_form_is_mandatory():
    text = norm(skill_source()).lower()
    for mandate in ("number the headings", "every answer must", "every section must",
                    "every response must", "must contain a table", "must contain a diagram",
                    "end every", "always end with"):
        assert mandate not in text, mandate


def test_icons_are_optional_not_a_default():
    block = norm(op_block(skill_source(), "visual"))
    assert "Optional, where it genuinely helps" in block
    assert "Neither is ever required" in block
    assert "neither belongs on every heading or every item" in block
    # The v0.6.0/v0.7.0 wordings that made an icon the expected case are gone.
    low = block.lower()
    for driver in ("prefer meaning-matched icons", "are the default on key headings",
                   "by default on the key headings"):
        assert driver not in low, driver
    # The vocabulary itself stays available.
    for icon in ("🧠", "⚙️", "🗄️", "🔄", "📊", "💡", "🛡️", "✅", "❌", "⚠️"):
        assert icon in block, icon


def test_visuals_have_no_quota_and_no_cap():
    block = norm(op_block(skill_source(), "visual"))
    assert "Spend the first figure on the hardest idea" in block
    assert "Leave it out when the prose already makes the relationship plain" in block
    # Neither a per-idea requirement nor a per-answer cap.
    low = block.lower()
    for driver in ("for each such idea", "one per section", "two per answer",
                   "last third", "even across the answer"):
        assert driver not in low, driver


def test_closing_units_stay_conditional():
    block = norm(op_block(skill_source(), "close"))
    assert "only when it" in block                 # takeaway is earned
    assert "asks to practise or be tested" in block  # check question is requested
    assert "Most answers need no closing unit at all" in block
    assert "explain X again, not a prompt for a quiz" in block


def test_artifacts_and_interactive_offers_stay_opt_in():
    block = norm(op_block(skill_source(), "visual"))
    assert "explicitly asks for an artifact" in block
    assert "never append the offer by default" in block
    assert "Keep the reply markdown" in block


# ---------------------------------------------------------------------------
# B. One source per rule
# ---------------------------------------------------------------------------

def test_policy_modules_index_the_skill_rather_than_restating_it(repo_root):
    comms = repo_root / "communication"
    for name in ("core.md", "strategies.md", "controls.md"):
        text = read(comms / name)
        assert "Version 0.8.0" in text, name
        assert "index, not a second copy" in text, name
        # Every module points back at the skill as the source.
        assert "SKILL.md" in text, name


def test_modules_carry_no_rule_wording_the_skill_has_dropped(repo_root):
    """The divergence this round fixed: the modules kept thresholds the skill lost."""
    for name in ("core.md", "strategies.md", "controls.md"):
        low = norm(read(repo_root / "communication" / name)).lower()
        for rule in COUNTING_RULES:
            assert rule not in low, f"communication/{name} still counts: {rule!r}"


def test_the_reference_does_not_repeat_when_each_operation_applies():
    """treatment-selection.md §1 used to restate every operation's trigger from SKILL.md."""
    text = read(lib.SKILL_DIR / "references" / "treatment-selection.md")
    assert "## 1. Resolving conflicts" in text
    assert "Selection defaults" not in text
    assert "does not repeat that" in norm(text)


def test_each_module_and_reference_is_reachable_from_the_skill(repo_root):
    text = skill_source()
    for ref in (lib.SKILL_DIR / "references").glob("*.md"):
        assert f"references/{ref.name}" in text, ref.name


# ---------------------------------------------------------------------------
# C. Rules name actions
# ---------------------------------------------------------------------------

ACTION_OPERATIONS = ("sequencing", "mechanism", "examples", "terms", "plain",
                     "presentation", "visual", "register", "repair", "persistence",
                     "work-report", "close")


def test_every_operation_rule_names_an_action():
    text = skill_source()
    for op in ACTION_OPERATIONS:
        for rule in bullets(op_block(text, op)):
            assert not rule.lower().startswith(("do not", "don't", "never", "avoid")), (op, rule)


def step_3_checks(text: str) -> list[str]:
    """Step 3's bullets, each rejoined from its wrapped lines."""
    checks: list[str] = []
    for line in step_3(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--"):
            continue
        if stripped.startswith("- "):
            checks.append(stripped[2:])
        elif stripped and checks:
            checks[-1] += " " + stripped
    return checks


def test_step_3_asks_questions_about_the_draft_not_about_the_rules():
    checks = step_3_checks(skill_source())
    assert checks, "Step 3 has no checks"
    for check in checks:
        assert "?" in check, check


def test_step_3_stayed_short():
    """It grew one line per round through v0.6.0; v0.7.0 shrank it and this round again."""
    assert len(step_3_checks(skill_source())) <= 9


# ---------------------------------------------------------------------------
# D. Behaviour that must survive the simplification
# ---------------------------------------------------------------------------

def test_accuracy_rules_keep_every_requirement():
    accuracy = norm(section(skill_source(), "## Accuracy rules (always apply)")).lower()
    for requirement in (
        "know to be real",                      # no invented mechanisms or citations
        "keep \"usually\" and \"can\"",         # hedges survive expansion
        "simplify the expression, not the substance",
        "teach the general mechanism first",    # no one system taught as the rule
        "carry no database's or broker's behaviour over to another unchecked",
        "name the settings a guarantee depends on",
        "acknowledgements, durability, failure modes, and consistency",
        "workload, scale, or traffic pattern",
        "once, where it first matters",         # assumptions stated once
        "only when you are confident it exists",  # citations
        "only to what this conversation contains",
        "recall another conversation",
    ):
        assert requirement in accuracy, requirement


def test_diagram_accuracy_is_an_always_on_rule(tmp_path):
    """It must hold in the zero-operation build, so no ablation can remove it."""
    core = lib.render_markers(skill_source(), lib.VARIANTS["core"])
    joined = norm(core).lower()
    assert "label each transition with its trigger" in joined
    assert "whose action causes it" in joined
    assert "draw a simpler figure" in joined


def test_general_claims_get_shown_rather_than_asserted():
    """Owner brief §4: situation -> mechanism -> consequence, as a preference."""
    block = norm(op_block(skill_source(), "examples"))
    assert "complexity, cost, risk, latency, failure" in block
    assert "show it happening once instead of asserting it" in block
    assert "the situation, what the mechanism does, and what the reader is left with" in block
    mechanism_check = norm(" ".join(
        re.findall(r"<!-- op:mechanism -->\n(.*?)<!-- /op:mechanism -->", step_3(skill_source()),
                   re.DOTALL)))
    assert "shown rather than" in mechanism_check


def test_the_five_intent_strategies_keep_their_priorities():
    strategies = norm(section(skill_source(), "## Match the communication strategy to the intent"))
    assert "priorities, not templates" in strategies
    for lead in (
        "lead with the working",                      # coding
        "lead with the likely cause",                  # debugging
        "lead with the recommendation",                # discussion
        "answer directly and",                         # quick
        "build an accurate mental model",              # teaching
    ):
        assert lead in strategies, lead
    # Decisions still argue rather than endorse.
    assert "solves a real problem here" in strategies
    assert "what would make a rejected one worth adopting" in strategies
    # Form follows content in every strategy, not only teaching.
    assert "In every strategy, pick the form from the content" in strategies


def test_scope_keeps_the_skill_out_of_non_teaching_replies():
    scope = norm(section(skill_source(), "## Scope: decide first whether this applies"))
    assert "Answer normally, without the explanation operations" in scope
    assert "apply the skill only to the \"why\", briefly" in scope
    assert "Return a requested deliverable" in scope
    assert "without wrapping it in explanation" in scope


def test_figure_table_and_prose_keep_different_jobs():
    block = norm(op_block(skill_source(), "visual"))
    assert "Give every figure, table, and paragraph a different job" in block
    assert "the text says why and what follows" in block
    assert "Write after a figure only what it cannot show" in block
    # A second representation is allowed when it adds something.
    assert "when it shows something the first cannot" in block


def test_tables_keep_the_verdict_and_move_the_argument_under_the_table():
    block = norm(op_block(skill_source(), "presentation"))
    assert "the verdict in the cell" in block
    assert "a condition, a second reason or an argument in a list under the" in block
    assert "the dimension named in each header" in block


def test_depth_layer_and_hierarchy_survive():
    block = norm(op_block(skill_source(), "presentation"))
    assert "Put the essential point first" in block
    assert "variants, tuning, one system's edge cases" in block
    assert "a reader who skips it still has the whole answer" in block


def test_the_bold_line_contradiction_is_resolved():
    """op:presentation required a bold title line AND forbade bold lines as headings."""
    block = norm(op_block(skill_source(), "presentation"))
    assert "A bold line on its own announcing a section is a heading written wrong" in block
    assert "bold title line" not in block
    assert "name what the block shows in the sentence before it" in block


def test_the_caption_contradiction_is_resolved():
    """op:plain deleted announcing sentences; op:visual required one before each figure."""
    plain = norm(op_block(skill_source(), "plain"))
    assert "carries content and stays" in plain
    visual = norm(op_block(skill_source(), "visual"))
    assert "Say what each figure shows and the one thing to notice" in visual


def test_conversational_register_is_an_instruction_not_only_a_check():
    plain = norm(op_block(skill_source(), "plain"))
    assert "knowledgeable person talking to this reader" in plain
    for banned in ("manufactured enthusiasm", "flattery", "academic throat-clearing"):
        assert banned in plain, banned


def test_multi_turn_operations_survive():
    text = skill_source()
    for op, marker in (("repair", "answer only that gap"),
                       ("persistence", "until they change it"),
                       ("work-report", "what you did not verify")):
        assert marker in norm(op_block(text, op)), op


def test_the_operation_contract_is_unchanged():
    """The 12 operations map to studied treatments and to the ablation variants; the
    simplification cut rule text inside them, not the set (audit §3)."""
    assert len(lib.OPERATIONS) == 12
    assert len(lib.VARIANTS) == 15
    headings = re.findall(r"^## Operation: .+$", skill_source(), re.MULTILINE)
    assert len(headings) == len(lib.OPERATIONS)


# ---------------------------------------------------------------------------
# E. Both installs agree with the source
# ---------------------------------------------------------------------------

def test_the_simplified_skill_ships_in_the_claude_ai_zip(tmp_path):
    out, _ = build_skill("full", out_dir=tmp_path)
    with zipfile.ZipFile(out) as archive:
        shipped = archive.read("socialized/SKILL.md").decode("utf-8")
    assert "op:" not in shipped
    assert shipped == lib.render_markers(skill_source(), lib.VARIANTS["full"])


def test_the_simplified_skill_ships_in_the_plugin():
    shipped = read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md")
    assert "op:" not in shipped
    assert shipped == lib.render_markers(skill_source(), lib.VARIANTS["full"])


def test_both_installs_carry_the_same_skill():
    assert bp.check() == [], "run: python scripts/build_plugin.py"


def test_activation_fell_back_within_the_compaction_relevant_range():
    """The simplification removed text; activation must not have grown doing it."""
    report = tb.build_report(tb.HeuristicCounter(), tb.load_budgets(), tb.load_baseline())
    activation = next(r for r in report["components"] if r["id"] == "activation")
    assert activation["baseline"] is not None
    assert activation["tokens"] < activation["baseline"], (
        "the simplification is expected to leave activation below the Phase 4 baseline")
    ceiling = tb.load_budgets()["activation"]["max"]
    assert activation["tokens"] <= ceiling
