"""Validate a Claude skill directory or packaged skill ZIP.

    python scripts/validate_skill.py                      # validate skill/socialized
    python scripts/validate_skill.py path/to/skill-dir
    python scripts/validate_skill.py dist/socialized.zip
    python scripts/validate_skill.py --surface api ...    # relax the claude.ai 200-char description limit

Exit status is 0 when there are no errors. Warnings never fail validation unless
--strict is given. Offline structural validation does not show that Claude will
load or follow the skill.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402


def read_text(path: Path, report: lib.Report, label: str) -> str | None:
    try:
        raw = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        report.error(f"{label}: not valid UTF-8")
        return None
    if "\r\n" in raw:
        report.warn(f"{label}: CRLF line endings (the packager normalizes to LF)")
    return raw.replace("\r\n", "\n")


def validate_dir(skill_dir: Path, *, surface: str = "claude-ai", packaged: bool = False) -> lib.Report:
    report = lib.Report()
    if not skill_dir.is_dir():
        report.error(f"skill directory not found: {skill_dir}")
        return report

    entries = {p.name for p in skill_dir.iterdir()}
    if "SKILL.md" not in entries:
        others = sorted(n for n in entries if n.lower() == "skill.md")
        hint = f" (found {others[0]}; the file must be named exactly SKILL.md)" if others else ""
        report.error(f"SKILL.md not found in {skill_dir}{hint}")
        return report

    files = lib.iter_skill_files(skill_dir)
    rel_files = {p.relative_to(skill_dir).as_posix() for p in files}
    texts: dict[str, str] = {}

    for path in files:
        rel = path.relative_to(skill_dir).as_posix()
        parts = set(PurePosixPath(rel).parts)
        if path.name in lib.FORBIDDEN_FILE_NAMES or parts & lib.FORBIDDEN_DIR_NAMES:
            report.error(f"{rel}: file must not be shipped in a skill")
            continue
        if path.suffix in lib.EXECUTABLE_SUFFIXES:
            report.warn(f"{rel}: executable script in skill; V0 is instructions-only")
        if path.suffix in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js"}:
            text = read_text(path, report, rel)
            if text is None:
                continue
            texts[rel] = text
            report.extend(lib.scan_text(text, rel))
            markers = lib.check_markers(text, rel)
            report.extend(markers)
            if packaged and any(lib.parse_marker(line) for line in text.splitlines()):
                report.error(f"{rel}: packaged file still contains operation markers")

    skill_text = texts.get("SKILL.md")
    if skill_text is None:
        return report

    meta, body, fm_error = lib.split_frontmatter(skill_text)
    if fm_error:
        report.error(f"SKILL.md: {fm_error}")
        return report
    report.extend(lib.check_frontmatter(meta, folder_name=skill_dir.name, surface=surface))

    body_lines = body.count("\n") + 1
    if body_lines > lib.BODY_MAX_LINES:
        report.error(f"SKILL.md body is {body_lines} lines; keep it under {lib.BODY_MAX_LINES}")

    linked_from_skill = set()
    for ref in sorted(lib.referenced_paths(body)):
        reason = lib.unsafe_path_reason(ref)
        if reason:
            report.error(f"SKILL.md references '{ref}', which {reason}")
            continue
        normalized = PurePosixPath(ref).as_posix()
        if normalized not in rel_files:
            report.error(f"SKILL.md references missing file '{ref}'")
        linked_from_skill.add(normalized)

    for rel, text in texts.items():
        if rel == "SKILL.md":
            continue
        if rel not in linked_from_skill:
            report.warn(f"{rel}: not referenced from SKILL.md (Claude may never read it)")
        if text.count("\n") + 1 > lib.TOC_REQUIRED_OVER_LINES and not lib.has_contents_section(text):
            report.warn(f"{rel}: longer than {lib.TOC_REQUIRED_OVER_LINES} lines without a Contents section")
        for ref in sorted(lib.referenced_paths(text)):
            reason = lib.unsafe_path_reason(ref)
            if reason:
                report.error(f"{rel} references '{ref}', which {reason}")
                continue
            if ref == "SKILL.md":
                continue
            candidates = {PurePosixPath(ref).as_posix(), (PurePosixPath(rel).parent / ref).as_posix()}
            if not candidates & rel_files:
                report.error(f"{rel} references missing file '{ref}'")
            else:
                report.warn(f"{rel} references '{ref}'; keep references one level deep from SKILL.md")
    return report


def validate_zip(zip_path: Path, *, surface: str = "claude-ai", expected_name: str | None = None) -> lib.Report:
    report = lib.Report()
    if not zip_path.is_file():
        report.error(f"ZIP not found: {zip_path}")
        return report
    try:
        archive = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        report.error(f"{zip_path.name}: not a valid ZIP file")
        return report
    with archive, tempfile.TemporaryDirectory() as tmp:
        names = archive.namelist()
        bad = [n for n in names if lib.unsafe_path_reason(n.rstrip("/")) or n.startswith("/")]
        if bad:
            report.error(f"{zip_path.name}: unsafe entry paths {bad}")
            return report
        roots = {PurePosixPath(n).parts[0] for n in names if n.strip("/")}
        if len(roots) != 1:
            report.error(f"{zip_path.name}: must contain exactly one top-level skill folder, found {sorted(roots)}")
            return report
        root = roots.pop()
        if any(PurePosixPath(n).parts == (root,) and not n.endswith("/") for n in names):
            report.error(f"{zip_path.name}: top-level entry '{root}' must be a folder, not a file")
            return report
        if f"{root}/SKILL.md" not in names:
            report.error(f"{zip_path.name}: '{root}/SKILL.md' missing (SKILL.md must sit directly inside the skill folder)")
        if expected_name and root != expected_name:
            report.error(f"{zip_path.name}: top-level folder is '{root}', expected '{expected_name}'")
        archive.extractall(tmp)
        report.extend(validate_dir(Path(tmp) / root, surface=surface, packaged=True))
    return report


def print_report(target: Path, report: lib.Report) -> None:
    for message in report.errors:
        print(f"ERROR   {message}")
    for message in report.warnings:
        print(f"WARNING {message}")
    status = "PASSED" if report.ok else "FAILED"
    print(f"{status}: {target} ({len(report.errors)} error(s), {len(report.warnings)} warning(s))")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a skill directory or ZIP.")
    parser.add_argument("target", nargs="?", default=str(lib.SKILL_DIR))
    parser.add_argument("--surface", choices=["claude-ai", "api"], default="claude-ai",
                        help="claude-ai enforces the 200-character description limit")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if target.suffix.lower() == ".zip":
        report = validate_zip(target, surface=args.surface)
    else:
        report = validate_dir(target, surface=args.surface)
    print_report(target, report)
    if not report.ok or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
