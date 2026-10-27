import json
import os
import sys
from pathlib import Path

import pytest

import collect_cc as cc
import evalschema as es
import make_run_sheet
import package_skill

FAKE = Path(__file__).with_name("fake_claude.py")
REPO = Path(__file__).resolve().parents[1]
TOKEN = "fake-oauth-token-value-1234567890"


@pytest.fixture
def dist(tmp_path, monkeypatch):
    out = tmp_path / "dist"
    for variant in ("full", "seq"):
        _, report = package_skill.build(variant, out_dir=out)
        assert report.ok, report.errors
    monkeypatch.setattr(cc, "DIST_DIR", out)
    return out


@pytest.fixture
def run_dir(tmp_path, dist, monkeypatch):
    monkeypatch.setattr(make_run_sheet.es, "REPO_ROOT", tmp_path)
    make_run_sheet.main(["--run-id", "r", "--runs-dir", str(tmp_path / "runs"), "--cases", "mech_001,fact_003",
                         "--conditions", "A_normal,C_skill_explicit", "--samples", "1"])
    return tmp_path / "runs" / "r"


def fake_env(tmp_path, mode="normal", **extra):
    env = {k: v for k, v in os.environ.items() if k not in cc.FORBIDDEN_ENV and k != cc.TOKEN_ENV}
    env.update({cc.TOKEN_ENV: TOKEN, "FAKE_CLAUDE_MODE": mode, "FAKE_CLAUDE_LOG": str(tmp_path / "calls.log"),
                "FAKE_CLAUDE_STATE": str(tmp_path / "state.txt")})
    env.update(extra)
    return env


CLAUDE = [sys.executable, str(FAKE)]
OPTS = cc.Options(model="sonnet", timeout=60, max_retries=2, backoff=1)


def calls(tmp_path):
    path = tmp_path / "calls.log"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


# --- pure arm checks ---------------------------------------------------------

def init_event(skills, api="none", tools=("Read", "Skill")):
    return {"skills": skills, "slash_commands": skills, "apiKeySource": api, "tools": list(tools),
            "model": "m", "claude_code_version": "v"}


def test_arm_problems_accepts_matching_arms():
    assert cc.arm_problems(True, cc.observe_init(init_event(["explanation-lab", "debug"]))) == []
    assert cc.arm_problems(False, cc.observe_init(init_event(["debug"]))) == []


def test_arm_problems_flags_each_mismatch():
    assert "ON" in cc.arm_problems(True, cc.observe_init(init_event(["debug"])))[0]
    assert "skillOverrides" in cc.arm_problems(False, cc.observe_init(init_event(["explanation-lab"])))[0]
    assert "cannot be verified" in cc.arm_problems(False, cc.observe_init({"apiKeySource": "none",
                                                                           "tools": ["Read", "Skill"]}))[0]
    assert "apiKeySource" in cc.arm_problems(True, cc.observe_init(init_event(["explanation-lab"], api="ANTHROPIC_API_KEY")))[0]
    assert "tools" in cc.arm_problems(True, cc.observe_init(init_event(["explanation-lab"], tools=("Bash",))))[0]


def test_skill_touch_detection():
    assert cc.invokes_skill({"name": "Skill", "input": {"skill": "explanation-lab"}})
    assert cc.invokes_skill({"name": "Skill", "input": {"command": "/explanation-lab"}})
    assert not cc.invokes_skill({"name": "Skill", "input": {"skill": "debug"}})
    assert cc.reads_skill_file({"name": "Read", "input": {
        "file_path": "C:\\t\\work\\.claude\\skills\\explanation-lab\\references\\treatment-selection.md"}}) \
        == "references/treatment-selection.md"
    assert cc.reads_skill_file({"name": "Read", "input": {"file_path": "/x/notes.md"}}) is None


def test_classify_result():
    assert cc.classify_result({"subtype": "success", "is_error": False, "result": "hi"}, False)[0] == "ok"
    assert cc.classify_result({"is_error": True, "api_error_status": 429, "result": ""}, False)[0] == "rate_limited"
    assert cc.classify_result({"is_error": True, "result": "Claude AI usage limit reached"}, False)[0] == "rate_limited"
    assert cc.classify_result({"is_error": True, "result": "Not logged in"}, False)[0] == "auth"
    assert cc.classify_result({"is_error": True, "result": "boom"}, False)[0] == "error"


# --- environment ---------------------------------------------------------------

