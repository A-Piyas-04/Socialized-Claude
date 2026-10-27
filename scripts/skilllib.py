"""Shared helpers for validating and packaging the Explanation Lab skill.

Standard library plus PyYAML (the same dependency Anthropic's quick_validate.py uses).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only without PyYAML
    raise SystemExit("PyYAML is required: pip install -r requirements-dev.txt") from exc

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skill" / "explanation-lab"
DIST_DIR = REPO_ROOT / "dist"

OPERATIONS = ("sequencing", "mechanism", "examples", "terms", "presentation")

# Temporary skill variants for ablation runs. "full" is the production build.
VARIANTS: dict[str, frozenset[str]] = {
    "full": frozenset(OPERATIONS),
    "core": frozenset(),
    "seq": frozenset({"sequencing"}),
    "mech": frozenset({"mechanism"}),
    "seq-mech": frozenset({"sequencing", "mechanism"}),
}

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
RESERVED_NAME_WORDS = ("anthropic", "claude")
NAME_MAX = 64
DESCRIPTION_MAX_API = 1024
# The claude.ai Help Center ("How to create custom skills") states 200 characters.
DESCRIPTION_MAX_CLAUDE_AI = 200
BODY_MAX_LINES = 500
TOC_REQUIRED_OVER_LINES = 100

MARKER_RE = re.compile(r"^\s*<!--\s*(/?)op:([a-z,\-]+)\s*-->\s*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\.(?:md|txt|json|py|csv|ya?ml|sh|js))`")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
XML_TAG_RE = re.compile(r"<[^>]+>")

FORBIDDEN_FILE_NAMES = {".env", ".DS_Store", "Thumbs.db"}
FORBIDDEN_DIR_NAMES = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
EXECUTABLE_SUFFIXES = {".py", ".sh", ".js", ".ts", ".ps1", ".bat", ".exe"}

SECRET_PATTERNS = {
    "Anthropic API key": re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}"),
    "OpenAI-style secret key": re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Bearer token": re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    "Credential assignment": re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}

EXTERNAL_INFERENCE_PATTERNS = {
    "Anthropic API endpoint": re.compile(r"api\.anthropic\.com"),
    "OpenAI API endpoint": re.compile(r"api\.openai\.com"),
    "Gemini API endpoint": re.compile(r"generativelanguage\.googleapis\.com"),
    "Provider API key variable": re.compile(r"\b(ANTHROPIC|OPENAI|GEMINI|GOOGLE)_API_KEY\b"),
    "Provider SDK import": re.compile(r"\b(import anthropic|from anthropic import|import openai|from openai import|google\.generativeai)\b"),
    "HTTP client usage": re.compile(r"\b(import requests|urllib\.request|http\.client|fetch\(|curl\s+-)"),
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def extend(self, other: "Report") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter, body, error). Expects LF line endings."""
    if not text.startswith("---"):
        return None, text, "No YAML frontmatter found (file must start with '---')"
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text, "Invalid frontmatter format (missing closing '---')"
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, text[match.end():], f"Invalid YAML in frontmatter: {exc}"
    if not isinstance(data, dict):
        return None, text[match.end():], "Frontmatter must be a YAML mapping"
    return data, text[match.end():], None


def check_frontmatter(meta: dict, *, folder_name: str | None, surface: str) -> Report:
    report = Report()
    unexpected = set(meta) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        report.error(f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}")

    name = meta.get("name")
    if name is None:
        report.error("Missing 'name' in frontmatter")
    elif not isinstance(name, str):
        report.error(f"'name' must be a string, got {type(name).__name__}")
    else:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            report.error(f"name '{name}' must be lowercase letters, digits and single hyphens, "
                         "not starting or ending with a hyphen")
        if len(name) > NAME_MAX:
            report.error(f"name is {len(name)} characters; maximum is {NAME_MAX}")
        for word in RESERVED_NAME_WORDS:
            if word in name:
                report.error(f"name must not contain the reserved word '{word}'")
        if XML_TAG_RE.search(name):
            report.error("name must not contain XML tags")
        if folder_name is not None and folder_name != name:
            report.error(f"skill folder '{folder_name}' must match name '{name}'")

    desc = meta.get("description")
    if desc is None:
        report.error("Missing 'description' in frontmatter")
    elif not isinstance(desc, str):
        report.error(f"'description' must be a string, got {type(desc).__name__}")
    else:
        stripped = desc.strip()
        if not stripped:
            report.error("description must not be empty")
        if "<" in stripped or ">" in stripped:
            report.error("description must not contain angle brackets or XML tags")
        if len(stripped) > DESCRIPTION_MAX_API:
            report.error(f"description is {len(stripped)} characters; API maximum is {DESCRIPTION_MAX_API}")
        if len(stripped) > DESCRIPTION_MAX_CLAUDE_AI:
            message = (f"description is {len(stripped)} characters; claude.ai maximum is "
                       f"{DESCRIPTION_MAX_CLAUDE_AI}")
            if surface == "claude-ai":
                report.error(message)
            else:
                report.warn(message)
        if re.match(r"(?i)^(i|you|we)\b", stripped) or re.search(r"(?i)\b(I can|you can|I will)\b", stripped):
            report.warn("description should be written in the third person")
        if not re.search(r"(?i)\buse (it )?(when|for|if)\b", stripped):
            report.warn("description should say when to use the skill (e.g. 'Use when ...')")
    return report


