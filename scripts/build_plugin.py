"""Build the Claude Code plugin from the canonical skill.

    python scripts/build_plugin.py            # materialize plugin tree + build dist ZIP
    python scripts/build_plugin.py --check    # verify tree and ZIP are in sync; exit 1 if not

The canonical skill in skill/socialized/ is the single source of truth for the
communication guidance. This script renders it (full variant, markers stripped,
identical to dist/socialized.zip) into the plugin's skill directory so the two
never diverge. plugin.json and .claude-plugin/marketplace.json are hand-written
source-of-truth files and are not generated here.

Source of truth : skill/socialized/ , plugins/socialized/.claude-plugin/plugin.json , LICENSE
Generated        : plugins/socialized/skills/socialized/** , plugins/socialized/LICENSE ,
                   dist/socialized-claude-plugin.zip

Builds are deterministic: the same source produces a byte-identical ZIP.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

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
    files: dict[str, bytes] = {".claude-plugin/plugin.json": manifest_bytes,
                               "LICENSE": lib.license_bytes()}
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


def _display(path: Path) -> str:
    """Repo-relative path for messages, or the bare name if the path is outside the repo."""
    try:
        return path.relative_to(lib.REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def canonical_zip_bytes(files: dict[str, bytes]) -> bytes:
    """The byte-exact archive a fresh deterministic build would produce for `files`."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_zip = Path(tmp) / PLUGIN_ZIP.name
        write_zip(files, PLUGIN_NAME, tmp_zip)
        return tmp_zip.read_bytes()


def read_zip_members(archive: zipfile.ZipFile) -> dict[str, bytes]:
    """Decompressed file members of `archive`, keyed by path relative to the root folder."""
    members: dict[str, bytes] = {}
    for name in archive.namelist():
        if name.endswith("/"):
            continue
        parts = PurePosixPath(name).parts
        members["/".join(parts[1:])] = archive.read(name)
    return members


def check_manifest(zip_raw: bytes, expected: dict[str, bytes]) -> list[str]:
    """Verify the ZIP's sidecar manifest matches the archive and the canonical files."""
    problems: list[str] = []
    manifest_path = PLUGIN_ZIP.with_suffix(".manifest.json")
    rel = _display(manifest_path)
    if not manifest_path.is_file():
        problems.append(f"missing {rel}")
        return problems
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        problems.append(f"{rel}: not valid JSON ({exc})")
        return problems
    if manifest.get("plugin") != PLUGIN_NAME:
        problems.append(f"{rel}: plugin is {manifest.get('plugin')!r}, expected {PLUGIN_NAME!r}")
    if manifest.get("zip") != PLUGIN_ZIP.name:
        problems.append(f"{rel}: zip is {manifest.get('zip')!r}, expected {PLUGIN_ZIP.name!r}")
    if manifest.get("zip_root") != f"{PLUGIN_NAME}/":
        problems.append(f"{rel}: zip_root is {manifest.get('zip_root')!r}, expected {PLUGIN_NAME + '/'!r}")
    if manifest.get("zip_sha256") != sha256(zip_raw):
        problems.append(f"{rel}: zip_sha256 does not match {PLUGIN_ZIP.name}")
    expected_hashes = {r: sha256(d) for r, d in sorted(expected.items())}
    recorded = manifest.get("files")
    if recorded != expected_hashes:
        if not isinstance(recorded, dict):
            problems.append(f"{rel}: files map is missing or malformed")
        else:
            for r in sorted(set(expected_hashes) - set(recorded)):
                problems.append(f"{rel}: no hash recorded for '{r}'")
            for r in sorted(set(recorded) - set(expected_hashes)):
                problems.append(f"{rel}: hash recorded for unexpected file '{r}'")
            for r in sorted(set(expected_hashes) & set(recorded)):
                if recorded[r] != expected_hashes[r]:
                    problems.append(f"{rel}: hash for '{r}' does not match the canonical build")
    return problems


def check_zip(expected: dict[str, bytes]) -> list[str]:
    """Verify the distributable ZIP against the canonical files and its manifest."""
    problems: list[str] = []
    rel = _display(PLUGIN_ZIP)
    if not PLUGIN_ZIP.is_file():
        problems.append(f"missing {rel}")
        return problems
    raw = PLUGIN_ZIP.read_bytes()
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        problems.append(f"{rel}: not a valid ZIP archive")
        return problems
    with archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            problems.append(f"{rel}: corrupt archive entry '{corrupt}'")
            return problems
        names = [n for n in archive.namelist() if n.strip("/")]
        roots = {PurePosixPath(n).parts[0] for n in names}
        if roots != {PLUGIN_NAME}:
            problems.append(
                f"{rel}: archive must have a single root folder '{PLUGIN_NAME}/', found {sorted(roots)}")
            problems.extend(check_manifest(raw, expected))
            return problems
        members = read_zip_members(archive)
    content_problems: list[str] = []
    for r in sorted(set(expected) - set(members)):
        content_problems.append(f"{rel}: missing archived file '{r}'")
    for r in sorted(set(members) - set(expected)):
        content_problems.append(f"{rel}: unexpected archived file '{r}'")
    for r in sorted(set(expected) & set(members)):
        if members[r] != expected[r]:
            content_problems.append(f"{rel}: archived file '{r}' differs from the canonical build")
    problems.extend(content_problems)
    # Byte-for-byte drift (archive metadata: timestamps, permissions, ordering) is only
    # meaningful to flag once the file contents themselves line up.
    if not content_problems and raw != canonical_zip_bytes(expected):
        problems.append(f"{rel}: archive bytes differ from a deterministic rebuild (metadata drift)")
    problems.extend(check_manifest(raw, expected))
    return problems


def check() -> list[str]:
    """Return a list of drift problems; empty means the tree, ZIP and manifest are current."""
    problems: list[str] = []
    files = plugin_files()
    for rel, data in files.items():
        target = PLUGIN_DIR / rel
        if not target.is_file():
            problems.append(f"missing generated file: plugins/{PLUGIN_NAME}/{rel}")
        elif target.read_bytes() != data:
            problems.append(f"stale generated file: plugins/{PLUGIN_NAME}/{rel}")
    problems.extend(check_zip(zip_files(files)))
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
