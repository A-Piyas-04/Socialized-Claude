"""Gaps the Phase 5 suites left: the public documentation set and the staging command.

These cover failures that would embarrass a release rather than break a build - a licence
claimed before one exists, a documentation file nobody links to, a staging command that could
publish something. They are deliberately few. The existing suites already cover package
hygiene, drift, metadata agreement and broken relative links.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import skilllib as lib
from stage_release import LICENSE_NAMES, blockers, find_license

PUBLIC_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "docs/INSTALLATION.md",
    "docs/USAGE.md",
    "docs/COMPATIBILITY.md",
    "docs/TROUBLESHOOTING.md",
    "docs/LICENSING.md",
    "docs/LIMITATIONS.md",
    "docs/RELEASE_READINESS.md",
)

# Each install path a first-time user might take must be findable from the installation doc.
INSTALL_PATHS = (
    "dist/socialized.zip",
    "dist/socialized-claude-plugin.zip",
    "--plugin-dir",
    "claude plugin marketplace add",
    "claude plugin install socialized@socialized-claude",
    "claude plugin uninstall socialized@socialized-claude",
    "claude plugin update socialized@socialized-claude",
    "~/.claude/skills/socialized/",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def project_markdown(repo_root: Path) -> list[Path]:
    skip = {"research-results-2026-10-26", "temp", "dist", "__pycache__", ".git", "plugins"}
    return [md for md in sorted(repo_root.rglob("*.md"))
            if not set(md.relative_to(repo_root).parts) & skip]


def test_every_public_document_exists(repo_root):
    missing = [name for name in PUBLIC_DOCS if not (repo_root / name).is_file()]
    assert missing == [], f"public documentation missing: {missing}"


def test_readme_links_to_every_public_document(repo_root):
    """A document nobody links to is a document nobody reads."""
    readme = read(repo_root / "README.md")
    targets = {t.split("#")[0] for t in lib.MD_LINK_RE.findall(readme)}
    unlinked = [name for name in PUBLIC_DOCS if name != "README.md" and name not in targets]
    assert unlinked == [], f"README.md does not link to: {unlinked}"


def test_no_open_source_claim_while_no_license_exists(repo_root):
    """The one claim this repository cannot make yet.

    Phrases that assert a licence, as opposed to discussing the open decision. The licensing
    document and this test are allowed to name them.
    """
    if find_license() is not None:
        pytest.skip("a LICENSE file exists; this guard no longer applies")

    claims = re.compile(
        r"(is open source"
        r"|licen[cs]ed under"
        r"|released under the"
        r"|MIT licen[cs]ed"
        r"|under the (MIT|Apache)\b)",
        re.IGNORECASE)
    allowed = {"docs/LICENSING.md", "tests/test_public_release.py"}
    offenders = []
    for md in project_markdown(repo_root):
        rel = md.relative_to(repo_root).as_posix()
        if rel in allowed:
            continue
        for match in claims.finditer(read(md)):
            offenders.append(f"{rel}: {match.group(0)!r}")
    assert offenders == [], (
        "licence claimed while the repository has no LICENSE file: " + "; ".join(offenders))


def test_plugin_manifest_declares_no_license_it_does_not_have(repo_root):
    """`license` in plugin.json ships inside the plugin ZIP, so it must not be aspirational."""
    manifest = json.loads(read(repo_root / "plugins/socialized/.claude-plugin/plugin.json"))
    declared = manifest.get("license")
    if declared:
        assert find_license() is not None, (
            f"plugin.json declares license {declared!r} but no LICENSE file exists at the "
            f"repository root (looked for {', '.join(LICENSE_NAMES)})")


MIT_PERMISSION = ("The above copyright notice and this permission notice shall be included in all\n"
                  "copies or substantial portions of the Software.")


def test_license_is_mit_and_names_the_copyright_holder(repo_root):
    text = read(repo_root / "LICENSE")
    assert text.startswith("MIT License\n\nCopyright (c) 2026 Ahnaf Shahriar Pias\n")
    assert MIT_PERMISSION in text
    assert 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND' in text


def test_declared_license_agrees_everywhere(repo_root):
    """plugin.json ships inside the plugin ZIP; the marketplace entry is what a catalog reads."""
    plugin = json.loads(read(repo_root / "plugins/socialized/.claude-plugin/plugin.json"))
    entry = json.loads(read(repo_root / ".claude-plugin/marketplace.json"))["plugins"][0]
    assert plugin.get("license") == "MIT"
    assert entry.get("license") == plugin["license"]


@pytest.mark.parametrize("rel", ("dist/socialized.zip", "dist/socialized-claude-plugin.zip"))
def test_every_package_ships_the_license(repo_root, rel):
    """MIT's one condition: the notice travels with every copy."""
    with zipfile.ZipFile(repo_root / rel) as archive:
        shipped = archive.read("socialized/LICENSE")
    assert shipped == lib.license_bytes(), f"{rel}: socialized/LICENSE differs from LICENSE"


