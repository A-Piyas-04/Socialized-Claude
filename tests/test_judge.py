import io
import json
import re
import urllib.error

import pytest

import evalschema as es
import judge as jd
import judgelib as jl
import make_run_sheet
import screen_items as si
import summarize_results

KEY = "AIzaFAKEKEYFAKEKEYFAKEKEYFAKEKEY12345"


class FakeBackend:
    """Deterministic judge. Fact replies read `cf:<id>` / `mis:<id>` markers in the answer."""

    name, model = "fake", "fake-judge-1"

    def __init__(self, pairwise="prefer_longer", known=None, recall_stems=()):
        self.pairwise, self.known, self.recall_stems = pairwise, known or {}, recall_stems
        self.prompts = []

    def complete(self, prompt, temperature):
        self.prompts.append(prompt)
        if "FACTS:" in prompt:
            answer = prompt.split("ANSWER:", 1)[1].split("FACTS:", 1)[0]
            return json.dumps({"facts_stated": re.findall(r"cf:(\S+)", answer),
                               "misconceptions_asserted": re.findall(r"mis:(m\d+)", answer)})
        if "ANSWER 1:" in prompt:
            one = prompt.split("ANSWER 1:", 1)[1].split("ANSWER 2:", 1)[0]
            two = prompt.split("ANSWER 2:", 1)[1]
            if self.pairwise == "always_first":
                return '{"winner": 1}'
            return '```json\n{"winner": %d}\n```' % (1 if len(one) > len(two.split(">>>")[0]) else 2)
        if '"class"' in prompt:
            stem = prompt.split("Item: ", 1)[1].split("\n", 1)[0]
            return json.dumps({"class": "recall" if stem in self.recall_stems else "application"})
        stem = prompt.split("reading material.\n\n", 1)[1].split("\n", 1)[0]
        if stem in self.known:
            for line in prompt.splitlines():
                if line[1:3] == ". " and line[3:] == self.known[stem]:
                    return json.dumps({"answer": line[0]})
        return '{"answer": "Z"}'


@pytest.fixture
def run_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(make_run_sheet.es, "REPO_ROOT", tmp_path)
    make_run_sheet.main(["--run-id", "r", "--runs-dir", str(tmp_path), "--cases", "found_001,mech_001",
                         "--conditions", "A_normal,C_skill", "--samples", "2"])
    run = tmp_path / "r"
    _, rows = es.read_csv(run / "run_sheet.csv")
    for row in rows:
        facts = [f["id"] for f in es.load_cases()[row["case_id"]]["critical_facts"]]
        if row["condition"] == "C_skill":
            text = "A longer, structured answer using the explanation-lab skill. " + " ".join(f"cf:{f}" for f in facts[:1])
        else:
            text = "Plain answer. " + " ".join(f"cf:{f}" for f in facts[:2]) + " mis:m1"
        (run / row["response_file"]).write_text(f"{text} (sample {row['sample_index']})", encoding="utf-8")
    return run


def test_facts_prompt_and_parse_ignore_unknown_ids():
    case = es.load_cases()["found_001"]
    prompt = jd.facts_prompt(case, "Text")
    assert "found_001_cf1" in prompt and "m1: DNA itself performs" in prompt
    stated, asserted = jd.parse_facts('{"facts_stated": ["found_001_cf2", "bogus"], '
                                      '"misconceptions_asserted": ["m3", "m9"]}', case)
    assert stated == ["found_001_cf2"] and asserted == ["m3"]


def test_blinding_removes_skill_mentions():
    assert "explanation" not in jd.blind("Using the Explanation-Lab skill, here is it. explanation_lab").lower()
    assert "socialized" not in jd.blind("Use the socialized skill. Socialized-Claude says so.").lower()


def test_parse_json_object_tolerates_prose_and_fences():
    assert jl.parse_json_object('Sure! {"winner": 2} hope that helps') == {"winner": 2}
    assert jl.parse_json_object('```json\n{"a": {"b": 1}}\n```') == {"a": {"b": 1}}
    with pytest.raises(jl.JudgeError):
        jl.parse_json_object("no json here")


