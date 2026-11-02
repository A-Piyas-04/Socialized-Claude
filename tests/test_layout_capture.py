"""Phase 5 evidence (docs/SKILL_UPGRADE_PLAN_V2.md): the render probe, the layout prompts, and the
round-2 claude.ai answers kept as a recorded baseline for Phase 10. Nothing here gates the skill text."""

import json
import re
from pathlib import Path

import lint_markdown as lm

REPO = Path(__file__).resolve().parents[1]
EVAL = REPO / "evaluation"
ROUND2 = EVAL / "layout_capture" / "round2"
HEADING_RE = re.compile(r"^(#{1,6})\s", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def heading_levels(markdown: str) -> set[int]:
    prose = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    return {len(m.group(1)) for m in HEADING_RE.finditer(prose)}


def test_render_probe_shows_every_level_and_renders_cleanly():
    probe = read(EVAL / "render_probe.md")
    assert heading_levels(probe) == {1, 2, 3, 4}
    for device in ("**A bold line", "\n---\n", "> A plain blockquote", "> 🙋", "> 🧠", "> 🎯", "> 🧪"):
        assert device in probe, device
    assert lm.check(probe) == []
    assert (EVAL / "layout_capture" / "render_probe-claude-ai.png").is_file()


def test_layout_prompts_are_unique_and_cover_the_capture():
    prompts = json.loads(read(EVAL / "layout_prompts.json"))["prompts"]
    ids = [p["id"] for p in prompts]
    assert len(ids) == len(set(ids))
    for p in prompts:
        assert set(p) >= {"id", "intent", "register", "question"} and p["question"].strip()
    by_id = {p["id"]: p["question"] for p in prompts}
    capture = json.loads(read(ROUND2 / "capture.json"))
    for answer in capture["answers"]:
        assert by_id[answer["prompt_id"]] == answer["prompt"]


def test_round2_capture_files_exist():
    capture = json.loads(read(ROUND2 / "capture.json"))
    assert capture["surface"] == "claude.ai" and capture["build"]["commit"] == "e93f3c0"
    for answer in capture["answers"]:
        assert (ROUND2 / answer["markdown"]).is_file()
        assert answer["screenshots"] and all((ROUND2 / s).is_file() for s in answer["screenshots"])


def test_round2_baseline_is_recorded():
    """V1 on claude.ai: clean markdown, sections at ##, sub-sections at ###, and no # title."""
    replicas, monolith = read(ROUND2 / "replicas.md"), read(ROUND2 / "monolith.md")
    assert lm.check(replicas) == [] and lm.check(monolith) == []
    assert heading_levels(replicas) == {2, 3}
    assert heading_levels(monolith) == {2}
