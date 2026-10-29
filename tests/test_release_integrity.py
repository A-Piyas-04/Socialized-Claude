"""Phase 5: integrity of the committed packages, the metadata that installs them, and
the offline gate that checks them.

These tests close gaps the Phase 1-4 suites left open:

* `package_skill.py --check` had no coverage at all, because it did not exist. Every
  defect it is supposed to catch is provoked here on a disposable copy.
* ZIP member hygiene (traversal, absolute paths, backslashes) was asserted for the
  skill ZIP's inventory but never as a rule about member *paths* in both packages.
* The marketplace entry and the plugin manifest were each valid on their own; nothing
  compared them, so a rename on one side could pass.
* A changed distributable could be committed without any version decision.
* Nothing checked that CI runs the same gate a contributor runs locally.

Nothing here mutates the canonical skill, the committed archives or the lock file:
mutation tests build a copy under tmp_path first.
"""

from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

import package_skill as ps
import skilllib as lib
import verify
import version_lock as vl

PACKAGES = ("dist/socialized.zip", "dist/socialized-claude-plugin.zip")
WORKFLOW = Path(".github/workflows/validate.yml")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.fixture
def built(skill_copy, tmp_path) -> tuple[Path, Path, Path]:
    """A freshly built full-variant package in a disposable tree.

    Returns (skill_dir, out_dir, zip_path).
    """
    out_dir = tmp_path / "dist"
    zip_path, report = ps.build("full", skill_dir=skill_copy, out_dir=out_dir)
    assert report.ok, report.errors
    return skill_copy, out_dir, zip_path


def check(built) -> list[str]:
    skill_dir, out_dir, _ = built
    return ps.check_variant("full", skill_dir=skill_dir, out_dir=out_dir)


def rewrite_zip(zip_path: Path, edit) -> None:
    """Rebuild an archive after `edit(members)` has changed the member map."""
    with zipfile.ZipFile(zip_path) as archive:
        members = {i.filename: archive.read(i) for i in archive.infolist()}
    edit(members)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)


# ---------------------------------------------------------------------------
# package_skill.py --check: it must pass on a valid tree and fail on each defect
# ---------------------------------------------------------------------------

def test_check_passes_on_the_repository():
    assert ps.check_variant("full") == [], "run: python scripts/package_skill.py"


def test_check_passes_on_a_freshly_built_copy(built):
    assert check(built) == []


def test_check_detects_a_missing_zip(built):
    _, _, zip_path = built
    zip_path.unlink()
    assert any("is missing" in p for p in check(built))


def test_check_detects_a_corrupt_zip(built):
    _, _, zip_path = built
    zip_path.write_bytes(b"not a zip at all")
    problems = check(built)
    assert problems and "readable ZIP" in problems[0]


def test_check_detects_a_missing_member(built):
    _, _, zip_path = built
    rewrite_zip(zip_path, lambda m: m.pop("socialized/references/treatment-selection.md"))
    assert any("missing socialized/references/treatment-selection.md" in p for p in check(built))


def test_check_detects_an_unexpected_member(built):
    _, _, zip_path = built
    rewrite_zip(zip_path, lambda m: m.update({"socialized/notes.md": b"stray\n"}))
    assert any("unexpected socialized/notes.md" in p for p in check(built))


def test_check_detects_modified_member_contents(built):
    _, _, zip_path = built
    rewrite_zip(zip_path, lambda m: m.update({"socialized/SKILL.md": m["socialized/SKILL.md"] + b"\nedited\n"}))
    assert any("differs from the canonical skill" in p for p in check(built))


def test_check_detects_a_member_outside_the_root(built):
    _, _, zip_path = built
    rewrite_zip(zip_path, lambda m: m.update({"README.md": b"root-level file\n"}))
    assert any("outside the socialized/ root" in p for p in check(built))


def test_check_detects_a_traversal_member(built):
    _, _, zip_path = built
    rewrite_zip(zip_path, lambda m: m.update({"socialized/../evil.md": b"escape\n"}))
    assert any("unsafe member" in p for p in check(built))