def test_judge_run_tables(run_dir):
    backend = FakeBackend()
    summary = jd.judge_run(run_dir, backend)
    facts = summary["facts"]["by_condition"]
    assert facts["A_normal"]["mean_fact_capture"] > facts["C_skill"]["mean_fact_capture"]
    assert facts["A_normal"]["responses_asserting_misconception"] == 4
    table = summary["pairwise"]["tables"]["pairwise"]["C_skill vs A_normal"]
    assert table == {"pairs": 4, "order_flips": 0, "flip_rate": 0.0, "consistent": 4, "x_wins": 4, "y_wins": 0,
                     "x_win_share": 1.0}
    assert set(summary["pairwise"]["tables"]) == {"pairwise", "navigability", "register_fit"}
    check = summary["fluency_checks"][0]
    assert check["comparison"] == "C_skill vs A_normal" and check["flag"] is True
    md = (run_dir / "judge" / "judge_summary.md").read_text(encoding="utf-8")
    assert md.index(es.SURFACE_NOTICE) < md.index("## Preference versus fact capture")
    assert es.JUDGE_NOTICE in md and "PREFERENCE UP, FACTS FLAT/DOWN" in md
    assert all("explanation-lab" not in p for p in backend.prompts), "condition must be blinded"


def test_every_pair_is_judged_in_both_orders(run_dir):
    backend = FakeBackend()
    jd.judge_run(run_dir, backend, ("pairwise",))
    _, rows = es.read_csv(run_dir / "judge" / "pairwise.csv")
    assert len(backend.prompts) == 2 * len(rows)
    assert {r["first_shown"] for r in rows} <= {"x", "y"}


def test_position_bias_shows_up_as_flips_and_is_discarded(run_dir):
    summary = jd.judge_run(run_dir, FakeBackend(pairwise="always_first"), ("pairwise",))
    table = summary["pairwise"]["tables"]["pairwise"]["C_skill vs A_normal"]
    assert table["flip_rate"] == 1.0 and table["consistent"] == 0 and table["x_win_share"] is None


def test_cache_makes_reruns_free(run_dir):
    jd.judge_run(run_dir, FakeBackend())
    again = jd.judge_run(run_dir, FakeBackend())
    assert again["judge_calls"] == 0 and again["cache_hits"] > 0


def test_summarize_prints_judge_comparison_first(run_dir, monkeypatch):
    jd.judge_run(run_dir, FakeBackend())
    summary, _ = summarize_results.summarize(run_dir, n_boot=10)
    md = summarize_results.render_markdown(summary)
    assert md.index("Automated screening: preference versus fact capture") < md.index("## Success criteria")
    assert all(c["id"] in {"S1", "S2", "S3", "S4", "S5", "S6", "S7"} for c in summary["criteria"])
    assert "judge" not in json.dumps(summary["criteria"]).lower()


def test_calibration_withholds_verdicts(run_dir, tmp_path):
    jd.judge_run(run_dir, FakeBackend(), ("facts",))
    _, fact_rows = es.read_csv(run_dir / "judge" / "fact_capture.csv")
    md, key = tmp_path / "cal.md", tmp_path / "key.json"
    n = jd.write_calibration(run_dir, jd.load_responses(run_dir), fact_rows, es.load_cases(), md, key, 0)
    assert n == 8
    text = md.read_text(encoding="utf-8")
    assert "A_normal" not in text and "C_skill" not in text and "found_001_cf1" in text
    assert es.SURFACE_NOTICE in text and es.JUDGE_NOTICE in text
    items = json.loads(key.read_text(encoding="utf-8"))["items"]
    assert {i["condition"] for i in items} == {"A_normal", "C_skill"}