def test_refuses_api_key(tmp_path, run_dir):
    env = fake_env(tmp_path, ANTHROPIC_API_KEY="sk-ant-should-never-be-used")
    with pytest.raises(cc.HarnessError, match="ANTHROPIC_API_KEY is set"):
        cc.collect(run_dir, CLAUDE, env, OPTS, write=lambda _: None)
    assert calls(tmp_path) == []
    assert env["ANTHROPIC_API_KEY"], "the key must be left for the user to unset"


def test_main_refuses_api_key(tmp_path, run_dir, monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-should-never-be-used")
    monkeypatch.setenv(cc.TOKEN_ENV, TOKEN)
    code = cc.main([str(run_dir), "--claude", sys.executable])
    assert code == 1
    assert "ANTHROPIC_API_KEY is set" in capsys.readouterr().err


def test_requires_token(tmp_path, run_dir):
    env = fake_env(tmp_path)
    del env[cc.TOKEN_ENV]
    with pytest.raises(cc.HarnessError, match="CLAUDE_CODE_OAUTH_TOKEN is not set"):
        cc.collect(run_dir, CLAUDE, env, OPTS, write=lambda _: None)


# --- full collection with the fake CLI ------------------------------------------

def test_collects_and_fills_run_sheet(tmp_path, run_dir):
    assert cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None, today="2026-10-27") == 0
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    assert len(rows) == 4
    for row in rows:
        assert (run_dir / row["response_file"]).read_text(encoding="utf-8").startswith("Fake answer")
        assert row["surface"] == "claude-code" and row["operator"] == "collect_cc"
        assert row["model_label"] == "claude-fake-1" and row["date"] == "2026-10-27"
        if row["batch"] == "skill_off":
            assert row["activation_observed"] == "na"
            assert "does not list explanation-lab (skillOverrides off)" in row["activation_evidence"]
        else:
            assert row["activation_observed"] == "yes"
            assert "lists explanation-lab" in row["activation_evidence"]
    log = calls(tmp_path)
    assert len(log) == 4
    assert all(REPO not in Path(c["cwd"]).parents for c in log), "sandbox must be outside the repo"
    assert len({c["config"] for c in log}) == 4, "each row needs its own CLAUDE_CONFIG_DIR"
    assert (run_dir / "COLLECTION_NOTICE.md").read_text(encoding="utf-8").count(es.SURFACE_NOTICE) == 1
    meta = json.loads((run_dir / "cc_meta" / f"{rows[0]['row_id']}.json").read_text(encoding="utf-8"))
    assert meta["notice"] == es.SURFACE_NOTICE and meta["status"] == "ok"


def test_summarize_check_only_passes_after_collection(tmp_path, run_dir):
    import summarize_results
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None)
    assert summarize_results.main([str(run_dir), "--check-only"]) == 0


def test_mismatch_fails_row_and_stops(tmp_path, run_dir):
    code = cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "ignore_overrides"), OPTS, write=lambda _: None)
    assert code == 3
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    first = min(rows, key=lambda r: int(r["order"]))
    assert first["batch"] == "skill_off"
    assert not (run_dir / first["response_file"]).exists()
    assert "ARM MISMATCH" in first["notes"] and "skillOverrides not honoured" in first["notes"]
    assert "lists explanation-lab" in first["activation_evidence"]
    assert len(calls(tmp_path)) == 1, "no further rows after a mismatch"


def test_skill_off_row_that_reads_the_skill_is_failed(tmp_path, run_dir):
    assert cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "read_skill_off"), OPTS, write=lambda _: None) == 3
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    first = min(rows, key=lambda r: int(r["order"]))
    assert "touched the skill via Read" in first["notes"]


def test_missing_init_is_a_mismatch(tmp_path, run_dir):
    assert cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "no_init"), OPTS, write=lambda _: None) == 3


def test_api_key_source_is_a_mismatch(tmp_path, run_dir):
    assert cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "apikey"), OPTS, write=lambda _: None) == 3


def test_resume_skips_existing_responses(tmp_path, run_dir):
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, limit=1, write=lambda _: None)
    assert len(calls(tmp_path)) == 1
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None)
    assert len(calls(tmp_path)) == 4, "the completed row must not be re-run"


def test_backfill_after_crash_between_response_and_sheet(tmp_path, run_dir):
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, limit=1, write=lambda _: None)
    header, rows = es.read_csv(run_dir / "run_sheet.csv")
    done = [r for r in rows if r["date"]]
    for column in ("date", "surface", "model_label", "operator"):
        done[0][column] = ""
    es.write_csv(run_dir / "run_sheet.csv", header, rows)
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None)
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    assert all(r["date"] and r["surface"] == "claude-code" for r in rows)