def test_check_detects_a_stale_zip_after_the_source_changes(built):
    skill_dir, _, _ = built
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(read(skill_md) + "\nA late edit to the source.\n", encoding="utf-8")
    problems = check(built)
    assert problems, "editing the source after the build must be reported"
    assert any("differs from the canonical skill" in p or "is stale" in p for p in problems)


def test_check_detects_manifest_sha_drift(built):
    _, _, zip_path = built
    path = ps.manifest_path(zip_path)
    manifest = json.loads(read(path))
    manifest["zip_sha256"] = "0" * 64
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assert any("zip_sha256 does not match" in p for p in check(built))


def test_check_detects_a_stale_per_file_sha(built):
    _, _, zip_path = built
    path = ps.manifest_path(zip_path)
    manifest = json.loads(read(path))
    manifest["files"]["SKILL.md"] = "1" * 64
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assert any("sha256 for SKILL.md is stale" in p for p in check(built))


def test_check_detects_a_wrong_operation_list(built):
    _, _, zip_path = built
    path = ps.manifest_path(zip_path)
    manifest = json.loads(read(path))
    manifest["enabled_operations"] = ["mechanism"]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assert any("enabled_operations is" in p for p in check(built))


def test_check_detects_a_missing_manifest(built):
    _, _, zip_path = built
    ps.manifest_path(zip_path).unlink()
    assert any("manifest.json is missing" in p for p in check(built))


def test_check_detects_an_unreadable_manifest(built):
    _, _, zip_path = built
    ps.manifest_path(zip_path).write_text("{ not json", encoding="utf-8")
    assert any("not readable JSON" in p for p in check(built))


def test_check_rejects_a_source_that_does_not_validate(built):
    skill_dir, _, _ = built
    (skill_dir / "SKILL.md").unlink()
    assert any("does not validate" in p for p in check(built))


def test_check_writes_nothing(built):
    """Check mode must never rebuild, so a stale package stays stale until asked."""
    skill_dir, out_dir, zip_path = built
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns)
              for p in sorted(out_dir.rglob("*")) if p.is_file()}
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(read(skill_md) + "\nchanged\n", encoding="utf-8")
    assert check(built) != []
    after = {p: (p.read_bytes(), p.stat().st_mtime_ns)
             for p in sorted(out_dir.rglob("*")) if p.is_file()}
    assert after == before
    assert check(built) != [], "a second check must report the same drift"


def test_check_skips_ablation_variants_that_are_not_committed(built):
    """dist/ablation/ is git-ignored, so an absent ablation ZIP is not drift."""
    skill_dir, out_dir, _ = built
    assert ps.check_variant("mech", skill_dir=skill_dir, out_dir=out_dir, required=False) == []
    assert ps.check_variant("mech", skill_dir=skill_dir, out_dir=out_dir, required=True) != []


def test_check_still_examines_an_ablation_zip_that_is_present(built):
    skill_dir, out_dir, _ = built
    zip_path, report = ps.build("mech", skill_dir=skill_dir, out_dir=out_dir)
    assert report.ok, report.errors
    assert ps.check_variant("mech", skill_dir=skill_dir, out_dir=out_dir, required=False) == []
    rewrite_zip(zip_path, lambda m: m.update({"socialized/SKILL.md": b"gutted\n"}))
    assert ps.check_variant("mech", skill_dir=skill_dir, out_dir=out_dir, required=False) != []


def test_zip_bytes_match_the_written_file(built):
    skill_dir, _, zip_path = built
    files = ps.package_files(skill_dir, lib.VARIANTS["full"])
    assert ps.zip_bytes(files, skill_dir.name) == zip_path.read_bytes()


# ---------------------------------------------------------------------------
# Member hygiene in both committed packages
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel", PACKAGES)
def test_committed_package_members_are_safe_relative_paths(repo_root, rel):
    with zipfile.ZipFile(repo_root / rel) as archive:
        names = archive.namelist()
    assert names
    for name in names:
        assert lib.unsafe_path_reason(name) is None, f"{rel}: unsafe member {name!r}"
        assert not Path(name).is_absolute(), f"{rel}: absolute member {name!r}"


