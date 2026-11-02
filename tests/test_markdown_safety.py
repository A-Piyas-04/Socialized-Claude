"""Renderer-safety linter: each break class is caught, and correct markdown passes."""

import json
from pathlib import Path

import pytest

import lint_markdown as lm
import skilllib as lib

FIXTURES = Path(__file__).parent / "fixtures" / "structural"

BROKEN = {
    "unclosed_fence": ("Intro line.\n\n```python\nprint(1)\n", [3]),
    # The inner closing fence ends the outer block early, so the last fence opens a new, unclosed one.
    "nested_fence": ("Example:\n\n```markdown\n```python\nprint(1)\n```\n```\n", [4, ("unclosed_fence", 7)]),
    "table_pipe_mismatch": ("The table shows it.\n\n| Kind | Cost |\n|---|---|\n| a | b | c |\n", [5]),
    "wide_table": ("The table shows it.\n\n| A | B | C | D | E |\n|---|---|---|---|---|\n| 1 | 2 | 3 | 4 | 5 |\n",
                   [3]),
    "mermaid_label": ("The flow.\n\n```mermaid\nflowchart TD\n  A[Start] --> B[Call f(x)]\n```\n", [5]),
    "heading_jump": ("## Top\n\nText here.\n\n#### Too deep\n\nMore text.\n", [5]),
    "emoji_outside_palette": ("## Setup\n\nThis is done 🎃 now.\n", [3]),
}

CLEAN = """## 🔑 How a cache hit works

A read checks the cache first. The table compares the two paths.

| Path | Cost | Notes |
| --- | --- | --- |
| ✅ hit | low | `a \\| b` escaped |
| ❌ miss | high | goes to memory |

### The flow

The diagram shows the miss path.

```mermaid
flowchart TD
  Read[[Read request]] --> Check{In cache}
  Check -->|yes| Hit[Return line]
  Check -->|no| Miss[Fetch from memory]
  classDef key fill:#cfc
  class Read key
```

**Example: a nested fence**

````markdown
```python
print("inner")
```
````
"""


@pytest.mark.parametrize("code", sorted(BROKEN))
def test_each_break_class_is_caught_at_its_line(code):
    text, expected = BROKEN[code]
    breaks = lm.check(text)
    assert [(b.code, b.line) for b in breaks] == [e if isinstance(e, tuple) else (code, e) for e in expected], breaks


def test_correct_markdown_passes():
    assert lm.check(CLEAN) == []


def test_mermaid_edge_labels_quotes_and_arrows_are_checked():
    edge = "```mermaid\nflowchart LR\n  A -->|call (x)| B\n```\n"
    quoted = "```mermaid\nflowchart LR\n  A[\"Process main\"] --> B\n```\n"
    arrow = "```mermaid\nflowchart LR\n  A[x --> y] --> B\n```\n"
    for text in (edge, quoted, arrow):
        assert [b.code for b in lm.check(text)] == ["mermaid_label"], text


def test_sequence_diagram_text_is_not_label_checked():
    seq = "```mermaid\nsequenceDiagram\n  A->>B: send (x)\n```\n"
    assert lm.check(seq) == []


def test_tilde_fence_holds_backtick_fences_and_a_narrower_inner_fence_is_safe():
    assert lm.check("~~~\n```python\nx\n```\n~~~\n") == []
    assert lm.check("````\n```python\nx\n```\n````\n") == []


def test_emoji_in_code_and_joined_sequences():
    assert lm.check("Use `🎃` in code.\n\n```\n🎃\n```\n") == []
    joined = lm.check("A team 👩\u200d💻 works.\n")
    assert [b.code for b in joined] == ["emoji_outside_palette"]
    assert [b.code for b in lm.check("Flag \U0001F1EF\U0001F1F5 here.\n")] == ["emoji_outside_palette"]
    assert lm.check("A check mark \u2713 is a text glyph.\n") == []


def test_first_heading_may_start_at_any_level():
    assert lm.check("### Start deep\n\nText.\n\n#### Then one more\n\nText.\n") == []


@pytest.mark.parametrize("name", ["prose_two_sentences", "prose_causal_chain", "process_steps",
                                  "comparison_table", "labelled_list", "code_block", "branching_diagram",
                                  "scannable_table", "classed_diagram"])
def test_legitimate_fixtures_have_no_breaks(name):
    assert lm.check((FIXTURES / f"{name}.md").read_text(encoding="utf-8")) == []


def test_the_skill_and_its_references_render():
    for path in lib.iter_skill_files(lib.SKILL_DIR):
        if path.suffix == ".md":
            assert lm.check(path.read_text(encoding="utf-8")) == [], path.name


def test_cli_exit_status_json_and_disclaimer(tmp_path, capsys):
    good = tmp_path / "good.md"
    good.write_text(CLEAN, encoding="utf-8")
    assert lm.main([str(good)]) == 0
    assert "no breaks found" in capsys.readouterr().out
    bad = tmp_path / "bad.md"
    bad.write_text(BROKEN["heading_jump"][0], encoding="utf-8")
    assert lm.main([str(bad), "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data["breaks"] == [{"code": "heading_jump", "line": 5, "detail": "level 2 straight to level 4"}]
    assert "cannot watch a live conversation" in data["disclaimer"]
    with pytest.raises(SystemExit):
        lm.main(["--help"])
    assert "not a quality score" in capsys.readouterr().out
