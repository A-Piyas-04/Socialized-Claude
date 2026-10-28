"""Phase 4B: token-budget reporting and the compaction-aware SKILL.md layout.

Every count here is a local estimate. The tests use the stdlib heuristic so they run
offline and identically everywhere; the claude-legacy tokenizer is compared with it
only when its tokenizer.json is already cached locally.
"""

from __future__ import annotations

import json
import re
import zipfile

import pytest

import skilllib as lib
import token_budget as tb


@pytest.fixture(scope="module")
def report() -> dict:
    return tb.build_report(tb.HeuristicCounter(), tb.load_budgets(), tb.load_baseline())


def rows(report: dict) -> dict[str, dict]:
    return {r["id"]: r for r in report["components"]}


def test_heuristic_counter_is_deterministic():
    counter = tb.HeuristicCounter()
    assert counter.count("") == 0
    text = "The server rejects the request, so the client retries."
    assert counter.count(text) == counter.count(text) > 0


def test_every_instruction_surface_is_reported(report):
    ids = set(rows(report))
    assert {"metadata", "activation", "persistent:project-instructions", "persistent:claude-md"} <= ids
    for name in ("explanation-examples.md", "explanation-methodology.md", "treatment-selection.md"):
        assert f"ref:{name}" in ids
    for name in ("core.md", "strategies.md", "controls.md"):
        assert f"repo:communication/{name}" in ids
    loading = {r["id"]: r["loading"] for r in report["components"]}
    assert loading["activation"] == tb.ON_ACTIVATION
    assert loading["ref:treatment-selection.md"] == tb.ON_DEMAND
    assert loading["repo:communication/core.md"] == tb.NOT_SHIPPED
    assert "Not measured Claude API usage" in report["disclaimer"]


def test_activation_component_is_the_shipped_skill_md(repo_root, report):
    shipped = next(c.text for c in tb.collect() if c.id == "activation")
    with zipfile.ZipFile(repo_root / "dist" / "socialized.zip") as archive:
        assert archive.read("socialized/SKILL.md").decode("utf-8") == shipped
    assert report["plugin_copy_identical"] is True


def test_totals_are_consistent(report):
    r, totals = rows(report), report["totals"]
    refs = sum(v["tokens"] for k, v in r.items() if k.startswith("ref:"))
    assert totals["references_on_demand"] == refs
    assert totals["distributable_skill"] == r["activation"]["tokens"] + refs
    assert totals["loaded_on_activation"] == r["activation"]["tokens"]
    assert totals["persistent_opt_in"] == (r["persistent:project-instructions"]["tokens"]
                                          + r["persistent:claude-md"]["tokens"])


def test_persistent_snippets_are_found():
    snippets = tb.persistent_snippets()
    assert "answer the question in the first sentence" in snippets["persistent:project-instructions"]
    assert snippets["persistent:claude-md"].startswith("<!-- BEGIN socialized-claude -->")


def test_repository_passes_its_configured_budgets(report):
    assert report["over_budget"] == []


def test_activation_shrank_from_the_recorded_baseline(report):
    activation = rows(report)["activation"]
    assert activation["baseline"] is not None
    assert activation["tokens"] < activation["baseline"]


def test_budgets_are_configurable_and_targets_never_gate(tmp_path, capsys):
    assert tb.main(["--tokenizer", "heuristic", "--check", "--budget", "activation=100"]) == 1
    assert "Over budget: activation" in capsys.readouterr().out
    assert tb.main(["--tokenizer", "heuristic", "--check", "--budget", "activation=none"]) == 0
    config = tmp_path / "budgets.json"
    config.write_text(json.dumps({"budgets": {"activation": {"max": None, "target": 1}}}), encoding="utf-8")
    assert tb.main(["--tokenizer", "heuristic", "--check", "--budgets", str(config)]) == 0
    assert "Above advisory target (does not fail): activation" in capsys.readouterr().out


def test_budget_override_rejects_malformed_values():
    with pytest.raises(SystemExit):
        tb.load_budgets(overrides=["activation"])


def test_json_report_round_trips(tmp_path):
    out = tmp_path / "report.json"
    assert tb.main(["--tokenizer", "heuristic", "--json", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["tokenizer"] == "heuristic" and data["totals"]["loaded_on_activation"] > 0


def test_write_baseline_keeps_other_tokenizers(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"counts": {"other": {"activation": 1}}}), encoding="utf-8")
    assert tb.main(["--tokenizer", "heuristic", "--baseline", str(path), "--write-baseline", "test"]) == 0
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["source"] == "test" and set(data["counts"]) == {"other", "heuristic"}


def test_legacy_tokenizer_is_never_downloaded(tmp_path, monkeypatch):
    monkeypatch.delenv("SOCIALIZED_TOKENIZER_FILE", raising=False)
    monkeypatch.setenv("HF_HUB_CACHE", str(tmp_path))
    assert tb.find_legacy_file() is None
    with pytest.raises(SystemExit):
        tb.make_counter("claude-legacy")
    assert isinstance(tb.make_counter("auto"), tb.HeuristicCounter)


def test_heuristic_tracks_the_legacy_tokenizer_when_cached():
    path = tb.find_legacy_file()
    if path is None:
        pytest.skip("claude-legacy tokenizer.json not cached locally")
    pytest.importorskip("tokenizers")
    legacy, heuristic = tb.LegacyCounter(path), tb.HeuristicCounter()
    activation = next(c.text for c in tb.collect() if c.id == "activation")
    assert abs(heuristic.count(activation) - legacy.count(activation)) / legacy.count(activation) < 0.05


# ---------------------------------------------------------------------------
# Compaction-aware layout: the always-on core comes before the operations
# ---------------------------------------------------------------------------

ALWAYS_ON = (
    "## Scope: decide first whether this applies",
    "## Match the communication strategy to the intent",
    "## Step 1: Read the request (silently)",
    "## Step 2: Size the answer",
    "## Accuracy rules (always apply)",
    "## Reference files",
)


def test_always_on_core_precedes_every_operation():
    text = lib.render_markers(lib.split_frontmatter(
        (lib.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n"))[1],
        lib.VARIANTS["full"])
    first_operation = text.index("## Operation:")
    for heading in ALWAYS_ON:
        assert text.index(heading) < first_operation, heading
    assert text.rindex("## Operation:") < text.index("## Step 3: Check before sending (silently)")


def test_always_on_core_survives_compaction_reattach(report):
    past = " ".join(report["past_compaction_keep"])
    for heading in ALWAYS_ON:
        assert heading[3:] not in past, heading
    assert not re.search(r"Operation: (Order|Explain|Ground|Introduce|Write|Give|Show|Pitch|Repair|Keep)", past)
