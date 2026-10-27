"""Structural descriptors of a markdown response. Pure functions; no model calls, no network.

These describe the FORM of a response only. They are not a comprehension score: a response can
score perfectly on every metric here and still be wrong, and nothing here can tell.

Definitions (all heuristics; the TypeScript port in extension/ must match them exactly):

  blocks       A response is split into units: each heading line, each list item, each table,
               each fenced code block, and each paragraph (consecutive non-blank lines of prose).
  word_count   Whitespace-separated tokens outside fenced code blocks, ignoring markdown markers
               (#, list markers, table pipes and separator rows, ** and __).
  emphasis     Bold spans (**x** or __x__), not counting a bold label that opens a list item
               ("- **Term:** ..."), which is the labelled-list form.
  sentences    Prose in paragraphs and list items split after . ! or ? followed by whitespace.
  answer_first_offset
               Words in the leading units that are headings, stock preambles ("Great question",
               "Sure", "Let me explain", ...), or restatements of the question (>= 50% of the
               sentence's content words appear in the question). Needs the question for the
               restatement test; without it only headings and preambles count.

decorative_structure_flags (each a short code):
  heading_thin          a heading whose section holds fewer than 2 sentences
  table_thin            a table with fewer than 2 data columns besides the first (label) column
  bullets_unconnected   a run of 2+ unordered list items, not a labelled list, in which no item
                        contains a connective (because, so, therefore, which means, if)
  emoji_structure       an emoji opening a heading or list item
  whitespace_padding    4+ prose paragraphs of which at least 75% are a single sentence
  empty_transition      a one-sentence paragraph that only announces what follows ("Let's look
                        at...", "Here's how it works."), followed by prose or a heading
  emphasis_overuse      more than 2 bold spans (labels excluded)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__")
LABEL_RE = re.compile(r"^\s*(\*\*[^*]+\*\*|__[^_]+__)")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+")
CONNECTIVE_RE = re.compile(r"(?i)\b(because|so|therefore|which means|if)\b")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\u2705\u274C\u2714\u2716]")
PREAMBLE_RE = re.compile(
    r"(?i)^(great|good|excellent|interesting) question\b|^(sure|certainly|of course|absolutely)\b|"
    r"^(let me|let's|i'll|i will) (explain|break|walk|look|start|dive)|^here'?s (a|an|the|how|what|why)\b|"
    r"^in this (answer|explanation|response)\b|^to (understand|answer) (this|that|your)\b")
TRANSITION_RE = re.compile(
    r"(?i)^(now,?\s+)?(let's|let me|here's|here is|below|the following|next,|in the next|we'll|we will)\b")
STOPWORDS = frozenset(
    "a an the is are was were be been being of to in on for and or but with as at by from it its this that "
    "these those do does did why how what when where which who whom i you we they he she my your our their "
    "me us them can could would should will just so if than then there here not no yes".split())


@dataclass
class Block:
    kind: str        # heading | bullet | numbered | table | code | paragraph
    text: str        # prose text (markers stripped); raw text for code and tables
    lines: list[str]


def strip_inline(text: str) -> str:
    return re.sub(r"\*\*|__|`", "", text).strip()


def parse_blocks(markdown: str) -> list[Block]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    blocks: list[Block] = []
    para: list[str] = []
    i = 0

    def flush() -> None:
        if para:
            blocks.append(Block("paragraph", strip_inline(" ".join(p.strip() for p in para)), list(para)))
            para.clear()

    while i < len(lines):
        line = lines[i]
        if FENCE_RE.match(line):
            flush()
            fence = [line]
            i += 1
            while i < len(lines) and not FENCE_RE.match(lines[i]):
                fence.append(lines[i])
                i += 1
            if i < len(lines):
                fence.append(lines[i])
            blocks.append(Block("code", "\n".join(fence[1:-1]), fence))
            i += 1
            continue
        if TABLE_ROW_RE.match(line) and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            flush()
            table = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and TABLE_ROW_RE.match(lines[i]):
                table.append(lines[i])
                i += 1
            blocks.append(Block("table", "\n".join(table), table))
            continue
        if not line.strip():
            flush()
        elif match := HEADING_RE.match(line):
            flush()
            blocks.append(Block("heading", strip_inline(match.group(1).rstrip("#").strip()), [line]))
        elif match := BULLET_RE.match(line):
            flush()
            blocks.append(Block("bullet", strip_inline(match.group(1)), [line]))
        elif match := NUMBERED_RE.match(line):
            flush()
            blocks.append(Block("numbered", strip_inline(match.group(1)), [line]))
        elif blocks and blocks[-1].kind in {"bullet", "numbered"} and not para and line.startswith((" ", "\t")):
            blocks[-1].lines.append(line)
            blocks[-1].text = f"{blocks[-1].text} {strip_inline(line)}"
        else:
            para.append(line)
        i += 1
    flush()
    return blocks


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"\S+", text) if re.search(r"[A-Za-z0-9]", w)]


def table_cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def block_words(block: Block) -> int:
    if block.kind == "code":
        return 0
    if block.kind == "table":
        rows = [r for i, r in enumerate(block.lines) if i != 1]
        return sum(len(words(strip_inline(" ".join(table_cells(r))))) for r in rows)
    return len(words(block.text))


def sentences(text: str) -> list[str]:
    return [s for s in (p.strip() for p in SENTENCE_SPLIT_RE.split(text.strip())) if words(s)]


def bold_spans(markdown: str) -> int:
    count = 0
    for block in parse_blocks(markdown):
        if block.kind == "code":
            continue
        raw = "\n".join(block.lines)
        if block.kind in {"bullet", "numbered"}:
            body = BULLET_RE.sub(r"\1", NUMBERED_RE.sub(r"\1", block.lines[0]), count=1)
            label = LABEL_RE.match(body)
            raw = "\n".join([body[label.end():] if label else body, *block.lines[1:]])
        count += len(BOLD_RE.findall(raw))
    return count


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in STOPWORDS and len(w) > 2}


def is_restatement(sentence: str, question: str | None) -> bool:
    if not question:
        return False
    mine = content_words(sentence)
    return bool(mine) and len(mine & content_words(question)) / len(mine) >= 0.5


def answer_first_offset(markdown: str, question: str | None = None) -> int:
    offset = 0
    for block in parse_blocks(markdown):
        if block.kind == "heading":
            offset += len(words(block.text))
            continue
        if block.kind in {"code", "table"}:
            return offset
        for sentence in sentences(block.text):
            if PREAMBLE_RE.search(sentence) or is_restatement(sentence, question):
                offset += len(words(sentence))
            else:
                return offset
    return offset


def is_labelled(block: Block) -> bool:
    body = BULLET_RE.sub(r"\1", block.lines[0], count=1)
    return bool(LABEL_RE.match(body)) or bool(re.match(r"^\s*[^:]{1,40}:\s", block.text))


def decorative_structure_flags(markdown: str) -> list[str]:
    blocks = parse_blocks(markdown)
    flags: list[str] = []
    for i, block in enumerate(blocks):
        if block.kind == "heading":
            section = []
            for later in blocks[i + 1:]:
                if later.kind == "heading":
                    break
                section.append(later)
            n = sum(len(sentences(b.text)) for b in section if b.kind in {"paragraph", "bullet", "numbered"})
            n += sum(2 for b in section if b.kind in {"table", "code"})
            if n < 2:
                flags.append("heading_thin")
        if block.kind == "table":
            rows = [table_cells(r) for j, r in enumerate(block.lines) if j >= 2]
            width = max((len(r) for r in rows), default=0)
            data_cols = sum(1 for c in range(1, width) if any(c < len(r) and r[c] for r in rows))
            if data_cols < 2:
                flags.append("table_thin")
        if block.kind in {"heading", "bullet", "numbered"} and EMOJI_RE.match(
                re.sub(r"^\s*(#{1,6}|[-*+]|\d+[.)])\s+", "", block.lines[0]).lstrip("*_ ")):
            flags.append("emoji_structure")
    run: list[Block] = []
    for block in [*blocks, Block("end", "", [])]:
        if block.kind == "bullet":
            run.append(block)
            continue
        if len(run) >= 2 and not all(is_labelled(b) for b in run) and not any(CONNECTIVE_RE.search(b.text) for b in run):
            flags.append("bullets_unconnected")
        run = []
    paragraphs = [b for b in blocks if b.kind == "paragraph"]
    if len(paragraphs) >= 4 and sum(len(sentences(p.text)) == 1 for p in paragraphs) / len(paragraphs) >= 0.75:
        flags.append("whitespace_padding")
    for i, block in enumerate(blocks[:-1]):
        if (block.kind == "paragraph" and len(sentences(block.text)) == 1 and TRANSITION_RE.match(block.text)
                and blocks[i + 1].kind in {"paragraph", "heading"}):
            flags.append("empty_transition")
    if bold_spans(markdown) > 2:
        flags.append("emphasis_overuse")
    return flags


def metrics(markdown: str, question: str | None = None) -> dict:
    blocks = parse_blocks(markdown)
    counted = [b for b in blocks if b.kind != "code"]
    sizes = [block_words(b) for b in counted]
    prose = [s for b in blocks if b.kind in {"paragraph", "bullet", "numbered"} for s in sentences(b.text)]
    return {
        "word_count": sum(sizes),
        "block_count": len(blocks),
        "mean_block_words": round(sum(sizes) / len(sizes), 2) if sizes else 0.0,
        "max_block_words": max(sizes, default=0),
        "heading_count": sum(b.kind == "heading" for b in blocks),
        "bullet_count": sum(b.kind == "bullet" for b in blocks),
        "numbered_count": sum(b.kind == "numbered" for b in blocks),
        "table_count": sum(b.kind == "table" for b in blocks),
        "code_block_count": sum(b.kind == "code" for b in blocks),
        "emphasis_count": bold_spans(markdown),
        "mean_sentence_words": round(sum(len(words(s)) for s in prose) / len(prose), 2) if prose else 0.0,
        "answer_first_offset": answer_first_offset(markdown, question),
        "decorative_structure_flags": decorative_structure_flags(markdown),
    }