class OracleBackend:
    """Knows which texts are the archive originals. mode: good | shorter (consistent but useless) | first."""

    name, model = "oracle", "oracle-1"

    def __init__(self, originals, buried, mode="good"):
        self.originals, self.buried, self.mode = originals, buried, mode

    def complete(self, prompt, temperature):
        if "FACTS:" in prompt:
            answer = prompt.split("ANSWER:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
            ids = re.findall(r"^- (\S+?_f\d+):", prompt, flags=re.M)
            keep = len(ids) if answer in self.originals or answer in self.buried else len(ids) - 1
            return json.dumps({"facts_stated": ids[:keep], "misconceptions_asserted": []})
        one = prompt.split("ANSWER 1:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
        two = prompt.split("ANSWER 2:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
        if self.mode == "first":
            return '{"winner": 1}'
        if self.mode == "pretty":
            markup = lambda t: t.count("**") + t.count("\n- ") + t.count("## ")  # noqa: E731
            if markup(one) != markup(two):
                return '{"winner": %d}' % (1 if markup(one) > markup(two) else 2)
        if self.mode == "shorter":
            return '{"winner": %d}' % (1 if (len(one), one) < (len(two), two) else 2)
        if (one in self.originals) != (two in self.originals):
            return '{"winner": %d}' % (1 if one in self.originals else 2)
        return '{"winner": %d}' % (1 if len(one) >= len(two) else 2)


def oracle(mode="good"):
    import judge_acceptance as ja
    cases, responses = ja.load_archive()
    base = {r["case_id"]: r for r in responses if r["style"] == "base"}
    originals = {r["text"] for r in base.values()}
    buried = {ja.bury(r["text"]) for r in base.values()}
    return OracleBackend(originals, buried, mode)


def test_acceptance_is_claude_only_with_a_floor(tmp_path):
    import judge_acceptance as ja
    cases, responses = ja.load_archive()
    assert len(responses) == 15 and {r["style"] for r in responses} == {"base", "tutor", "pedagogical"}
    result = ja.acceptance(oracle(), cache_dir=tmp_path / "c1")
    assert result["strata"]["claude-base vs claude-pedagogical"]["pairs"] == 5
    assert not any("gpt" in k for k in result["strata"])
    assert len(result["floor_pairs"]) == 20, "5 topics x truncated, fact_removed, buried, formatted_emptier"
    assert result["thresholds"] == {"max_flip_rate": 0.20, "floor_min_share": 0.80}
    assert result["floor"]["pairwise_floor_passed"] and result["floor"]["fact_floor_passed"]
    assert result["floor"]["presentation_floor_passed"]
    assert result["accepted"] is True and "ACCEPTED" in ja.render(result)


def test_a_judge_that_rewards_formatting_is_rejected(tmp_path):
    import judge_acceptance as ja
    result = ja.acceptance(oracle("pretty"), cache_dir=tmp_path / "c4")
    assert result["flip_rate"] == 0.0
    assert result["floor"]["pairwise_floor_passed"], "it handles truncation, removal and burying correctly"
    assert result["floor"]["formatted_emptier_preferred_count"] == 5
    assert not result["floor"]["presentation_floor_passed"] and result["accepted"] is False


def test_a_consistent_but_useless_judge_is_rejected(tmp_path):
    import judge_acceptance as ja
    result = ja.acceptance(oracle("shorter"), cache_dir=tmp_path / "c2")
    assert result["flip_rate"] == 0.0 and result["flip_rate_passed"]
    assert not result["floor"]["pairwise_floor_passed"] and result["accepted"] is False


def test_a_position_biased_judge_is_rejected(tmp_path):
    import judge_acceptance as ja
    result = ja.acceptance(oracle("first"), cache_dir=tmp_path / "c3")
    assert result["flip_rate"] == 1.0 and result["accepted"] is False and "REJECTED" in ja.render(result)


def test_degradations_are_deterministic_and_targeted():
    import judge_acceptance as ja
    cases, responses = ja.load_archive()
    for r in (r for r in responses if r["style"] == "base"):
        case = cases[r["case_id"]]
        versions = {v["degradation"]: v for v in ja.degraded_versions(r, case)}
        assert len(ja.truncate(r["text"]).split()) < 0.5 * len(r["text"].split())
        assert ja.paragraphs(versions["buried"]["text"])[-1] == ja.paragraphs(r["text"])[0]
        assert sorted(versions["buried"]["text"].split()) == sorted(r["text"].split())
        removed = versions["fact_removed"]["text"]
        for old, new in ja.FACT_REMOVALS[case["topic"]][1]:
            assert old not in removed and (not new or new in removed)
        pretty = versions["formatted_emptier"]["text"]
        assert pretty.startswith("## Overview") and "\n- " in pretty and "**" in pretty
        assert len(pretty.split()) < len(r["text"].split()), "looks more organised, contains less"
    assert ja.degraded_versions(responses[0], cases[responses[0]["case_id"]]) == \
        ja.degraded_versions(responses[0], cases[responses[0]["case_id"]])


def test_fact_removal_list_must_match_exactly():
    import judge_acceptance as ja
    with pytest.raises(ValueError, match="does not match"):
        ja.remove_fact("Unrelated text.", "databases")


def test_floor_verdict_thresholds():
    import judge_acceptance as ja
    rows = [{"winner": "x"}] * 4 + [{"winner": "y"}]
    meta = [{"original": "o", "degraded": f"d{i}", "degradation": "fact_removed", "topic": "t"} for i in range(5)]
    counts = {"o": 4, "d0": 3, "d1": 3, "d2": 3, "d3": 3, "d4": 4}
    verdict = ja.floor_verdicts(rows, counts, meta)
    assert verdict["pairwise_floor_passed"] and verdict["fact_lower_share"] == 0.8
    assert not verdict["fact_floor_passed"], "no buried control judged, so the fact floor cannot pass"


class UsageBackend(FakeBackend):
    name, model = "fake-groq", "fake-model"

    def complete(self, prompt, temperature):
        self.last_usage = {"prompt_tokens": len(prompt) // 4, "completion_tokens": 300,
                           "total_tokens": len(prompt) // 4 + 300}
        self.last_limits = {"x-ratelimit-limit-requests": "1000"}
        return '{"winner": 1}' if "ANSWER 1:" in prompt else '{"facts_stated": [], "misconceptions_asserted": []}'


def test_capacity_projection_measures_real_usage_and_stops_when_too_slow(tmp_path, monkeypatch, capsys):
    import judge_acceptance as ja
    import judge_capacity as jc
    monkeypatch.setattr(ja, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(jc, "OUT_PATH", tmp_path / "capacity.json")
    monkeypatch.setattr(jl, "backend_from_env", lambda **kw: UsageBackend())
    assert jc.main(["--tpd", "10000000"]) == 0
    result = json.loads((tmp_path / "capacity.json").read_text(encoding="utf-8"))
    assert [m["kind"] for m in result["measured"]] == ["pairwise", "facts"]
    assert result["requests_per_day"] == 1000 and result["mean_completion_tokens"] == 300
    assert result["plans"]["acceptance"]["calls"] == 95, "15 + 20 pairs in both orders, 25 fact prompts"
    assert result["plans"]["pilot sweep"]["calls"] == 192 + 16 * 3 * 4 * 3 * 2
    monkeypatch.setattr(ja, "CACHE_DIR", tmp_path / "cache2")
    assert jc.main(["--tpd", "100000"]) == 3
    assert "STOP:" in capsys.readouterr().out


# --- Gemini client (no network) ------------------------------------------------

class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_gemini_sends_key_in_header_not_url():
    seen = []

    def opener(request, timeout):
        seen.append(request)
        return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": '{"winner": 1}'}]}}]}).encode())

    backend = jl.GeminiBackend(KEY, "m", min_interval=0, opener=opener, sleep=lambda _: None)
    assert backend.complete("hi", 0.0) == '{"winner": 1}'
    assert KEY not in seen[0].full_url and seen[0].get_header("X-goog-api-key") == KEY


def test_gemini_rejects_silent_model_reroute():
    def opener(request, timeout):
        return FakeResponse(json.dumps({"modelVersion": "gemini-other", "candidates": [
            {"content": {"parts": [{"text": "{}"}]}}]}).encode())

    backend = jl.GeminiBackend(KEY, "gemini-3.6-flash", min_interval=0, opener=opener, sleep=lambda _: None)
    with pytest.raises(jl.JudgeError, match="answered with gemini-other"):
        backend.complete("hi", 0.0)


def test_gemini_retries_then_reports_unavailable_without_leaking_key():
    waits = []

    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 429, "Too Many Requests", {}, None)

    backend = jl.GeminiBackend(KEY, "m", min_interval=0, max_retries=2, backoff=1, opener=opener, sleep=waits.append)
    with pytest.raises(jl.JudgeUnavailable) as info:
        backend.complete("hi", 0.0)
    assert waits == [1, 2] and KEY not in str(info.value)


def test_daily_quota_stops_without_retrying():
    waits = []
    body = json.dumps({"error": {"details": [{"violations": [
        {"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier", "quotaValue": "20"}]}]}}).encode()

    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 429, "Too Many Requests", {}, io.BytesIO(body))

    backend = jl.GeminiBackend(KEY, "m", min_interval=0, max_retries=3, opener=opener, sleep=waits.append)
    with pytest.raises(jl.JudgeUnavailable, match="daily quota .* \\(20 requests per day\\)"):
        backend.complete("hi", 0.0)
    assert waits == []


def test_backend_requires_key():
    with pytest.raises(jl.JudgeError, match="GROQ_API_KEY is not set"):
        jl.backend_from_env({})
    with pytest.raises(jl.JudgeError, match="GEMINI_API_KEY is not set"):
        jl.backend_from_env({"JUDGE_BACKEND": "gemini"})
    with pytest.raises(jl.JudgeError, match="unknown JUDGE_BACKEND"):
        jl.backend_from_env({"JUDGE_BACKEND": "other"})


GROQ_KEY = "gsk_" + "F" * 40


def groq(opener, **kwargs):
    return jl.OpenAICompatibleBackend("groq", jl.GROQ_URL, GROQ_KEY, "openai/gpt-oss-120b", min_interval=0,
                                      opener=opener, **kwargs)


def test_groq_is_the_default_and_sends_bearer_header():
    backend = jl.backend_from_env({"GROQ_API_KEY": GROQ_KEY + "\n"})
    assert backend.name == "groq" and backend.model == jl.DEFAULT_GROQ_MODEL
    seen = []

    def opener(request, timeout):
        seen.append(request)
        return FakeResponse(json.dumps({"model": "openai/gpt-oss-120b",
                                        "choices": [{"message": {"content": '{"winner": 2}'}}]}).encode())

    assert groq(opener).complete("hi", 0.0) == '{"winner": 2}'
    body = json.loads(seen[0].data)
    assert body["response_format"] == {"type": "json_object"} and body["messages"][0]["content"] == "hi"
    assert GROQ_KEY not in seen[0].full_url and seen[0].get_header("Authorization") == f"Bearer {GROQ_KEY}"


def test_groq_daily_limit_stops_and_minute_limit_waits():
    day = json.dumps({"error": {"message": "Rate limit reached for model on requests per day (RPD): Limit 1000"}})

    def daily(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 429, "Too Many", {}, io.BytesIO(day.encode()))

    waits = []
    with pytest.raises(jl.JudgeUnavailable, match="daily limit"):
        groq(daily, sleep=waits.append).complete("hi", 0.0)
    assert waits == []

    calls = []

    def minute_then_ok(request, timeout):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "Too Many", {"retry-after": "7"},
                                         io.BytesIO(b'{"error": {"message": "requests per minute (RPM)"}}'))
        return FakeResponse(json.dumps({"model": "openai/gpt-oss-120b",
                                        "choices": [{"message": {"content": "{}"}}]}).encode())

    assert groq(minute_then_ok, sleep=waits.append).complete("hi", 0.0) == "{}"
    assert waits == [7.0]


def test_groq_rejects_a_different_served_model_and_never_leaks_the_key():
    def opener(request, timeout):
        return FakeResponse(json.dumps({"model": "llama-other", "choices": [{"message": {"content": "{}"}}]}).encode())

    with pytest.raises(jl.JudgeError, match="answered with llama-other") as info:
        groq(opener).complete("hi", 0.0)
    assert GROQ_KEY not in str(info.value)


def test_gemma_requests_skip_json_mode():
    seen = []

    def opener(request, timeout):
        seen.append(json.loads(request.data))
        return FakeResponse(json.dumps({"modelVersion": "gemma-4-26b-a4b-it", "candidates": [
            {"content": {"parts": [{"text": "{}"}]}}]}).encode())

    jl.GeminiBackend(KEY, "gemma-4-26b-a4b-it", min_interval=0, opener=opener, sleep=lambda _: None).complete("x", 0)
    assert "responseMimeType" not in seen[0]["generationConfig"]


# --- item screening ----------------------------------------------------------------

def test_screening_drops_answerable_items_and_flags_recall(tmp_path):
    bank = es.load_json(es.ITEM_BANK_PATH)
    items = {i["item_id"]: i for t in bank["topics"] for i in t["items"]}
    known = {items["nc_pre_1"]["stem"]: items["nc_pre_1"]["options"][items["nc_pre_1"]["correct_index"]]}
    backend = FakeBackend(known=known, recall_stems={items["gps_post_3"]["stem"], items["fr_pre_1"]["stem"]})
    screened = si.screen_bank(bank, backend, attempts=3, cache_dir=tmp_path / "cache")
    s = screened["screening"]
    assert s["mc_items"] == 21 and s["dropped"] == ["nc_pre_1"] and s["survivors"] == 20
    assert s["recall_flagged"] == ["fr_pre_1", "gps_post_3"]
    assert s["mislabelled"] == ["gps_post_3"]
    kept = {i["item_id"] for t in screened["topics"] for i in t["items"]}
    assert "nc_pre_1" not in kept and "nc_explain" in kept
    assert screened["notice"] == es.JUDGE_NOTICE
    assert "20/21" in si.report(screened)


def test_screening_reports_collapse_honestly(tmp_path):
    bank = es.load_json(es.ITEM_BANK_PATH)
    known = {i["stem"]: i["options"][i["correct_index"]] for t in bank["topics"] for i in t["items"] if i["format"] == "mc"}
    screened = si.screen_bank(bank, FakeBackend(known=known), attempts=3, cache_dir=tmp_path / "cache")
    assert screened["screening"]["survivors"] == 0
    assert "This is a result, not a reason to relax the rule." in si.report(screened)


def test_answer_options_are_shuffled_per_attempt(tmp_path):
    bank = es.load_json(es.ITEM_BANK_PATH)
    backend = FakeBackend()
    si.screen_bank({"topics": [bank["topics"][0]]}, backend, attempts=5, cache_dir=tmp_path / "cache")
    first_item = [p for p in backend.prompts if bank["topics"][0]["items"][0]["stem"] in p and '"answer"' in p]
    assert len({p.split("\n")[3] for p in first_item}) > 1
