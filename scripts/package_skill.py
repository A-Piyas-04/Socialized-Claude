"""Package the skill as an installable ZIP.

    python scripts/package_skill.py                    # dist/socialized.zip (production, all operations)
    python scripts/package_skill.py --variant seq      # dist/ablation/socialized--seq.zip
    python scripts/package_skill.py --all-variants     # every ablation variant
    python scripts/package_skill.py --check            # is the committed ZIP current? writes nothing

The ZIP contains one top-level folder, socialized/, with SKILL.md directly
inside it, as claude.ai expects. Operation markers are removed. Ablation variants
also drop the blocks of disabled operations. Every variant keeps the same name and
description, so automatic activation sees identical metadata.

Builds are deterministic: the same source produces a byte-identical ZIP, which is
what makes --check possible: it renders the skill in memory and compares the result
against the committed archive and manifest without touching either.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402
from validate_skill import print_report, validate_dir, validate_zip  # noqa: E402

ZIP_DATE = (1980, 1, 1, 0, 0, 0)
# zipfile defaults ZipInfo.create_system to 0 on Windows and 3 elsewhere, which puts a
# different "version made by" host byte in every header. Pinning it keeps a rebuild
# byte-identical on any platform, so the --check drift gates mean the same thing in CI.
ZIP_CREATE_SYSTEM = 0
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}


def render_files(skill_dir: Path, enabled: frozenset[str]) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    for path in lib.iter_skill_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        if path.name in lib.FORBIDDEN_FILE_NAMES or set(Path(rel).parts) & lib.FORBIDDEN_DIR_NAMES:
            continue
        data = path.read_bytes()
        if path.suffix in TEXT_SUFFIXES:
            text = data.decode("utf-8").replace("\r\n", "\n")
            text = lib.render_markers(text, enabled)
            if not text.endswith("\n"):
                text += "\n"
            data = text.encode("utf-8")
        rendered[rel] = data
    return rendered


def zip_bytes(files: dict[str, bytes], root: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        folder = zipfile.ZipInfo(f"{root}/", date_time=ZIP_DATE)
        folder.create_system = ZIP_CREATE_SYSTEM
        folder.external_attr = (0o40755 << 16) | 0x10
        archive.writestr(folder, b"")
        for rel in sorted(files):
            info = zipfile.ZipInfo(f"{root}/{rel}", date_time=ZIP_DATE)
            info.create_system = ZIP_CREATE_SYSTEM
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[rel])
    return buffer.getvalue()


def write_zip(files: dict[str, bytes], root: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(zip_bytes(files, root))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_path(out_path: Path) -> Path:
    return out_path.with_suffix(".manifest.json")


def render_manifest(manifest: dict) -> bytes:
    return (json.dumps(manifest, indent=2) + "\n").encode("utf-8")


def read_zip_members(archive: zipfile.ZipFile) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    for info in archive.infolist():
        if info.filename.endswith("/"):
            continue
        members[info.filename] = archive.read(info)
    return members


def out_path_for(variant: str, root: str, out_dir: Path = lib.DIST_DIR) -> Path:
    if variant == "full":
        return out_dir / f"{root}.zip"
    return out_dir / "ablation" / f"{root}--{variant}.zip"


def manifest_for(variant: str, root: str, out_path: Path, files: dict[str, bytes],
                 archive: bytes) -> dict:
    return {
        "skill": root,
        "variant": variant,
        "enabled_operations": sorted(lib.VARIANTS[variant]),
        "zip": out_path.name,
        "zip_sha256": sha256(archive),
        "files": {rel: sha256(data) for rel, data in sorted(files.items())},
    }


def build(variant: str, *, skill_dir: Path = lib.SKILL_DIR, out_dir: Path = lib.DIST_DIR,
          surface: str = "claude-ai") -> tuple[Path, lib.Report]:
    if variant not in lib.VARIANTS:
        raise ValueError(f"unknown variant '{variant}'; choose from {sorted(lib.VARIANTS)}")
    source_report = validate_dir(skill_dir, surface=surface)
    report = lib.Report([f"source: {m}" for m in source_report.errors],
                        [f"source: {m}" for m in source_report.warnings])
    if not report.ok:
        return Path(), report

    enabled = lib.VARIANTS[variant]
    files = render_files(skill_dir, enabled)
    root = skill_dir.name
    if variant == "full":
        out_path = out_dir / f"{root}.zip"
    else:
        out_path = out_dir / "ablation" / f"{root}--{variant}.zip"
    write_zip(files, root, out_path)

    zip_report = validate_zip(out_path, surface=surface, expected_name=root)
    report.errors.extend(f"zip: {m}" for m in zip_report.errors)
    report.warnings.extend(f"zip: {m}" for m in zip_report.warnings)
    manifest = {
        "skill": root,
        "variant": variant,
        "enabled_operations": sorted(enabled),
        "zip": out_path.name,
        "zip_sha256": sha256(out_path.read_bytes()),
        "files": {rel: sha256(data) for rel, data in sorted(files.items())},
    }
    out_path.with_suffix(".manifest.json").write_bytes((json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    return out_path, report


# ---------------------------------------------------------------------------
# Drift check: read-only. Renders the skill in memory and compares.
# ---------------------------------------------------------------------------

def check_variant(variant: str, *, skill_dir: Path = lib.SKILL_DIR,
                  out_dir: Path = lib.DIST_DIR, required: bool = True) -> list[str]:
    """Problems with the committed ZIP and manifest for one variant. Writes nothing.

    With required=False an absent archive is not a problem: only the production ZIP is
    committed, while dist/ablation/ is ignored and rebuilt on demand. An ablation ZIP
    that *is* present is still checked for drift.
    """
    if variant not in lib.VARIANTS:
        return [f"unknown variant '{variant}'"]

    source = validate_dir(skill_dir, surface="claude-ai")
    if not source.ok:
        return [f"skill source does not validate: {m}" for m in source.errors]

    root = skill_dir.name
    files = render_files(skill_dir, lib.VARIANTS[variant])
    expected = {f"{root}/{rel}": data for rel, data in files.items()}
    out_path = out_path_for(variant, root, out_dir)
    archive_bytes = zip_bytes(files, root)

    problems: list[str] = []
    if not out_path.is_file():
        if not required:
            return []
        return [f"{_display(out_path)} is missing; run package_skill.py to build it"]

    committed = out_path.read_bytes()
    try:
        with zipfile.ZipFile(io.BytesIO(committed)) as archive:
            if archive.testzip() is not None:
                return [f"{_display(out_path)} is corrupt"]
            members = read_zip_members(archive)
    except zipfile.BadZipFile as exc:
        return [f"{_display(out_path)} is not a readable ZIP: {exc}"]

    for name in sorted(members):
        reason = lib.unsafe_path_reason(name)
        if reason:
            problems.append(f"{_display(out_path)}: unsafe member '{name}' ({reason})")
        elif not name.startswith(f"{root}/"):
            problems.append(f"{_display(out_path)}: member '{name}' is outside the {root}/ root")

    for name in sorted(set(expected) - set(members)):
        problems.append(f"{_display(out_path)}: missing {name}")
    for name in sorted(set(members) - set(expected)):
        problems.append(f"{_display(out_path)}: unexpected {name}")
    for name in sorted(set(expected) & set(members)):
        if members[name] != expected[name]:
            problems.append(f"{_display(out_path)}: {name} differs from the canonical skill")

    if not problems and committed != archive_bytes:
        problems.append(f"{_display(out_path)} is stale: the same source now builds different bytes")

    problems.extend(check_manifest(variant, root, out_path, files, archive_bytes, committed))
    return problems


def check_manifest(variant: str, root: str, out_path: Path, files: dict[str, bytes],
                   archive_bytes: bytes, committed: bytes) -> list[str]:
    path = manifest_path(out_path)
    if not path.is_file():
        return [f"{_display(path)} is missing"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"{_display(path)} is not readable JSON: {exc}"]

    expected = manifest_for(variant, root, out_path, files, archive_bytes)
    problems: list[str] = []
    for key in ("skill", "variant", "zip", "enabled_operations"):
        if manifest.get(key) != expected[key]:
            problems.append(f"{_display(path)}: {key} is {manifest.get(key)!r}, expected {expected[key]!r}")
    if manifest.get("zip_sha256") != sha256(committed):
        problems.append(f"{_display(path)}: zip_sha256 does not match the committed archive")
    recorded = manifest.get("files")
    if not isinstance(recorded, dict):
        problems.append(f"{_display(path)}: files is not an object")
    else:
        for rel in sorted(set(expected["files"]) - set(recorded)):
            problems.append(f"{_display(path)}: files is missing {rel}")
        for rel in sorted(set(recorded) - set(expected["files"])):
            problems.append(f"{_display(path)}: files records an unexpected {rel}")
        for rel in sorted(set(expected["files"]) & set(recorded)):
            if recorded[rel] != expected["files"][rel]:
                problems.append(f"{_display(path)}: sha256 for {rel} is stale")
    return problems


def check(variants: list[str], *, skill_dir: Path = lib.SKILL_DIR,
          out_dir: Path = lib.DIST_DIR) -> list[str]:
    problems: list[str] = []
    for variant in variants:
        problems.extend(check_variant(variant, skill_dir=skill_dir, out_dir=out_dir,
                                      required=variant == "full"))
    return problems


def _display(path: Path) -> str:
    try:
        return path.relative_to(lib.REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the skill ZIP.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--variant", default="full", choices=sorted(lib.VARIANTS))
    group.add_argument("--all-variants", action="store_true")
    parser.add_argument("--skill-dir", default=str(lib.SKILL_DIR))
    parser.add_argument("--out-dir", default=str(lib.DIST_DIR))
    parser.add_argument("--check", action="store_true",
                        help="report drift between the source and the committed ZIP; write nothing")
    args = parser.parse_args(argv)

    variants = sorted(lib.VARIANTS) if args.all_variants else [args.variant]

    if args.check:
        problems = check(variants, skill_dir=Path(args.skill_dir), out_dir=Path(args.out_dir))
        if problems:
            print("Committed skill package is out of date:")
            for problem in problems:
                print(f"  - {problem}")
            print("Rebuild with: python scripts/package_skill.py")
            return 1
        label = "every variant" if args.all_variants else f"variant={args.variant}"
        print(f"Committed skill package is in sync with the canonical skill ({label}).")
        return 0

    failed = False
    for variant in variants:
        out_path, report = build(variant, skill_dir=Path(args.skill_dir), out_dir=Path(args.out_dir))
        print_report(out_path if out_path.name else Path(args.skill_dir), report)
        if not report.ok:
            failed = True
            continue
        digest = sha256(out_path.read_bytes())
        print(f"Built {out_path} (variant={variant}, sha256={digest[:16]}...)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
