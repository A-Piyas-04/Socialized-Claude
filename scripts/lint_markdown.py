"""Renderer-safety linter for a markdown response: finds markdown that renders broken.

    python scripts/lint_markdown.py response.md             # human-readable
    python scripts/lint_markdown.py response.md --json      # machine-readable
    type response.md | python scripts/lint_markdown.py -    # stdin

Exit status is 1 when any break is found, 0 otherwise.

Break codes (each reported with the 1-based line where it starts):

  unclosed_fence         a fenced block still open at the end of the text
  nested_fence           inside a fence, an opening fence of the same character, at least as wide,
                         with an info string; its own closing fence will close the outer block early
  table_pipe_mismatch    a table row whose cell count (split on unescaped pipes) differs from the
                         header's
  wide_table             a table with more than four columns
  broken_table_separator a pipe row followed by a separator row whose pipes are escaped (\\|), so no
                         table renders at all
  mermaid_label          in a Mermaid flowchart, a node or edge label holding ( ) " [ ] { } or an arrow
  heading_jump           a heading more than one level below the previous heading
  emoji_outside_palette  outside code: an emoji in U+1F000-U+1FAFF that is not in the status legend
                         or references/emoji-palette.md, a joiner (U+200D), a flag letter, or a keycap

Symbols in U+2600-U+27BF (such as a check mark) render as text glyphs everywhere and are not checked.

This checks only the text it is given. It cannot watch a live conversation, and a response that
passes can still be wrong or badly explained.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import structural_metrics as sm  # noqa: E402

DISCLAIMER = ("Renderer-safety checks on the text given, not a quality score. It cannot watch a live "
              "conversation, and a response that passes can still be wrong.")

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:\s|$)")
MERMAID_FLOW_RE = re.compile(r"^\s*(flowchart|graph)\b")
MERMAID_SKIP_RE = re.compile(r"^\s*(classDef|class|style|subgraph|end|direction|%%|click|linkStyle)\b")
NODE_RE = re.compile(r"[A-Za-z0-9_]+(\[\[|\[\(|\(\(|\(\[|\{\{|\[/|\[\\|\[|\(|\{|>)")
EDGE_LABEL_RE = re.compile(r"\|([^|]*)\|")
CLOSERS = {"[[": ("]]",), "[(": (")]",), "((": ("))",), "([": ("])",), "{{": ("}}",),
           "[/": ("/]", "\\]"), "[\\": ("\\]", "/]"), "[": ("]",), "(": (")",), "{": ("}",), ">": ("]",)}
LABEL_BAD_CHARS = frozenset('()"[]{}')
ARROW_RE = re.compile(r"-->|->|==>")
UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


@dataclass
class Break:
    code: str
    line: int
    detail: str


@dataclass
class Fence:
    char: str
    width: int
    line: int
    info: str


def table_cells(row: str) -> list[str]:
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return UNESCAPED_PIPE_RE.split(s)


def bad_label(label: str) -> bool:
    return bool(LABEL_BAD_CHARS & set(label)) or ARROW_RE.search(label) is not None


def node_labels(line: str) -> list[str]:
    labels = []
    pos = 0
    while match := NODE_RE.search(line, pos):
        start = match.end()
        ends = [i for i in (line.find(c, start) for c in CLOSERS[match.group(1)]) if i >= 0]
        if not ends:
            labels.append(line[start:])
            break
        labels.append(line[start:min(ends)])
        pos = min(ends) + 1
    return labels


def mermaid_breaks(body: list[tuple[int, str]]) -> list[Break]:
    content = [(n, text) for n, text in body if text.strip()]
    if not content or not MERMAID_FLOW_RE.match(content[0][1]):
        return []
    breaks = []
    for n, text in content[1:]:
        if MERMAID_SKIP_RE.match(text):
            continue
        edges = EDGE_LABEL_RE.findall(text)
        nodes = node_labels(EDGE_LABEL_RE.sub(" ", text))
        bad = next((label for label in edges + nodes if bad_label(label)), None)
        if bad is not None:
            breaks.append(Break("mermaid_label", n, f"label {bad.strip()!r} has a bracket, quote, or arrow"))
    return breaks


def emoji_break(line: str, n: int) -> Break | None:
    for c in sm.INLINE_CODE_RE.sub("", line):
        if c == "\u200d":
            return Break("emoji_outside_palette", n, "a joiner glues two emoji into one")
        if c == "\u20e3":
            return Break("emoji_outside_palette", n, "a keycap sequence")
        if "\U0001F1E6" <= c <= "\U0001F1FF":
            return Break("emoji_outside_palette", n, "a flag letter")
        if "\U0001F000" <= c <= "\U0001FAFF" and c not in sm.NAV_ICONS and c not in sm.LEGEND:
            return Break("emoji_outside_palette", n, f"U+{ord(c):04X} is not in the palette")
    return None


def check(markdown: str) -> list[Break]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    breaks: list[Break] = []
    fence: Fence | None = None
    mermaid: list[tuple[int, str]] = []
    prev_level = 0
    i = 0
    while i < len(lines):
        line, n = lines[i], i + 1
        match = FENCE_RE.match(line)
        if fence:
            if match and match.group(1)[0] == fence.char and len(match.group(1)) >= fence.width:
                if not match.group(2).strip():
                    if fence.info == "mermaid":
                        breaks.extend(mermaid_breaks(mermaid))
                    fence, mermaid = None, []
                    i += 1
                    continue
                breaks.append(Break("nested_fence", n, f"an inner fence as wide as the outer one (line {fence.line})"))
            elif fence.info == "mermaid":
                mermaid.append((n, line))
            i += 1
            continue
        if match:
            info = match.group(2).strip()
            fence = Fence(match.group(1)[0], len(match.group(1)), n, info.split()[0].lower() if info else "")
            i += 1
            continue
        if found := emoji_break(line, n):
            breaks.append(found)
        if heading := HEADING_RE.match(line):
            level = len(heading.group(1))
            if prev_level and level > prev_level + 1:
                breaks.append(Break("heading_jump", n, f"level {prev_level} straight to level {level}"))
            prev_level = level
        elif line.strip().startswith("|") and i + 1 < len(lines) and sm.TABLE_SEP_RE.match(lines[i + 1]):
            width = len(table_cells(line))
            if width > sm.TABLE_MAX_COLUMNS:
                breaks.append(Break("wide_table", n, f"{width} columns; keep it to {sm.TABLE_MAX_COLUMNS}"))
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                if found := emoji_break(lines[i], i + 1):
                    breaks.append(found)
                cells = len(table_cells(lines[i]))
                if cells != width:
                    breaks.append(Break("table_pipe_mismatch", i + 1, f"{cells} cells under a {width}-cell header"))
                i += 1
            continue
        elif (line.strip().startswith("|") and i + 1 < len(lines) and "\\|" in lines[i + 1]
              and sm.TABLE_SEP_RE.match(lines[i + 1].replace("\\|", "|"))):
            breaks.append(Break("broken_table_separator", i + 2, "escaped pipes in the separator row; no table renders"))
        i += 1
    if fence:
        breaks.append(Break("unclosed_fence", fence.line, "this fence never closes"))
    return breaks


def render(breaks: list[Break]) -> str:
    lines = [f"line {b.line}: {b.code} ({b.detail})" for b in breaks] or ["no breaks found"]
    lines.append(f"({DISCLAIMER})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Renderer-safety linter for a markdown response.\n" + DISCLAIMER,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="response file, or - for stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    breaks = check(text)
    if args.json:
        print(json.dumps({"breaks": [asdict(b) for b in breaks], "disclaimer": DISCLAIMER}, indent=2))
    else:
        print(render(breaks))
    return 1 if breaks else 0


if __name__ == "__main__":
    sys.exit(main())
