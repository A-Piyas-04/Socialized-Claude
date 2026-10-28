"""Change control for the two installable packages.

    python scripts/version_lock.py            # report; exit 1 when the lock is out of date
    python scripts/version_lock.py --update   # record the current packages and version

`version` in the plugin manifest is what an installed copy pins itself to, so a changed
package needs a deliberate version decision rather than a silent overwrite. The lock
records the version together with the SHA-256 of each committed package. A documentation
or tooling edit changes no package, so it needs no bump; changing the shipped skill does.

The lock deliberately says nothing about whether the packages match their *source* -
`package_skill.py --check` and `build_plugin.py --check` own that question.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "scripts" / "version_lock.json"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"
PACKAGES = ("dist/socialized.zip", "dist/socialized-claude-plugin.zip")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plugin_version(manifest: Path = PLUGIN_MANIFEST) -> str:
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def load_lock(path: Path = LOCK_FILE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def current(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    return {rel: sha256(repo_root / rel) for rel in PACKAGES
            if (repo_root / rel).is_file()}


def problems(repo_root: Path = REPO_ROOT, lock_file: Path | None = None) -> list[str]:
    lock_file = lock_file or repo_root / "scripts" / "version_lock.json"
    manifest = repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json"
    found: list[str] = []
    if not lock_file.is_file():
        return [f"{lock_file.name} is missing"]
    lock = load_lock(lock_file)
    locked = lock.get("packages")
    if not isinstance(locked, dict) or not locked:
        return [f"{lock_file.name} records no packages"]

    version = plugin_version(manifest)
    if lock.get("plugin_version") != version:
        found.append(
            f"plugin.json version is {version!r} but the lock records "
            f"{lock.get('plugin_version')!r}; run version_lock.py --update after an intended bump")

    now = current(repo_root)
    for rel in sorted(set(locked) - set(now)):
        found.append(f"{rel} is locked but missing from the checkout")
    for rel in sorted(set(now) - set(locked)):
        found.append(f"{rel} is committed but not locked")
    for rel in sorted(set(locked) & set(now)):
        if locked[rel] != now[rel]:
            found.append(
                f"{rel} changed since version {lock.get('plugin_version')} was locked. "
                "A changed package needs a version decision: bump "
                "plugins/socialized/.claude-plugin/plugin.json, then run "
                "python scripts/version_lock.py --update")
    return found


def update(repo_root: Path = REPO_ROOT, lock_file: Path | None = None) -> dict:
    lock_file = lock_file or repo_root / "scripts" / "version_lock.json"
    lock = load_lock(lock_file) if lock_file.is_file() else {}
    lock["plugin_version"] = plugin_version(
        repo_root / "plugins" / "socialized" / ".claude-plugin" / "plugin.json")
    lock["packages"] = current(repo_root)
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return lock


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or update the package version lock.")
    parser.add_argument("--update", action="store_true",
                        help="record the current packages and plugin version (the only writing mode)")
    args = parser.parse_args(argv)

    if args.update:
        lock = update()
        print(f"Locked version {lock['plugin_version']}:")
        for rel, digest in lock["packages"].items():
            print(f"  {rel}  {digest[:16]}...")
        return 0

    found = problems()
    if found:
        print("Version lock is out of date:")
        for problem in found:
            print(f"  - {problem}")
        return 1
    print(f"Packages match the locked version {load_lock()['plugin_version']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