# ---------------------------------------------------------------------------
# Operation markers (ablation support)
# ---------------------------------------------------------------------------

def parse_marker(line: str) -> tuple[bool, frozenset[str]] | None:
    match = MARKER_RE.match(line)
    if not match:
        return None
    closing = match.group(1) == "/"
    ops = frozenset(op.strip() for op in match.group(2).split(",") if op.strip())
    return closing, ops


def check_markers(text: str, label: str) -> Report:
    report = Report()
    open_ops: frozenset[str] | None = None
    open_line = 0
    for number, line in enumerate(text.splitlines(), start=1):
        if "op:" in line and "<!--" in line and parse_marker(line) is None:
            report.error(f"{label}:{number}: malformed operation marker: {line.strip()}")
            continue
        parsed = parse_marker(line)
        if parsed is None:
            continue
        closing, ops = parsed
        unknown = ops - set(OPERATIONS)
        if unknown:
            report.error(f"{label}:{number}: unknown operation(s) {sorted(unknown)}")
        if not closing:
            if open_ops is not None:
                report.error(f"{label}:{number}: nested operation marker (block opened at line {open_line})")
            open_ops, open_line = ops, number
        else:
            if open_ops is None:
                report.error(f"{label}:{number}: closing marker without an opening marker")
            elif ops != open_ops:
                report.error(f"{label}:{number}: closing marker {sorted(ops)} does not match "
                             f"opening {sorted(open_ops)} at line {open_line}")
            open_ops = None
    if open_ops is not None:
        report.error(f"{label}:{open_line}: operation block is never closed")
    return report


def render_markers(text: str, enabled: frozenset[str]) -> str:
    """Drop blocks whose operations are not all enabled; strip every marker line."""
    out: list[str] = []
    keep = True
    for line in text.split("\n"):
        parsed = parse_marker(line)
        if parsed is None:
            if keep:
                out.append(line)
            continue
        closing, ops = parsed
        keep = True if closing else ops <= enabled
    rendered = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", rendered)


# ---------------------------------------------------------------------------
# References and content scanning
# ---------------------------------------------------------------------------

def strip_code_fences(text: str) -> str:
    kept, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def referenced_paths(text: str) -> set[str]:
    prose = strip_code_fences(text)
    paths = set(BACKTICK_PATH_RE.findall(prose))
    for target in MD_LINK_RE.findall(prose):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        paths.add(target.split("#", 1)[0])
    return {p for p in paths if p}


def unsafe_path_reason(path: str) -> str | None:
    if "\\" in path:
        return "uses a backslash (use forward slashes)"
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        return "is absolute"
    if ".." in PurePosixPath(path).parts:
        return "escapes the skill directory"
    return None


def iter_skill_files(skill_dir: Path) -> list[Path]:
    return sorted(p for p in skill_dir.rglob("*") if p.is_file())


def has_contents_section(text: str) -> bool:
    return re.search(r"(?im)^#{1,3}\s+(contents|table of contents)\s*$", text) is not None


def scan_text(text: str, label: str) -> Report:
    report = Report()
    for kind, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            report.error(f"{label}: possible secret ({kind})")
    for kind, pattern in EXTERNAL_INFERENCE_PATTERNS.items():
        if pattern.search(text):
            report.error(f"{label}: external inference or network dependency ({kind})")
    return report