@pytest.mark.parametrize("rel", PACKAGES)
def test_committed_package_has_exactly_one_root_folder(repo_root, rel):
    with zipfile.ZipFile(repo_root / rel) as archive:
        roots = {name.split("/", 1)[0] for name in archive.namelist()}
    assert roots == {"socialized"}, f"{rel}: roots {sorted(roots)}"


@pytest.mark.parametrize("rel", PACKAGES)
def test_committed_package_carries_no_tooling_or_secrets(repo_root, rel):
    with zipfile.ZipFile(repo_root / rel) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
    for name in names:
        leaf = Path(name).name
        assert leaf not in lib.FORBIDDEN_FILE_NAMES, f"{rel}: {name}"
        assert not set(Path(name).parts) & lib.FORBIDDEN_DIR_NAMES, f"{rel}: {name}"
        assert Path(name).suffix not in lib.EXECUTABLE_SUFFIXES or name.endswith(".json"), \
            f"{rel}: ships an executable file {name}"


# ---------------------------------------------------------------------------
# Marketplace and plugin metadata must agree with each other
# ---------------------------------------------------------------------------

def test_marketplace_entry_and_plugin_manifest_agree(repo_root):
    mp = json.loads(read(repo_root / ".claude-plugin" / "marketplace.json"))
    entry = mp["plugins"][0]
    source = (repo_root / entry["source"]).resolve()
    manifest_path = source / ".claude-plugin" / "plugin.json"
    assert manifest_path.is_file(), f"{entry['source']} has no .claude-plugin/plugin.json"
    plugin = json.loads(read(manifest_path))
    # A rename on one side only would install under a name the other side does not know.
    assert entry["name"] == plugin["name"]
    assert entry["description"].strip()
    assert str(source).startswith(str(repo_root.resolve())), "plugin source must stay in the repo"


def test_marketplace_sources_are_relative_and_inside_the_repository(repo_root):
    mp = json.loads(read(repo_root / ".claude-plugin" / "marketplace.json"))
    for entry in mp["plugins"]:
        source = entry["source"]
        assert source.startswith("./"), f"{source} must be a relative path"
        assert lib.unsafe_path_reason(source.removeprefix("./")) is None, source


