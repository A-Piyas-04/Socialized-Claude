"""One command that runs every offline check this repository can run for free.

    python scripts/verify.py                      # the mandatory offline gate
    python scripts/verify.py --with-cli           # also try the optional Claude CLI tier
    python scripts/verify.py --require-cli        # ... and fail if the CLI is unavailable
    python scripts/verify.py --list               # show the checks without running them
    python scripts/verify.py --project-root PATH  # run against a checkout elsewhere

What it establishes: the skill source validates, the committed distributables match
the source, the plugin tree and manifests agree, the local token estimates stay inside
their budgets, and the deterministic policy-contract tests pass.

What it does not establish: that Claude loads the skill, follows it, or explains
anything better. Those are conversational observations, not offline checks. See
`docs/VALIDATION.md` and `docs/LIMITATIONS.md`.

The offline tier needs only Python and the packages in requirements-dev.txt: no
network, no Claude authentication, no model calls. It writes nothing into the
repository; `--check` modes report drift instead of rebuilding, and the run verifies
afterwards that the working tree is unchanged.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


@dataclass(frozen=True)
class Check:
    name: str
    argv: list[str]
    what: str
    tier: str = "offline"
    #: executable that must be on PATH; None means "this interpreter"
    requires: str | None = None


@dataclass
class Result:
    check: Check
    status: str
    detail: str = ""
    output: str = ""


@dataclass
class Suite:
    results: list[Result] = field(default_factory=list)

    @property
    def failed(self) -> list[Result]:
        return [r for r in self.results if r.status == FAIL]

    @property
    def skipped(self) -> list[Result]:
        return [r for r in self.results if r.status == SKIP]


def offline_checks() -> list[Check]:
    """The mandatory tier. Every command here is read-only."""
    return [
        Check("tests", [sys.executable, "-m", "pytest", "-q"],
              "deterministic test suite, including the protected policy contracts"),
        Check("skill-source", [sys.executable, "scripts/validate_skill.py"],
              "canonical skill/socialized/ is a well-formed skill"),
        Check("skill-zip", [sys.executable, "scripts/validate_skill.py", "dist/socialized.zip"],
              "the committed claude.ai ZIP is a well-formed skill"),
        Check("skill-drift", [sys.executable, "scripts/package_skill.py", "--check"],
              "the committed claude.ai ZIP and manifest match the source"),
        Check("plugin-drift", [sys.executable, "scripts/build_plugin.py", "--check"],
              "the generated plugin tree, ZIP and manifest match the source"),
        Check("token-budget", [sys.executable, "scripts/token_budget.py", "--check"],
              "local token estimates stay inside the configured budgets"),
        Check("version-lock", [sys.executable, "scripts/version_lock.py"],
              "the committed packages match the version they were locked under"),
        Check("archive-stats", [sys.executable, "research/recompute_archive_stats.py"],
              "the research archive still reproduces the numbers in EVIDENCE_AUDIT.md"),
    ]


def cli_checks() -> list[Check]:
    """The optional tier. Needs the Claude CLI; never required for a green gate."""
    return [
        Check("cli-plugin", ["claude", "plugin", "validate", "./plugins/socialized"],
              "Claude CLI accepts the generated plugin", tier="cli", requires="claude"),
        Check("cli-marketplace", ["claude", "plugin", "validate", "./.claude-plugin/marketplace.json"],
              "Claude CLI accepts the local marketplace", tier="cli", requires="claude"),
    ]


def shell(argv: list[str]) -> str:
    def quote(part: str) -> str:
        return f'"{part}"' if " " in part else part
    return " ".join(quote(p) for p in argv)


def run_check(check: Check, root: Path, timeout: int) -> Result:
    argv = list(check.argv)
    if check.requires:
        found = shutil.which(check.requires)
        if found is None:
            return Result(check, SKIP, f"{check.requires} is not on PATH")
        argv[0] = found
    try:
        done = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8", errors="replace")
    except OSError as exc:
        if check.requires:
            # Found on PATH but not launchable from here (a shell shim, for instance).
            # Unavailable is not the same as broken, and never the same as passed.
            return Result(check, SKIP, f"{check.requires} is on PATH but could not be launched: {exc}")
        return Result(check, FAIL, f"could not run: {exc}")
    except subprocess.TimeoutExpired:
        return Result(check, FAIL, f"timed out after {timeout}s")
    output = (done.stdout or "") + (done.stderr or "")
    if done.returncode != 0:
        return Result(check, FAIL, f"exit status {done.returncode}", output)
    return Result(check, PASS, "", output)


def git_state(root: Path) -> str | None:
    """`git status --porcelain`, or None when git or a repository is unavailable.

    Read-only: nothing here changes git settings, the index or any file.
    """
    if shutil.which("git") is None:
        return None
    try:
        done = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                              capture_output=True, text=True, timeout=120,
                              encoding="utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    return done.stdout


def tree_unchanged(before: str | None, after: str | None) -> Result:
    check = Check("tree-unchanged", ["git", "status", "--porcelain"],
                  "the checks left the working tree as they found it")
    if before is None or after is None:
        return Result(check, SKIP, "git or a repository is unavailable here")
    if before != after:
        added = sorted(set(after.splitlines()) - set(before.splitlines()))
        listed = "; ".join(added) if added else "see git status"
        return Result(check, FAIL, f"the checks modified the working tree: {listed}")
    return Result(check, PASS)


def resolve_root(given: str | None) -> Path:
    if given:
        root = Path(given).expanduser().resolve()
    else:
        root = Path(__file__).resolve().parents[1]
    if not (root / "scripts" / "verify.py").is_file():
        raise SystemExit(f"{root} does not look like this project: scripts/verify.py is missing. "
                         "Pass --project-root with the repository root.")
    return root


def report(suite: Suite, *, root: Path, verbose: bool) -> None:
    # Subprocess output can carry characters a legacy console cannot encode; a report
    # must never die on one.
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, OSError):  # pragma: no cover - exotic stdout
        pass
    width = max(len(r.check.name) for r in suite.results)
    print()
    for result in suite.results:
        line = f"  {result.status}  {result.check.name.ljust(width)}  {result.check.what}"
        if result.detail:
            line += f" - {result.detail}"
        print(line)
        if result.output and (verbose or result.status == FAIL):
            for out_line in result.output.rstrip().splitlines():
                print(f"        {out_line}")

    passed = sum(1 for r in suite.results if r.status == PASS)
    print(f"\n  {passed} passed, {len(suite.failed)} failed, {len(suite.skipped)} skipped"
          f"  (project root: {root})")
    for result in suite.skipped:
        print(f"  skipped, not passed: {result.check.name} - {result.detail}")
    if suite.failed:
        print("\n  Reproduce the failures:")
        for result in suite.failed:
            print(f"    {shell(result.check.argv)}")
        print("\n  OFFLINE VALIDATION FAILED" if any(r.check.tier == "offline" for r in suite.failed)
              else "\n  OPTIONAL CLI VALIDATION FAILED")
    else:
        label = ("Offline validation passed" if any(r.check.tier == "offline" for r in suite.results)
                 else "Selected checks passed")
        print(f"\n  {label}. Consistency of source, packages, metadata and policy text is")
        print("  what this establishes - not that Claude's answers improved. See docs/VALIDATION.md.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run every offline check for this repository.",
        epilog="Exit status is 0 only when no check failed. Skipped checks are never counted "
               "as passed.")
    parser.add_argument("--project-root", help="repository root (default: the parent of scripts/)")
    parser.add_argument("--with-cli", action="store_true",
                        help="also run the optional Claude CLI checks when the CLI is installed")
    parser.add_argument("--require-cli", action="store_true",
                        help="implies --with-cli, and fails when the CLI is unavailable")
    parser.add_argument("--only", action="append", default=[], metavar="NAME",
                        help="run only these checks (repeatable)")
    parser.add_argument("--list", action="store_true", help="list the checks and exit")
    parser.add_argument("--verbose", action="store_true", help="show output from passing checks too")
    parser.add_argument("--timeout", type=int, default=1800, metavar="SECONDS")
    args = parser.parse_args(argv)

    want_cli = args.with_cli or args.require_cli
    checks = offline_checks() + (cli_checks() if want_cli else [])
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {c.name for c in offline_checks() + cli_checks()}
        if unknown:
            raise SystemExit(f"unknown check(s): {', '.join(sorted(unknown))}")
        checks = [c for c in offline_checks() + cli_checks() if c.name in wanted]

    if args.list:
        for check in checks:
            print(f"  {check.tier:<8} {check.name:<16} {shell(check.argv)}")
        if not want_cli:
            print("\n  The optional Claude CLI tier is hidden; add --with-cli to include it.")
        return 0

    root = resolve_root(args.project_root)
    print(f"Socialized-Claude offline validation ({len(checks)} checks, project root {root})")

    before = git_state(root)
    suite = Suite()
    for check in checks:
        print(f"  ... {check.name}", flush=True)
        result = run_check(check, root, args.timeout)
        if result.status == SKIP and args.require_cli and check.tier == "cli":
            result = Result(check, FAIL, f"{result.detail} (required by --require-cli)")
        suite.results.append(result)
    suite.results.append(tree_unchanged(before, git_state(root)))

    report(suite, root=root, verbose=args.verbose)
    return 1 if suite.failed else 0


if __name__ == "__main__":
    sys.exit(main())
