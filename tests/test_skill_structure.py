"""Structural tests for the skill source, the validator, and the packager."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

import skilllib as lib
from package_skill import build
from validate_skill import validate_dir, validate_zip


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def frontmatter(skill_dir: Path) -> dict:
    meta, _, error = lib.split_frontmatter(read(skill_dir / "SKILL.md"))
    assert error is None
    return meta


def replace_in(path: Path, old: str, new: str) -> None:
    text = read(path)
    assert old in text, f"fixture text not found in {path.name}: {old!r}"
    write(path, text.replace(old, new, 1))


def set_frontmatter(skill_dir: Path, **fields: str) -> None:
    meta = frontmatter(skill_dir)
    meta.update(fields)
    _, body, _ = lib.split_frontmatter(read(skill_dir / "SKILL.md"))
    lines = "\n".join(f"{k}: {json.dumps(v)}" for k, v in meta.items())
    write(skill_dir / "SKILL.md", f"---\n{lines}\n---\n{body}")


def errors_for(skill_dir: Path, **kwargs) -> list[str]:
    return validate_dir(skill_dir, **kwargs).errors


# ---------------------------------------------------------------------------
# The real skill
# ---------------------------------------------------------------------------

def test_real_skill_has_no_errors():
    report = validate_dir(lib.SKILL_DIR)
    assert report.errors == []


def test_metadata_meets_claude_ai_limits():
    meta = frontmatter(lib.SKILL_DIR)
    assert meta["name"] == "explanation-lab"
    assert len(meta["description"]) <= lib.DESCRIPTION_MAX_CLAUDE_AI
    assert "Use when" in meta["description"]
    assert set(meta) <= lib.ALLOWED_FRONTMATTER_KEYS


def test_required_reference_files_exist_and_are_linked():
    body = read(lib.SKILL_DIR / "SKILL.md")
    for name in ("explanation-methodology.md", "treatment-selection.md", "explanation-examples.md"):
        assert (lib.SKILL_DIR / "references" / name).is_file()
        assert f"references/{name}" in body


def test_skill_body_is_compact():
    _, body, _ = lib.split_frontmatter(read(lib.SKILL_DIR / "SKILL.md"))
    rendered = lib.render_markers(body, lib.VARIANTS["full"])
    assert rendered.count("\n") < 300, "SKILL.md should stay well under the 500-line limit"


def test_skill_never_exposes_research_treatment_ids():
    for path in lib.iter_skill_files(lib.SKILL_DIR):
        text = read(path)
        for tid in ("T1", "T2", "T3", "T4", "T5", "T6"):
            assert f"{tid} " not in text and f"{tid}," not in text and f"({tid})" not in text, \
                f"{path.name} mentions research treatment id {tid}"


def test_markers_are_balanced_in_every_file():
    for path in lib.iter_skill_files(lib.SKILL_DIR):
        assert lib.check_markers(read(path), path.name).errors == []


# ---------------------------------------------------------------------------
# Validator failure cases
# ---------------------------------------------------------------------------

def test_missing_skill_md(skill_copy):
    (skill_copy / "SKILL.md").unlink()
    assert any("SKILL.md not found" in e for e in errors_for(skill_copy))


def test_wrong_case_skill_md_is_rejected_even_on_case_insensitive_filesystems(skill_copy):
    (skill_copy / "SKILL.md").rename(skill_copy / "skill.md")
    assert any("must be named exactly SKILL.md" in e for e in errors_for(skill_copy))


def test_missing_frontmatter(skill_copy):
    _, body, _ = lib.split_frontmatter(read(skill_copy / "SKILL.md"))
    write(skill_copy / "SKILL.md", body)
    assert any("frontmatter" in e for e in errors_for(skill_copy))


def test_invalid_yaml(skill_copy):
    text = read(skill_copy / "SKILL.md")
    write(skill_copy / "SKILL.md", text.replace("name: explanation-lab", "name: [unclosed", 1))
    assert any("Invalid YAML" in e for e in errors_for(skill_copy))


@pytest.mark.parametrize("bad_name, fragment", [
    ("Explanation-Lab", "lowercase"),
    ("explanation_lab", "lowercase"),
    ("-explanation", "lowercase"),
    ("explanation--lab", "lowercase"),
    ("claude-explainer", "reserved word 'claude'"),
    ("anthropic-explainer", "reserved word 'anthropic'"),
    ("a" * 65, "maximum is 64"),
])
def test_bad_names(skill_copy, bad_name, fragment):
    set_frontmatter(skill_copy, name=bad_name)
    assert any(fragment in e for e in errors_for(skill_copy)), errors_for(skill_copy)


def test_folder_must_match_name(tmp_path, skill_copy):
    renamed = skill_copy.rename(tmp_path / "other-name")
    assert any("must match name" in e for e in errors_for(renamed))


def test_description_over_200_fails_for_claude_ai_but_warns_for_api(skill_copy):
    long_description = "Explains concepts step by step. Use when someone asks how things work. " * 4
    set_frontmatter(skill_copy, description=long_description.strip())
    assert any("claude.ai maximum" in e for e in errors_for(skill_copy, surface="claude-ai"))
    api_report = validate_dir(skill_copy, surface="api")
    assert not any("claude.ai maximum" in e for e in api_report.errors)
    assert any("claude.ai maximum" in w for w in api_report.warnings)


def test_description_over_1024_always_fails(skill_copy):
    set_frontmatter(skill_copy, description="Use when explaining. " + "x" * 1100)
    assert any("API maximum" in e for e in errors_for(skill_copy, surface="api"))


def test_description_rejects_angle_brackets(skill_copy):
    set_frontmatter(skill_copy, description="Explains <b>concepts</b>. Use when asked.")
    assert any("angle brackets" in e for e in errors_for(skill_copy))


def test_empty_description(skill_copy):
    set_frontmatter(skill_copy, description="   ")
    assert any("must not be empty" in e for e in errors_for(skill_copy))


def test_unexpected_frontmatter_key(skill_copy):
    set_frontmatter(skill_copy, author="someone")
    assert any("Unexpected frontmatter key" in e for e in errors_for(skill_copy))


def test_first_person_description_warns(skill_copy):
    set_frontmatter(skill_copy, description="I can explain concepts. Use when someone is confused.")
    assert any("third person" in w for w in validate_dir(skill_copy).warnings)


def test_missing_reference_file(skill_copy):
    (skill_copy / "references" / "treatment-selection.md").unlink()
    assert any("missing file 'references/treatment-selection.md'" in e for e in errors_for(skill_copy))


@pytest.mark.parametrize("path, fragment", [
    ("../outside.md", "escapes the skill directory"),
    ("references\\explanation-examples.md", "backslash"),
    ("/etc/notes.md", "absolute"),
])
def test_unsafe_reference_paths(skill_copy, path, fragment):
    replace_in(skill_copy / "SKILL.md", "## Reference files", f"## Reference files\n\nSee `{path}`.\n")
    assert any(fragment in e for e in errors_for(skill_copy)), errors_for(skill_copy)


@pytest.mark.parametrize("snippet, fragment", [
    ("Use key sk-ant-api03-abcdefghijklmnopqrstuvwxyz", "Anthropic API key"),
    ("export OPENAI_API_KEY=placeholder", "Provider API key variable"),
    ("POST https://api.anthropic.com/v1/messages", "Anthropic API endpoint"),
    ("call generativelanguage.googleapis.com", "Gemini API endpoint"),
    ("import anthropic", "Provider SDK import"),
    ("-----BEGIN RSA PRIVATE KEY-----", "Private key block"),
])
def test_secrets_and_external_inference_are_rejected(skill_copy, snippet, fragment):
    path = skill_copy / "references" / "treatment-selection.md"
    write(path, read(path) + f"\n{snippet}\n")
    assert any(fragment in e for e in errors_for(skill_copy)), errors_for(skill_copy)


def test_forbidden_files_are_rejected(skill_copy):
    write(skill_copy / ".env", "X=1\n")
    assert any(".env" in e for e in errors_for(skill_copy))


def test_unreferenced_file_warns(skill_copy):
    write(skill_copy / "references" / "orphan.md", "# Orphan\n")
    assert any("orphan.md" in w and "not referenced" in w for w in validate_dir(skill_copy).warnings)


def test_long_reference_without_contents_warns(skill_copy):
    path = skill_copy / "references" / "treatment-selection.md"
    text = read(path).replace("## Contents", "## Overview")
    write(path, text + "\n" + "line\n" * 120)
    assert any("Contents section" in w for w in validate_dir(skill_copy).warnings)


def test_crlf_is_a_warning_not_an_error(skill_copy):
    path = skill_copy / "references" / "treatment-selection.md"
    path.write_bytes(read(path).replace("\n", "\r\n").encode("utf-8"))
    report = validate_dir(skill_copy)
    assert report.errors == []
    assert any("CRLF" in w for w in report.warnings)


# ---------------------------------------------------------------------------
# Operation markers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text, fragment", [
    ("<!-- op:sequencing -->\nx\n", "never closed"),
    ("x\n<!-- /op:sequencing -->\n", "without an opening"),
    ("<!-- op:sequencing -->\n<!-- op:mechanism -->\n<!-- /op:mechanism -->\n<!-- /op:sequencing -->\n", "nested"),
    ("<!-- op:sequencing -->\nx\n<!-- /op:mechanism -->\n", "does not match"),
    ("<!-- op:telepathy -->\nx\n<!-- /op:telepathy -->\n", "unknown operation"),
    ("<!-- op: sequencing extra -->\n", "malformed"),
])
def test_marker_errors(text, fragment):
    assert any(fragment in e for e in lib.check_markers(text, "t").errors)


def test_render_markers_requires_all_listed_operations():
    text = ("keep\n<!-- op:sequencing -->\nseq\n<!-- /op:sequencing -->\n"
            "<!-- op:sequencing,examples -->\nboth\n<!-- /op:sequencing,examples -->\nend\n")
    only_seq = lib.render_markers(text, frozenset({"sequencing"}))
    assert "seq" in only_seq and "both" not in only_seq and "op:" not in only_seq
    full = lib.render_markers(text, frozenset({"sequencing", "examples"}))
    assert "both" in full and "op:" not in full
    none = lib.render_markers(text, frozenset())
    assert none.split() == ["keep", "end"]


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------

def zip_texts(zip_path: Path) -> dict[str, str]:
    with zipfile.ZipFile(zip_path) as archive:
        return {n: archive.read(n).decode("utf-8") for n in archive.namelist() if not n.endswith("/")}


def test_production_zip_structure(tmp_path):
    out, report = build("full", out_dir=tmp_path)
    assert report.ok, report.errors
    assert out == tmp_path / "explanation-lab.zip"
    texts = zip_texts(out)
    assert set(texts) == {
        "explanation-lab/SKILL.md",
        "explanation-lab/references/explanation-methodology.md",
        "explanation-lab/references/treatment-selection.md",
        "explanation-lab/references/explanation-examples.md",
    }
    for name, text in texts.items():
        assert "op:" not in text, f"marker left in {name}"
        assert "\r\n" not in text
    assert texts["explanation-lab/SKILL.md"].startswith("---\nname: explanation-lab\n")


def test_zip_excludes_research_and_evaluation_material(tmp_path):
    out, _ = build("full", out_dir=tmp_path)
    blob = " ".join(zip_texts(out))
    for forbidden in ("research", "evaluation", "TEST_CASES", "transform-", ".csv", ".py"):
        assert forbidden not in blob


def test_build_is_deterministic(tmp_path):
    first, _ = build("full", out_dir=tmp_path / "a")
    second, _ = build("full", out_dir=tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()


def test_manifest_matches_zip(tmp_path):
    out, _ = build("full", out_dir=tmp_path)
    manifest = json.loads(out.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    import hashlib
    assert manifest["zip_sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    assert manifest["enabled_operations"] == sorted(lib.OPERATIONS)


def test_committed_dist_zip_is_current(repo_root, tmp_path):
    committed = repo_root / "dist" / "explanation-lab.zip"
    assert committed.is_file(), "run: python scripts/package_skill.py"
    fresh, _ = build("full", out_dir=tmp_path)
    assert committed.read_bytes() == fresh.read_bytes(), \
        "dist/explanation-lab.zip is stale; run: python scripts/package_skill.py"


HEADINGS = {
    "sequencing": "## Operation: Order ideas by dependency",
    "mechanism": "## Operation: Explain the mechanism",
    "examples": "## Operation: Ground with one example",
    "terms": "## Operation: Introduce terms where they are first needed",
    "presentation": "## Operation: Give the answer the shape of its content",
    "register": "## Operation: Pitch the answer at the reader's register",
    "repair": "## Operation: Repair after a clarification or correction",
    "persistence": "## Operation: Keep standing instructions in force",
    "work-report": "## Operation: Report work that was done",
}


@pytest.mark.parametrize("variant", sorted(lib.VARIANTS))
def test_variants_contain_exactly_their_operations(tmp_path, variant):
    out, report = build(variant, out_dir=tmp_path)
    assert report.ok, report.errors
    skill_text = zip_texts(out)["explanation-lab/SKILL.md"]
    for op, heading in HEADINGS.items():
        assert (heading in skill_text) == (op in lib.VARIANTS[variant]), (variant, op)
    for always in ("## Scope: decide first whether this applies", "## Accuracy rules (always apply)",
                   "## Step 4: Deliver naturally"):
        assert always in skill_text


def test_variants_share_identical_metadata(tmp_path):
    metas = set()
    for variant in lib.VARIANTS:
        out, _ = build(variant, out_dir=tmp_path)
        meta, _, _ = lib.split_frontmatter(zip_texts(out)["explanation-lab/SKILL.md"])
        metas.add((meta["name"], meta["description"]))
    assert len(metas) == 1, "ablation variants must not differ in activation metadata"


def test_single_operation_variants_drop_other_operations_examples(tmp_path):
    out, _ = build("seq", out_dir=tmp_path)
    examples = zip_texts(out)["explanation-lab/references/explanation-examples.md"]
    assert "what a derivative is" in examples
    assert "pressure cooker" not in examples.lower()
    assert "connection pool" not in examples.lower()


# ---------------------------------------------------------------------------
# ZIP validation failure cases
# ---------------------------------------------------------------------------

def make_zip(path: Path, entries: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in entries.items():
            archive.writestr(name, text)
    return path


def test_zip_with_files_at_root_fails(tmp_path):
    skill = read(lib.SKILL_DIR / "SKILL.md")
    bad = make_zip(tmp_path / "bad.zip", {"SKILL.md": skill})
    assert not validate_zip(bad).ok


def test_zip_with_two_roots_fails(tmp_path):
    skill = read(lib.SKILL_DIR / "SKILL.md")
    bad = make_zip(tmp_path / "bad.zip", {"a/SKILL.md": skill, "b/SKILL.md": skill})
    assert any("exactly one top-level" in e for e in validate_zip(bad).errors)


def test_zip_with_nested_skill_md_fails(tmp_path):
    skill = read(lib.SKILL_DIR / "SKILL.md")
    bad = make_zip(tmp_path / "bad.zip", {"explanation-lab/inner/SKILL.md": skill})
    assert any("SKILL.md' missing" in e for e in validate_zip(bad).errors)


def test_corrupt_zip_fails(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"not a zip")
    assert any("not a valid ZIP" in e for e in validate_zip(bad).errors)
