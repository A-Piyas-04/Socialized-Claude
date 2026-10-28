"""Build the Claude Code plugin from the canonical skill.

    python scripts/build_plugin.py            # materialize plugin tree + build dist ZIP
    python scripts/build_plugin.py --check    # verify tree and ZIP are in sync; exit 1 if not

The canonical skill in skill/socialized/ is the single source of truth for the
communication guidance. This script renders it (full variant, markers stripped,
identical to dist/socialized.zip) into the plugin's skill directory so the two
never diverge. plugin.json and .claude-plugin/marketplace.json are hand-written
source-of-truth files and are not generated here.

Source of truth : skill/socialized/ , plugins/socialized/.claude-plugin/plugin.json
Generated        : plugins/socialized/skills/socialized/**  , dist/socialized-claude-plugin.zip

Builds are deterministic: the same source produces a byte-identical ZIP.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402
from package_skill import render_files, sha256, write_zip  # noqa: E402
from validate_skill import validate_dir  # noqa: E402

PLUGIN_NAME = "socialized"
PLUGIN_DIR = lib.REPO_ROOT / "plugins" / PLUGIN_NAME
PLUGIN_MANIFEST = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
PLUGIN_SKILL_SUBDIR = f"skills/{PLUGIN_NAME}"
PLUGIN_ZIP = lib.DIST_DIR / "socialized-claude-plugin.zip"
# Files that live on disk in the plugin tree but stay out of the distributable ZIP.
DISK_ONLY = {"README.md"}


def plugin_files() -> dict[str, bytes]:
    """Return every file of the plugin, keyed by path relative to the plugin root."""
    manifest_bytes = PLUGIN_MANIFEST.read_bytes()
    files: dict[str, bytes] = {".claude-plugin/plugin.json": manifest_bytes}
    for rel, data in render_files(lib.SKILL_DIR, lib.VARIANTS["full"]).items():
        files[f"{PLUGIN_SKILL_SUBDIR}/{rel}"] = data
    return files


def materialize(files: dict[str, bytes]) -> None:
    for rel, data in files.items():
        target = PLUGIN_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def zip_files(files: dict[str, bytes]) -> dict[str, bytes]:
    return {rel: data for rel, data in files.items()
            if Path(rel).name not in DISK_ONLY}


def build() -> Path:
    report = validate_dir(lib.SKILL_DIR)
    if not report.ok:
        raise SystemExit("canonical skill does not validate:\n  " + "\n  ".join(report.errors))
    files = plugin_files()
    materialize(files)
    zf = zip_files(files)
    write_zip(zf, PLUGIN_NAME, PLUGIN_ZIP)
    manifest = {
        "plugin": PLUGIN_NAME,
        "zip": PLUGIN_ZIP.name,
        "zip_root": f"{PLUGIN_NAME}/",
        "zip_sha256": sha256(PLUGIN_ZIP.read_bytes()),
        "files": {rel: sha256(data) for rel, data in sorted(zf.items())},
    }
    PLUGIN_ZIP.with_suffix(".manifest.json").write_bytes(
        (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    return PLUGIN_ZIP


def check() -> list[str]:
    """Return a list of drift problems; empty means the tree and ZIP are current."""
    problems: list[str] = []
    files = plugin_files()
    for rel, data in files.items():
        target = PLUGIN_DIR / rel
        if not target.is_file():
            problems.append(f"missing generated file: plugins/{PLUGIN_NAME}/{rel}")
        elif target.read_bytes() != data:
            problems.append(f"stale generated file: plugins/{PLUGIN_NAME}/{rel}")
    if not PLUGIN_ZIP.is_file():
        problems.append(f"missing {PLUGIN_ZIP.relative_to(lib.REPO_ROOT).as_posix()}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Socialized-Claude plugin.")
    parser.add_argument("--check", action="store_true",
                        help="verify the plugin tree and ZIP match the canonical skill; exit 1 on drift")
    args = parser.parse_args(argv)
    if args.check:
        problems = check()
        if problems:
            print("Plugin is out of sync with the canonical skill:")
            for p in problems:
                print(f"  - {p}")
            print("Run: python scripts/build_plugin.py")
            return 1
        print("Plugin is in sync with the canonical skill.")
        return 0
    out = build()
    print(f"Built {out} (sha256={sha256(out.read_bytes())[:16]}...)")
    print(f"Materialized plugin tree at {PLUGIN_DIR.relative_to(lib.REPO_ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