def test_installed_plugin_tree_carries_the_license(repo_root):
    """A marketplace install copies plugins/socialized/, not the repository root."""
    assert (repo_root / "plugins/socialized/LICENSE").read_bytes() == lib.license_bytes()


def test_installation_doc_covers_every_install_path(repo_root):
    text = read(repo_root / "docs/INSTALLATION.md")
    missing = [path for path in INSTALL_PATHS if path not in text]
    assert missing == [], f"docs/INSTALLATION.md does not document: {missing}"


def test_security_policy_publishes_no_unmonitored_contact(repo_root):
    """A contact address nobody watches is worse than none; the policy says so itself."""
    text = read(repo_root / "SECURITY.md")
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    assert emails == [], f"SECURITY.md publishes an email address: {emails}"
    assert "security/advisories/new" in text, \
        "SECURITY.md must name GitHub private vulnerability reporting as the channel"


def test_license_blocker_tracks_whether_a_license_exists():
    labels = [label for label, _ in blockers("0.5.2")]
    if find_license() is None:
        assert any("LICENSE" in label for label in labels), \
            "stage_release must report the missing licence as a blocker"
    else:
        assert not any("LICENSE" in label for label in labels), \
            "stage_release still reports a licence blocker although LICENSE exists"
    assert any("evaluation" in label.lower() for label in labels), \
        "stage_release must keep reporting that no controlled evaluation exists"


def test_staging_cannot_publish():
    """The staging command has no path to a publish, by construction.

    A reviewer should not have to take that on trust, and a later edit that adds one should
    fail here rather than in a release.
    """
    source = read(lib.REPO_ROOT / "scripts" / "stage_release.py")
    # Calls, not prose: the summary it writes legitimately discusses publishing and uploads.
    forbidden = ('"gh"', "'gh'", "gh release", '"push"', "'push'", '"tag"', "'tag'",
                 "api.github.com", "urllib", "requests")
    found = [token for token in forbidden if token in source]
    assert found == [], f"stage_release.py contains a publishing path: {found}"


def test_staged_digests_match_the_committed_manifests(repo_root):
    """Staging must report the same bytes the build recorded, or it is not reproducible."""
    proc = subprocess.run([sys.executable, "scripts/stage_release.py", "--check"],
                          cwd=repo_root, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    from stage_release import sha256_file
    for manifest_name, zip_name in (
            ("dist/socialized.manifest.json", "dist/socialized.zip"),
            ("dist/socialized-claude-plugin.manifest.json",
             "dist/socialized-claude-plugin.zip")):
        manifest = json.loads(read(repo_root / manifest_name))
        assert sha256_file(repo_root / zip_name) == manifest["zip_sha256"], \
            f"{zip_name} does not match the digest in {manifest_name}"


def test_release_candidate_output_is_not_committed(repo_root):
    """Staged output is build output; a release must not depend on it being in the tree."""
    ignored = read(repo_root / ".gitignore").splitlines()
    assert "dist/release-candidate/" in ignored, \
        "dist/release-candidate/ must stay out of the repository"
