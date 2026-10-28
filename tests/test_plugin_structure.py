"""Offline structural tests for the Claude Code plugin and the local marketplace.

These do not shell out to the `claude` CLI, so they stay hermetic. The CLI check
(`claude plugin validate ./plugins/socialized`) is a documented manual step whose
result is reported in docs/phase-2-implementation.md.
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import build_plugin as bp
import skilllib as lib
from package_skill import build as build_skill
from package_skill import write_zip


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def zip_texts(zip_path: Path) -> dict[str, str]:
    with zipfile.ZipFile(zip_path) as archive:
        return {n: archive.read(n).decode("utf-8") for n in archive.namelist() if not n.endswith("/")}


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def test_plugin_manifest_is_valid():
    meta = json.loads(read(bp.PLUGIN_MANIFEST))
    assert meta["name"] == "socialized"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"]), "plugin name must be kebab-case"
    # The plugin name must not read as one of Anthropic's own (skill validator's rule, too).
    for reserved in ("claude", "anthropic"):
        assert reserved not in meta["name"]
    # Fields that keep `claude plugin validate` free of warnings.
    assert meta["version"] and meta["description"]
    assert meta["author"]["name"]
    assert meta["displayName"] == "Socialized-Claude"
    # Not claiming a production/v1.0 release in this MVP.
    assert not meta["version"].startswith("1.")


# ---------------------------------------------------------------------------
# Source of truth stays in sync with the generated plugin tree
# ---------------------------------------------------------------------------

def test_plugin_tree_matches_canonical_skill():
    assert bp.check() == [], "run: python scripts/build_plugin.py"


def test_plugin_skill_is_identical_to_the_claude_ai_skill(repo_root, tmp_path):
    """The plugin's skill must be byte-identical to dist/socialized.zip's skill."""
    fresh_skill_zip, report = build_skill("full", out_dir=tmp_path)
    assert report.ok, report.errors
    skill_texts = zip_texts(fresh_skill_zip)
    plugin_root = bp.PLUGIN_DIR
    for rel in ("SKILL.md", "references/explanation-methodology.md",
                "references/treatment-selection.md", "references/explanation-examples.md"):
        plugin_file = plugin_root / "skills" / "socialized" / rel
        assert plugin_file.is_file(), rel
        assert read(plugin_file) == skill_texts[f"socialized/{rel}"], rel


def test_plugin_skill_preserves_operations_and_strips_markers():
    skill_md = read(bp.PLUGIN_DIR / "skills" / "socialized" / "SKILL.md")
    assert "op:" not in skill_md, "operation markers must be stripped in the shipped skill"
    # All 12 explanation operations survive into the plugin skill.
    headings = [
        "## Operation: Order ideas by dependency",
        "## Operation: Explain the mechanism",
        "## Operation: Ground with one running example",
        "## Operation: Introduce terms where they are first needed",
        "## Operation: Write plain sentences",
        "## Operation: Give the answer the shape of its content",
        "## Operation: Show the shape instead of describing it",
        "## Operation: Pitch the answer at the reader's register",
        "## Operation: Repair after a clarification or correction",
        "## Operation: Keep standing instructions in force",
        "## Operation: Report work that was done",
        "## Operation: Close with something to keep",
    ]
    for h in headings:
        assert h in skill_md, h
    assert len(headings) == len(lib.OPERATIONS)
    # The Phase 1 intent section is present.
    assert "## Match the communication strategy to the intent" in skill_md


# ---------------------------------------------------------------------------
# Distributable ZIP
# ---------------------------------------------------------------------------

EXPECTED_ZIP_ENTRIES = {
    "socialized/.claude-plugin/plugin.json",
    "socialized/skills/socialized/SKILL.md",
    "socialized/skills/socialized/references/explanation-examples.md",
    "socialized/skills/socialized/references/explanation-methodology.md",
    "socialized/skills/socialized/references/treatment-selection.md",
}


def _build_zip_to(tmp: Path) -> Path:
    files = bp.zip_files(bp.plugin_files())
    out = tmp / bp.PLUGIN_ZIP.name
    write_zip(files, bp.PLUGIN_NAME, out)
    return out


def test_plugin_zip_structure():
    texts = zip_texts(bp.PLUGIN_ZIP)
    assert set(texts) == EXPECTED_ZIP_ENTRIES
    # Plugin root is one directory down, named for the plugin.
    assert all(name.startswith("socialized/") for name in texts)
    # The maintainer README is not shipped.
    assert not any(name.endswith("README.md") for name in texts)


def test_plugin_zip_excludes_research_and_tooling():
    blob = " ".join(zip_texts(bp.PLUGIN_ZIP))
    for forbidden in ("research", "evaluation", "TEST_CASES", ".py", ".csv"):
        assert forbidden not in blob


def test_committed_plugin_zip_is_current(tmp_path):
    fresh = _build_zip_to(tmp_path)
    assert bp.PLUGIN_ZIP.is_file(), "run: python scripts/build_plugin.py"
    assert bp.PLUGIN_ZIP.read_bytes() == fresh.read_bytes(), \
        "dist/socialized-claude-plugin.zip is stale; run: python scripts/build_plugin.py"


def test_plugin_build_is_deterministic(tmp_path):
    first = _build_zip_to(tmp_path / "a")
    second = _build_zip_to(tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()


def test_plugin_manifest_matches_committed_zip():
    manifest = json.loads(read(bp.PLUGIN_ZIP.with_suffix(".manifest.json")))
    import hashlib
    assert manifest["zip_sha256"] == hashlib.sha256(bp.PLUGIN_ZIP.read_bytes()).hexdigest()
    assert manifest["zip_root"] == "socialized/"


# ---------------------------------------------------------------------------
# Local marketplace
# ---------------------------------------------------------------------------

def test_marketplace_manifest_is_valid(repo_root):
    mp = json.loads(read(repo_root / ".claude-plugin" / "marketplace.json"))
    assert mp["name"] and "/" not in mp["name"] and mp["name"] != "."
    assert mp["owner"]["name"]
    assert isinstance(mp["plugins"], list) and mp["plugins"]
    entry = mp["plugins"][0]
    assert entry["name"] == "socialized"
    assert entry["source"] == "./plugins/socialized"
    assert entry["source"].startswith("./"), "relative plugin source must start with ./"
    assert (repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json").is_file()


# ---------------------------------------------------------------------------
# The original claude.ai skill package is untouched by Phase 2
# ---------------------------------------------------------------------------

def test_original_skill_package_still_intact(repo_root):
    committed = repo_root / "dist" / "socialized.zip"
    assert committed.is_file()
    with zipfile.ZipFile(committed) as archive:
        names = {n for n in archive.namelist() if not n.endswith("/")}
    assert names == {
        "socialized/SKILL.md",
        "socialized/references/explanation-methodology.md",
        "socialized/references/treatment-selection.md",
        "socialized/references/explanation-examples.md",
    }
