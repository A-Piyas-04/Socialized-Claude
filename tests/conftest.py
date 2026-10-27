import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skilllib  # noqa: E402


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def skill_copy(tmp_path: Path) -> Path:
    """A disposable copy of the real skill directory, for mutation tests."""
    target = tmp_path / "socialized"
    shutil.copytree(skilllib.SKILL_DIR, target)
    return target
