"""Stage a release candidate locally. Publishes nothing.

    python scripts/stage_release.py            # run the gate, then stage
    python scripts/stage_release.py --check    # report blockers only, stage nothing

It collects the artifacts that a release would carry, their SHA-256 digests, the commit they
were built from, and the blockers that are still open, into one directory a human can read
before deciding anything. It does not tag, push, create a GitHub release, or change any
repository setting, and it has no code path that can.

Staging refuses to run unless `python scripts/verify.py` passes, because a staged candidate
whose packages do not match the source would be worse than no candidate at all. The blockers
it reports do not stop staging: an open licence decision is exactly the thing the summary
exists to put in front of the owner.

Nothing here re-implements verify.py, package_skill.py or build_plugin.py. It shells out to the
gate and reads what the builders already wrote.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skilllib as lib  # noqa: E402

STAGE_DIR = lib.DIST_DIR / "release-candidate"
PLUGIN_MANIFEST = lib.REPO_ROOT / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"
VERSION_LOCK = lib.REPO_ROOT / "scripts" / "version_lock.json"
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")

ARTIFACTS = (
    "dist/socialized.zip",
    "dist/socialized.manifest.json",
    "dist/socialized-claude-plugin.zip",
    "dist/socialized-claude-plugin.manifest.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=lib.REPO_ROOT, capture_output=True,
                             text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return ""
    return out.stdout.strip()


def run_gate() -> tuple[bool, str]:
    """Run the offline gate. Returns (passed, last few lines of its output)."""
    proc = subprocess.run([sys.executable, "scripts/verify.py"], cwd=lib.REPO_ROOT,
                          capture_output=True, text=True)
    tail = [line for line in proc.stdout.splitlines() if line.strip()]
    summary = next((line.strip() for line in reversed(tail) if "passed," in line), "")
    return proc.returncode == 0, summary or (tail[-1].strip() if tail else "no output")


def find_license() -> Path | None:
    for name in LICENSE_NAMES:
        candidate = lib.REPO_ROOT / name
        if candidate.is_file():
            return candidate
    return None


def blockers(version: str) -> list[tuple[str, str]]:
    """Open items that must be decided before this candidate can be published.

    Each is (label, detail). An empty list does not mean "publish"; it means nothing this
    script can see is outstanding.
    """
    found: list[tuple[str, str]] = []

    manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    if find_license() is None and not manifest.get("license"):
        found.append((
            "LICENSE: OWNER DECISION REQUIRED",
            "No LICENSE file and no `license` field in plugin.json. The repository is not open "
            "source, and `claude plugin validate --profile directory` refuses a submission. "
            "See docs/LICENSING.md.",
        ))

    if version.startswith("0."):
        found.append((
            "Version is pre-1.0",
            f"plugin.json declares {version}. Two tests assert the pre-1.0 state; a 1.0 is a "
            "deliberate edit to both, not a side effect of staging.",
        ))

    found.append((
        "claude.ai install paths unverified",
        "Skill upload and plugin upload have not been exercised by this project. They are "
        "documented-compatible only. See docs/COMPATIBILITY.md.",
    ))
    found.append((
        "No controlled evaluation",
        "No comprehension or quality measurement exists. Release notes may not claim that "
        "explanations are better. See docs/LIMITATIONS.md.",
    ))
    return found


def summary_text(version: str, commit: str, dirty: bool, gate: str,
                 digests: dict[str, str], open_items: list[tuple[str, str]]) -> str:
    today = dt.date.today().isoformat()
    lines = [
        f"# Release candidate {version}",
        "",
        "**Staged locally. Nothing has been published, tagged or pushed.**",
        "",
        "| | |",
        "|---|---|",
        f"| Version | `{version}` |",
        f"| Commit | `{commit or 'unknown'}` |",
        f"| Branch | `{git('rev-parse', '--abbrev-ref', 'HEAD') or 'unknown'}` |",
        f"| Working tree | {'**dirty — uncommitted changes**' if dirty else 'clean'} |",
        f"| Staged | {today} |",
        "",
        "## Verification",
        "",
        "`python scripts/verify.py`:",
        "",
        f"```\n{gate}\n```",
        "",
        "This establishes that the skill is well-formed, both packages match the source byte "
        "for byte, the policy contracts are still in the text, and the token budgets hold. It "
        "establishes nothing about the quality of Claude's answers.",
        "",
        "## Artifacts",
        "",
        "| File | SHA-256 |",
        "|---|---|",
    ]
    lines += [f"| `{name}` | `{digest}` |" for name, digest in digests.items()]
    lines += [
        "",
        "Builds are deterministic and platform-independent: rebuild from this commit and the "
        "bytes match. Per-file digests are inside each `.manifest.json`.",
        "",
        "## Open before publishing",
        "",
    ]
    if open_items:
        for label, detail in open_items:
            lines += [f"- **{label}** — {detail}"]
    else:
        lines += ["- Nothing this script can detect."]
    lines += [
        "",
        "## What a release note may not say",
        "",
        "- Not that Claude's answers are measurably better.",
        "- Not a token saving in billed usage; the counts are local estimates.",
        "- Not reliable or universal activation.",
        "- No judge score, win rate or improvement percentage.",
        "",
        "Full checklist: `docs/RELEASE_READINESS.md`.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="report blockers and exit; stage nothing")
    args = parser.parse_args(argv)

    version = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))["version"]
    open_items = blockers(version)

    if args.check:
        print(f"Release candidate {version}: {len(open_items)} open item(s)")
        for label, detail in open_items:
            print(f"  - {label}\n      {detail}")
        print("\nNothing was staged. Run without --check to stage.")
        return 0

    print("Running the offline gate before staging...")
    passed, gate = run_gate()
    if not passed:
        print(f"  {gate}")
        print("\nStaging refused: python scripts/verify.py must pass first.")
        return 1
    print(f"  {gate}")

    missing = [name for name in ARTIFACTS if not (lib.REPO_ROOT / name).is_file()]
    if missing:
        print("Staging refused, missing artifacts: " + ", ".join(missing))
        print("Build them: python scripts/package_skill.py && python scripts/build_plugin.py")
        return 1

    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True)

    digests: dict[str, str] = {}
    for name in ARTIFACTS:
        source = lib.REPO_ROOT / name
        shutil.copy2(source, STAGE_DIR / source.name)
        digests[source.name] = sha256_file(source)

    (STAGE_DIR / "SHA256SUMS.txt").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in digests.items()), encoding="utf-8")

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    (STAGE_DIR / "RELEASE_CANDIDATE.md").write_text(
        summary_text(version, commit, dirty, gate, digests, open_items), encoding="utf-8")

    rel = STAGE_DIR.relative_to(lib.REPO_ROOT).as_posix()
    print(f"\nStaged {len(digests)} artifacts in {rel}/")
    print(f"  Summary: {rel}/RELEASE_CANDIDATE.md")
    print(f"  Digests: {rel}/SHA256SUMS.txt")
    if dirty:
        print("  WARNING: the working tree is dirty; this candidate is not a committed state.")
    print(f"\n{len(open_items)} open item(s) before this could be published:")
    for label, _ in open_items:
        print(f"  - {label}")
    print("\nNothing was published, tagged or pushed. That is a decision for the owner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