def test_rate_limit_retries_then_succeeds(tmp_path, run_dir):
    waits = []
    code = cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "ratelimit_once"), OPTS, limit=1,
                      write=lambda _: None, sleep=waits.append)
    assert code == 0 and waits == [1]


def test_rate_limit_cap_records_incomplete_and_continues(tmp_path, run_dir):
    waits = []
    opts = cc.Options(timeout=60, max_retries=2, backoff=1, max_consecutive_incomplete=2)
    code = cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "ratelimit"), opts, write=lambda _: None,
                      sleep=waits.append)
    assert code == 2
    assert waits == [1, 2, 1, 2], "two rows, each backing off twice, then stop after 2 consecutive"
    _, rows = es.read_csv(run_dir / "run_sheet.csv")
    incomplete = [r for r in rows if "incomplete (rate_limited)" in r["notes"]]
    assert len(incomplete) == 2
    assert not any((run_dir / r["response_file"]).exists() for r in rows)


def test_auth_failure_aborts(tmp_path, run_dir):
    with pytest.raises(cc.HarnessError, match="authentication failed"):
        cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "auth"), OPTS, write=lambda _: None)


def test_token_never_written(tmp_path, run_dir):
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path, "ratelimit"), cc.Options(max_retries=0, backoff=0,
               max_consecutive_incomplete=1), write=lambda _: None, sleep=lambda _: None)
    cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None)
    for path in run_dir.rglob("*"):
        if path.is_file():
            assert TOKEN not in path.read_text(encoding="utf-8", errors="replace"), path


def test_check_arms_withholds_token(tmp_path, run_dir):
    out = []
    assert cc.check_arms(run_dir, ["skill_off", "skill_on", "variant:seq"], CLAUDE, fake_env(tmp_path), OPTS,
                         write=out.append) == 0
    assert all(" -> OK" in line for line in out)
    assert [c["has_token"] for c in calls(tmp_path)] == [False, False, False]


def test_check_arms_reports_mismatch(tmp_path, run_dir):
    out = []
    assert cc.check_arms(run_dir, ["skill_off"], CLAUDE, fake_env(tmp_path, "ignore_overrides"), OPTS,
                         write=out.append) == 1
    assert "MISMATCH" in out[0]


def test_stale_build_is_refused(tmp_path, run_dir):
    header, rows = es.read_csv(run_dir / "run_sheet.csv")
    for row in rows:
        if row["batch"] == "skill_on":
            row["skill_zip_sha256"] = "0" * 64
    es.write_csv(run_dir / "run_sheet.csv", header, rows)
    with pytest.raises(cc.HarnessError, match="build changed"):
        cc.collect(run_dir, CLAUDE, fake_env(tmp_path), OPTS, write=lambda _: None)


def test_dry_run_calls_nothing(tmp_path, run_dir):
    out = []
    assert cc.dry_run(run_dir, CLAUDE, fake_env(tmp_path), OPTS, None, None, write=out.append) == 0
    assert calls(tmp_path) == []
    assert out[-1].startswith("Planned invocations: 4")


# --- optional: the real Claude Code binary (no quota: the token is withheld) ------

def real_claude():
    if os.environ.get("SMART_CLAUDE_REAL_CC") != "1":
        return None
    try:
        return cc.find_claude(None, dict(os.environ))
    except cc.HarnessError:
        return None


@pytest.mark.skipif(real_claude() is None, reason="set SMART_CLAUDE_REAL_CC=1 with Claude Code installed")
def test_real_binary_honours_skill_overrides(tmp_path, dist, monkeypatch):
    env = {k: v for k, v in os.environ.items() if k not in cc.FORBIDDEN_ENV}
    out = []
    assert cc.check_arms(None, ["skill_off", "skill_on"], real_claude(), env, OPTS, write=out.append) == 0, out

    real_prepare = cc.prepare_sandbox

    def sabotaged(root, arm, manifest):
        work, config, settings = real_prepare(root, arm, manifest)
        settings.write_text("{}", encoding="utf-8")
        return work, config, settings

    monkeypatch.setattr(cc, "prepare_sandbox", sabotaged)
    out = []
    assert cc.check_arms(None, ["skill_off"], real_claude(), env, OPTS, write=out.append) == 1
    assert "MISMATCH" in out[0]