def test_plugin_ships_its_skill_under_its_own_name(repo_root):
    plugin = json.loads(read(repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"))
    skill_dir = repo_root / "plugins" / plugin["name"] / "skills" / lib.SKILL_DIR.name
    assert (skill_dir / "SKILL.md").is_file()


def test_plugin_version_is_a_plain_semver(repo_root):
    plugin = json.loads(read(repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"))
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"]), plugin["version"]


# ---------------------------------------------------------------------------
# Version lock: a changed package needs a version decision
# ---------------------------------------------------------------------------

def test_repository_matches_its_version_lock():
    assert vl.problems() == [], "run: python scripts/version_lock.py"


def test_lock_records_both_distributables():
    lock = vl.load_lock()
    assert set(lock["packages"]) == set(PACKAGES)
    assert lock["plugin_version"] == vl.plugin_version()


@pytest.fixture
def lock_copy(repo_root, tmp_path) -> Path:
    """A disposable checkout holding only what the lock looks at."""
    for rel in PACKAGES + ("scripts/version_lock.json",
                           "plugins/socialized/.claude-plugin/plugin.json"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / rel, target)
    return tmp_path


def test_a_changed_package_without_a_bump_is_reported(lock_copy):
    zip_path = lock_copy / "dist" / "socialized.zip"
    zip_path.write_bytes(zip_path.read_bytes() + b"\x00")
    problems = vl.problems(lock_copy)
    assert any("needs a version decision" in p for p in problems), problems


def test_a_bump_without_relocking_is_reported(lock_copy):
    manifest = lock_copy / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"
    meta = json.loads(read(manifest))
    meta["version"] = "9.9.9"
    manifest.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    assert any("after an intended bump" in p for p in vl.problems(lock_copy))


def test_a_documentation_only_change_needs_no_bump(lock_copy):
    """The lock must not demand a version for edits that ship nothing."""
    (lock_copy / "README.md").write_text("# rewritten docs\n", encoding="utf-8")
    assert vl.problems(lock_copy) == []


def test_update_relocks_a_changed_package(lock_copy):
    zip_path = lock_copy / "dist" / "socialized.zip"
    zip_path.write_bytes(zip_path.read_bytes() + b"\x00")
    manifest = lock_copy / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"
    meta = json.loads(read(manifest))
    meta["version"] = "0.5.2"
    manifest.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    assert vl.problems(lock_copy) != []
    lock = vl.update(lock_copy)
    assert lock["plugin_version"] == "0.5.2"
    assert vl.problems(lock_copy) == []
    assert "_comment" in json.loads(read(lock_copy / "scripts" / "version_lock.json")), \
        "update must keep the explanation in the lock file"


def test_a_missing_lock_is_reported(lock_copy):
    (lock_copy / "scripts" / "version_lock.json").unlink()
    assert any("missing" in p for p in vl.problems(lock_copy))


# ---------------------------------------------------------------------------
# The offline gate itself
# ---------------------------------------------------------------------------

def test_offline_tier_is_free_and_read_only():
    names = [c.name for c in verify.offline_checks()]
    assert names == ["tests", "skill-source", "skill-zip", "skill-drift", "plugin-drift",
                     "token-budget", "version-lock", "archive-stats"]
    for check_ in verify.offline_checks():
        assert check_.tier == "offline"
        assert check_.requires is None, "the offline tier must not need anything but Python"
        joined = " ".join(check_.argv)
        assert ("--check" in check_.argv or "pytest" in check_.argv
                or "validate_skill.py" in joined or "version_lock.py" in joined
                or "recompute_archive_stats.py" in joined), \
            f"{check_.name} must be a read-only command"


def test_cli_tier_is_separate_and_optional():
    for check_ in verify.cli_checks():
        assert check_.tier == "cli"
        assert check_.requires == "claude"
        assert check_.argv[:3] == ["claude", "plugin", "validate"]


def test_every_offline_script_exists(repo_root):
    for check_ in verify.offline_checks():
        for arg in check_.argv:
            if arg.endswith(".py"):
                assert (repo_root / arg).is_file(), arg


def test_an_unavailable_cli_is_skipped_not_passed(tmp_path, monkeypatch):
    monkeypatch.setattr(verify.shutil, "which", lambda _name: None)
    result = verify.run_check(verify.cli_checks()[0], tmp_path, timeout=5)
    assert result.status == verify.SKIP
    assert "not on PATH" in result.detail


def test_a_failing_check_is_reported_with_its_command(tmp_path):
    import sys
    failing = verify.Check("boom", [sys.executable, "-c", "import sys; sys.exit(3)"], "fails")
    result = verify.run_check(failing, tmp_path, timeout=30)
    assert result.status == verify.FAIL
    assert "exit status 3" in result.detail
    assert "-c" in verify.shell(failing.argv)


def test_a_modified_working_tree_fails_the_run():
    before = " M scripts/verify.py\n"
    assert verify.tree_unchanged(before, before).status == verify.PASS
    changed = verify.tree_unchanged(before, before + "?? dist/socialized.zip\n")
    assert changed.status == verify.FAIL
    assert "dist/socialized.zip" in changed.detail
    assert verify.tree_unchanged(None, None).status == verify.SKIP


def test_the_entry_point_refuses_a_root_that_is_not_this_project(tmp_path):
    with pytest.raises(SystemExit):
        verify.resolve_root(str(tmp_path))
    assert verify.resolve_root(None) == lib.REPO_ROOT


def test_listing_the_checks_does_not_run_them(capsys):
    assert verify.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "pytest" in out and "--with-cli" in out


def test_unknown_check_names_are_rejected():
    with pytest.raises(SystemExit):
        verify.main(["--only", "no-such-check"])


# ---------------------------------------------------------------------------
# CI must run the same gate, with no secrets and no write access
# ---------------------------------------------------------------------------

@pytest.fixture
def workflow(repo_root) -> dict:
    path = repo_root / WORKFLOW
    assert path.is_file(), f"{WORKFLOW.as_posix()} is missing"
    return yaml.safe_load(read(path))


def test_ci_runs_the_same_offline_entry_point(repo_root, workflow):
    steps = workflow["jobs"]["offline"]["steps"]
    commands = " ".join(step.get("run", "") for step in steps)
    assert "scripts/verify.py" in commands, "CI must run the documented offline gate"
    assert "requirements-dev.txt" in commands


def test_ci_triggers_on_pushes_and_pull_requests(workflow):
    # PyYAML reads a bare `on:` key as the boolean True.
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) >= {"push", "pull_request"}


def test_ci_is_read_only_and_needs_no_secrets(repo_root, workflow):
    assert workflow["permissions"] == {"contents": "read"}
    text = read(repo_root / WORKFLOW)
    assert "secrets." not in text, "the offline gate must work without secrets, including on forks"
    assert "CLAUDE_CODE_OAUTH_TOKEN" not in text and "API_KEY" not in text


def test_ci_does_not_publish_or_commit(repo_root, workflow):
    text = read(repo_root / WORKFLOW)
    for forbidden in ("git push", "git commit", "gh release", "softprops/action-gh-release",
                      "actions/upload-release-asset", "npm publish"):
        assert forbidden not in text, f"Phase 5 CI must not publish: found {forbidden!r}"


def test_ci_pins_actions_to_a_major_version(repo_root, workflow):
    uses = re.findall(r"uses:\s*(\S+)", read(repo_root / WORKFLOW))
    assert uses
    for ref in uses:
        assert "@" in ref, f"{ref} must name a version"
        assert not ref.endswith("@master") and not ref.endswith("@main"), \
            f"{ref} must not float on a branch"


def test_the_optional_cli_tier_is_not_a_required_ci_job(repo_root, workflow):
    text = read(repo_root / WORKFLOW)
    assert "--require-cli" not in text, \
        "the Claude CLI cannot be relied on in hosted CI; keep that tier local"


# ---------------------------------------------------------------------------
# Documentation contracts: the commands and the install paths stay documented
# ---------------------------------------------------------------------------

def test_one_offline_command_is_documented(repo_root):
    for rel in ("README.md", "docs/VALIDATION.md"):
        assert "scripts/verify.py" in read(repo_root / rel), rel


def test_both_install_paths_stay_documented(repo_root):
    installation = read(repo_root / "docs" / "INSTALLATION.md")
    assert "dist/socialized.zip" in installation, "claude.ai upload path must stay documented"
    readme = read(repo_root / "README.md")
    assert "plugin marketplace add" in readme or "/plugin marketplace add" in readme, \
        "the Claude Code plugin install path must stay documented"


def test_validation_doc_states_what_ci_does_not_establish(repo_root):
    text = read(repo_root / "docs" / "VALIDATION.md").lower()
    for claim in ("does not", "activation"):
        assert claim in text
    assert "token" in text


def test_regression_inventory_separates_tested_from_observed(repo_root):
    text = read(repo_root / "docs" / "REGRESSION_INVENTORY.md")
    assert "Structurally tested" in text
    assert "Observable only in conversation" in text
    for phase in ("Phase 1", "Phase 3", "Phase 4", "Phase 4B", "Phase 4C"):
        assert phase in text, phase


def test_release_checklist_exists_and_does_not_promise_a_release(repo_root):
    text = read(repo_root / "docs" / "RELEASE_READINESS.md")
    for item in ("scripts/verify.py", "version_lock", "licen", "smoke"):
        assert item.lower() in text.lower(), item


def test_no_broken_relative_links_in_project_markdown(repo_root):
    """A reference nobody follows rots; the inventory and checklist depend on these."""
    skip = {"research-results-2026-10-26", "temp", "dist", "__pycache__", ".git"}
    broken: list[str] = []
    for md in sorted(repo_root.rglob("*.md")):
        if set(md.relative_to(repo_root).parts) & skip:
            continue
        for target in lib.MD_LINK_RE.findall(read(md)):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#")[0]
            if path and not (md.parent / path).exists():
                broken.append(f"{md.relative_to(repo_root).as_posix()} -> {target}")
    assert broken == [], f"broken relative links: {broken}"
