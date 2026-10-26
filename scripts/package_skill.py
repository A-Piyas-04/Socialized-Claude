"""Package the skill as an installable ZIP.

    python scripts/package_skill.py                    # dist/explanation-lab.zip (production, all operations)
    python scripts/package_skill.py --variant seq      # dist/ablation/explanation-lab--seq.zip
    python scripts/package_skill.py --all-variants     # every ablation variant

The ZIP contains one top-level folder, explanation-lab/, with SKILL.md directly
inside it, as claude.ai expects. Operation markers are removed. Ablation variants
also drop the blocks of disabled operations. Every variant keeps the same name and
description, so automatic activation sees identical metadata.

Builds are deterministic: the same source produces a byte-identical ZIP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402
from validate_skill import print_report, validate_dir, validate_zip  # noqa: E402

ZIP_DATE = (1980, 1, 1, 0, 0, 0)
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


def write_zip(files: dict[str, bytes], root: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        folder = zipfile.ZipInfo(f"{root}/", date_time=ZIP_DATE)
        folder.external_attr = (0o40755 << 16) | 0x10
        archive.writestr(folder, b"")
        for rel in sorted(files):
            info = zipfile.ZipInfo(f"{root}/{rel}", date_time=ZIP_DATE)
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[rel])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the skill ZIP.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--variant", default="full", choices=sorted(lib.VARIANTS))
    group.add_argument("--all-variants", action="store_true")
    parser.add_argument("--skill-dir", default=str(lib.SKILL_DIR))
    parser.add_argument("--out-dir", default=str(lib.DIST_DIR))
    args = parser.parse_args(argv)

    variants = sorted(lib.VARIANTS) if args.all_variants else [args.variant]
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
