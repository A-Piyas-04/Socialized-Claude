"""Communication policy invariants (policy 0.9.0, plugin 0.10.0).

This file replaces five round-specific suites — test_refinement_policy.py (Phase 4),
test_visual_restoration.py (Phase 4C), test_communication_recovery.py (v0.5.0),
test_communication_experience.py (v0.6.0) and test_communication_priority.py (v0.7.0).
Each of those pinned the exact wording its own round had just written, so the next
round could only add text beside it; by v0.7.0 the suite was the mechanism keeping
the instruction count rising. See docs/COMMUNICATION_SIMPLIFICATION_AUDIT.md §4 for
the inventory of what each dropped assertion covered and where its behaviour is now
asserted.

Section A was amended on 2026-10-29 by an owner instruction that reverses part of the
simplification: short paragraphs, bullets, emoji points, spacious layout and plain
language are now an always-on house style. Two assertions there are inverted on purpose
and say so in their docstrings. The audit section 8 records the reversal.

What is tested here is what should hold whatever the current wording is:

  A. The house style holds, and no other quota returns
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

# Thresholds that shipped between Phase 4C and v0.7.0 and made the model count output
# elements instead of judging the content. The simplification removed them; they stay
# removed. One cap survives by owner decision, asserted separately below.
COUNTING_RULES = (
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


def test_the_removed_counting_rules_stay_removed():
    for name, text in {"SKILL.md": skill_source(),
                       **{f"references/{p.name}": read(p)
                          for p in (lib.SKILL_DIR / "references").glob("*.md")}}.items():
        low = norm(text).lower()
        for rule in COUNTING_RULES:
            assert rule not in low, f"{name} still counts: {rule!r}"


def test_the_house_style_is_stated_once_up_front_and_always_on():
    """Owner instruction, 2026-10-29: short paragraphs, bullets, emoji points, spacing
    and plain language hold in every substantive reply. This replaces the
    simplification's "nothing here is a quota" preamble, which read as making these
    optional too. See the audit section 8.
    """
    text = skill_source()
    house = section(text, "## House style: always on")
    joined = norm(house)
    assert "standing instruction, not a preference to weigh" in joined
    for rule in ("Short paragraphs", "Bullets over prose", "An emoji point on each bullet",
                 "Spacious layout", "Simple words, simple sentences"):
        assert rule in joined, rule
    assert "Only an explicit request lifts one" in joined
    assert "stands until the person changes it" in joined
    assert text.index("## House style") < text.index("## Operation:")
    assert "never decides that a figure must exist" in joined


def test_the_paragraph_cap_is_the_one_intended_threshold():
    import structural_metrics as sm
    house = norm(section(skill_source(), "## House style: always on"))
    assert "Two or three sentences, never more" in house
    block = norm(op_block(skill_source(), "presentation"))
    assert "Hold every paragraph to two or three sentences" in block
    assert "unless the person explicitly asks for long paragraphs" in block
    # The linter measures the same rule, so drift is observable on a sampled answer.
    assert sm.DENSE_SENTENCES == 4 and sm.DENSE_PARAGRAPH_WORDS == 55


def test_bullets_are_the_default_form_for_multi_point_passages():
    block = norm(op_block(skill_source(), "presentation"))
    assert "Reach for a list whenever a passage carries more than one point" in block
    assert "Keep prose for a single chain of reasoning" in block
    assert "one idea and one emoji point" in block
    assert "blank line between every paragraph, list, table, figure" in block


def test_content_forms_stay_conditional():
    """The house style governs layout. Whether an answer needs a table, a diagram, an
    example or a takeaway at all is still decided by the content (audit section 8)."""
    text = norm(skill_source()).lower()
    for mandate in ("number the headings", "every answer must", "every section must",
                    "every response must", "must contain a table", "must contain a diagram",
                    "end every", "always end with"):
        assert mandate not in text, mandate


def test_emoji_points_are_the_default_on_bullets_and_key_headings():
    """Inverted on purpose, 2026-10-29. The simplification had just returned icons from a
    default to an option, because a default on key headings is the formatting mandate the
    simplification brief section 5 rules out. The owner then asked for an emoji point on
    each bullet as the house style. A direct owner instruction outranks that brief, and
    the audit section 8 records the reversal and what it costs. Restore the optional
    wording only on a new owner decision, not to satisfy section 5.
    """
    block = norm(op_block(skill_source(), "visual"))
    assert "Open every bullet and key heading with a meaning-matched icon" in block
    # Still a signal, not a bullet character.
    assert "Use the same icon for the same kind of thing all through one answer" in block
    assert "Drop the icon rather than pick one that does not match" in block
    # The exclusions keeping icons out of machine-readable and formal text survive.
    for excluded in ("code", "identifiers", "commands", "JSON", "logs", "file paths",
                     "formal or legal writing", "one-line reply"):
        assert excluded in block, excluded
    for icon in ("🧠", "⚙️", "🗄️", "🔄", "📊",
                 "💡", "🛡️", "✅", "❌", "⚠️",
                 "📡", "🔌"):
        assert icon in block, icon
    assert "references/emoji-palette.md" in block


def test_the_emoji_palette_reference_ships_and_is_reachable():
    palette = lib.SKILL_DIR / "references" / "emoji-palette.md"
    assert palette.is_file()
    text = read(palette)
    assert "references/emoji-palette.md" in skill_source()
    assert lib.has_contents_section(text), "a reference over 100 lines needs a Contents section"
    # The one rule that makes an icon a signal rather than decoration.
    assert "the same icon means" in norm(text)
    for group in ("Core concepts", "Mechanism, process and flow", "Data and storage",
                  "Network, services and messaging", "Code, build and tooling",
                  "Time, speed and scale", "Problems, risk and security", "Status marks"):
        assert group in text, group


def test_colour_is_the_three_techniques_that_actually_render():
    """Markdown has no text colour. The skill must not promise what a renderer cannot do."""
    block = norm(op_block(skill_source(), "visual"))
    assert "Markdown carries no text colour" in block
    for technique in ("`diff` fence", "`classDef`", "🟢"):
        assert technique in block, technique
    palette = norm(read(lib.SKILL_DIR / "references" / "emoji-palette.md"))
    assert "Markdown has **no text colour**" in palette


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
        assert "Version 0.9.0" in text, name
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
    """It grew one line per round through v0.6.0; v0.7.0 and the simplification shrank
    it to seven. The house style added two (paragraph length and icon matching) and
    removed one, so the ceiling is nine. It is a brake on the per-round growth that made
    Step 3 a checklist, not a target."""
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


def test_plain_language_names_the_substitutions_to_make():
    """Owner instruction: simple sentences and simple grammar, kept at all cost. A rule
    that only says "write simply" is satisfiable by writing exactly as before, so the
    rule names the swaps."""
    plain = norm(op_block(skill_source(), "plain"))
    assert "Keep the sentence to one clause, or two when the second is short" in plain
    for swap in ('"use" not "utilise"', '"in order to"', '"has the ability to"'):
        assert swap in plain, swap
    assert "Cut a phrase where a word will do" in plain
    # Step 3 asks for the swap too, folded into the final register check rather than
    # added as an eleventh line.
    assert "no formal phrase" in norm(step_3(skill_source()))


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


def test_activation_stays_inside_its_recorded_ceiling():
    """The simplification took activation below the Phase 4 baseline (5966). The owner's
    house style put it back above, because the always-on paragraph, bullet, emoji-point,
    spacing and plain-language rules have to sit in SKILL.md to be always on. The full
    emoji catalogue went to references/emoji-palette.md, which costs nothing until read.
    The ceiling in scripts/token_budgets.json is the gate; the baseline comparison is
    reported, not asserted. Audit section 8.
    """
    report = tb.build_report(tb.HeuristicCounter(), tb.load_budgets(), tb.load_baseline())
    activation = next(r for r in report["components"] if r["id"] == "activation")
    ceiling = tb.load_budgets()["activation"]["max"]
    assert ceiling is not None
    assert activation["tokens"] <= ceiling
    # The house style must be inside the 5,000-token compaction re-attach window.
    skill = skill_source()
    counter = tb.HeuristicCounter()
    assert counter.count(skill.split("## House style", 1)[0]) < 1000
