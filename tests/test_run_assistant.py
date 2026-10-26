"""Tests for the interactive run assistant, using a fake clipboard and scripted keyboard input."""

from __future__ import annotations

from pathlib import Path

import pytest

import evalschema as es
import make_run_sheet
import run_assistant as ra
import summarize_results


class FakeClipboard:
    def __init__(self, pastes: list[str]):
        self.pastes = list(pastes)
        self.copied: list[str] = []

    def copy(self, text: str) -> None:
        self.copied.append(text)

    def paste(self) -> str:
        return self.pastes.pop(0)


def scripted(answers: list[str]):
    queue = list(answers)

    def read(_prompt: str) -> str:
        if not queue:
            raise EOFError
        return queue.pop(0)
    return read


def make_run(tmp_path: Path, conditions: str = "A_normal,C_skill") -> Path:
    make_run_sheet.main(["--run-id", "assist", "--cases", "mech_001,neg_001", "--conditions", conditions,
                         "--seed", "2", "--runs-dir", str(tmp_path)])
    return tmp_path / "assist"


SESSION = ["claude.ai web", "Model X", "off", "tester"]


def rows_by_id(run: Path) -> dict[str, dict]:
    return {r["row_id"]: r for r in es.read_csv(run / "run_sheet.csv")[1]}


def test_full_session_saves_responses_and_fills_the_sheet(tmp_path):
    run = make_run(tmp_path)
    clip = FakeClipboard(["Answer one", "Answer two", "Answer three", "Answer four"])
    answers = [*SESSION, "ok", "", "", "ok", "", "y", "", "explanation-examples.md", "", "n", ""]
    out: list[str] = []
    assert ra.run(run, clipboard=clip, read=scripted(answers), write=out.append, today="2026-11-01") == 0

    rows = rows_by_id(run)
    ordered = sorted(rows.values(), key=lambda r: int(r["order"]))
    assert [r["batch"] for r in ordered] == ["skill_off", "skill_off", "skill_on", "skill_on"]
    for row, text in zip(ordered, ["Answer one", "Answer two", "Answer three", "Answer four"]):
        assert (run / row["response_file"]).read_text(encoding="utf-8") == text + "\n"
        assert (row["date"], row["surface"], row["model_label"], row["thinking_setting"], row["operator"]) == \
            ("2026-11-01", "claude.ai web", "Model X", "off", "tester")
    assert [r["activation_observed"] for r in ordered] == ["na", "na", "yes", "no"]
    assert ordered[2]["references_loaded"] == "explanation-examples.md"
    assert ordered[2]["activation_evidence"] == ra.DEFAULT_EVIDENCE["yes"]
    assert ordered[2]["skill_zip_sha256"], "skill rows record the build hash"

    expected_messages = [(run / r["message_file"]).read_text(encoding="utf-8") for r in ordered]
    assert clip.copied == expected_messages, "each message is copied in run-sheet order"
    assert any("turned OFF" in line for line in out) and any("turned ON" in line for line in out)

    _, issues = summarize_results.summarize(run, n_boot=10)
    assert issues.errors == [], "a completed run passes the completeness check"


def test_bad_clipboard_content_is_rejected_until_a_real_answer_arrives(tmp_path):
    run = make_run(tmp_path, conditions="A_normal")
    first = sorted(rows_by_id(run).values(), key=lambda r: int(r["order"]))[0]
    message = (run / first["message_file"]).read_text(encoding="utf-8")
    clip = FakeClipboard(["", message, "Real answer", "Real answer", "Second answer"])
    out: list[str] = []
    answers = [*SESSION, "ok", "", "", "", "", ""]
    ra.run(run, clipboard=clip, read=scripted(answers), write=out.append)
    text = "\n".join(out)
    assert "clipboard is empty" in text
    assert "still holds the message you sent" in text
    assert "same text as the previous saved response" in text
    saved = sorted(rows_by_id(run).values(), key=lambda r: int(r["order"]))
    assert (run / saved[0]["response_file"]).read_text(encoding="utf-8") == "Real answer\n"
    assert (run / saved[1]["response_file"]).read_text(encoding="utf-8") == "Second answer\n"


def test_quit_keeps_progress_and_resume_skips_done_rows(tmp_path):
    run = make_run(tmp_path)
    ra.run(run, clipboard=FakeClipboard(["First"]), read=scripted([*SESSION, "ok", "", "q"]), write=lambda _: None)
    done = [r for r in rows_by_id(run).values() if ra.response_done(run, r)]
    assert len(done) == 1

    clip = FakeClipboard(["Second"])
    out: list[str] = []
    # Pressing Enter at each session prompt accepts the values from the saved rows.
    ra.run(run, clipboard=clip, read=scripted(["", "", "", "", "ok", "", "q"]), write=out.append)
    rows = rows_by_id(run)
    assert sum(ra.response_done(run, r) for r in rows.values()) == 2
    assert {r["model_label"] for r in rows.values() if r["date"]} == {"Model X"}
    assert any("1/4 responses already saved" in line for line in out)


def test_eof_is_treated_as_quit(tmp_path):
    run = make_run(tmp_path)
    assert ra.run(run, clipboard=FakeClipboard([]), read=scripted(SESSION), write=lambda _: None) == 0
    assert not any(ra.response_done(run, r) for r in rows_by_id(run).values())


def test_skip_note_and_recopy(tmp_path):
    run = make_run(tmp_path, conditions="A_normal")
    clip = FakeClipboard(["Kept answer"])
    answers = [*SESSION, "ok", "s", "c", "n regenerated once after a network error", "", "q"]
    ra.run(run, clipboard=clip, read=scripted(answers), write=lambda _: None)
    ordered = sorted(rows_by_id(run).values(), key=lambda r: int(r["order"]))
    assert not ra.response_done(run, ordered[0]), "skipped row stays pending"
    assert ra.response_done(run, ordered[1])
    assert ordered[1]["notes"] == "regenerated once after a network error"
    assert len(clip.copied) == 3, "message copied for row 1, row 2, and once more on 'c'"


def test_batch_filter_and_nothing_to_do(tmp_path):
    run = make_run(tmp_path)
    out: list[str] = []
    clip = FakeClipboard(["One", "Two"])
    answers = [*SESSION, "ok", "", "y", "", "", "", "n", ""]
    ra.run(run, clipboard=clip, read=scripted(answers), write=out.append, batch="skill_on")
    rows = rows_by_id(run).values()
    assert {r["batch"] for r in rows if ra.response_done(run, r)} == {"skill_on"}
    out.clear()
    assert ra.run(run, clipboard=FakeClipboard([]), read=scripted([]), write=out.append, batch="skill_on") == 0
    assert any("Nothing to do" in line for line in out)


def test_batch_gate_requires_ok(tmp_path):
    run = make_run(tmp_path, conditions="A_normal")
    out: list[str] = []
    ra.run(run, clipboard=FakeClipboard(["x"]), read=scripted([*SESSION, "yes", "ok", "", "q"]), write=out.append)
    assert any("Change the skill setting first" in line for line in out)


def test_session_requires_values_and_warns_on_model_change(tmp_path):
    run = make_run(tmp_path, conditions="A_normal")
    ra.run(run, clipboard=FakeClipboard(["a"]), read=scripted([*SESSION, "ok", "", "q"]), write=lambda _: None)
    out: list[str] = []
    ra.run(run, clipboard=FakeClipboard([]), read=scripted(["", "Other model", "", ""]), write=out.append)
    assert any("Mixing models invalidates" in line for line in out)


def test_missing_run_sheet(tmp_path):
    out: list[str] = []
    assert ra.run(tmp_path / "none", clipboard=FakeClipboard([]), read=scripted([]), write=out.append) == 1
    assert "make_run_sheet.py" in out[0]


@pytest.mark.parametrize("response, message, previous, fragment", [
    ("", "msg", None, "empty"),
    ("msg", "msg\n", None, "still holds the message"),
    ("same", "msg", "same", "previous saved response"),
    ("fine", "msg", "other", None),
])
def test_check_response(response, message, previous, fragment):
    problem = ra.check_response(response, message, previous)
    assert (problem is None) if fragment is None else (fragment in problem)


def test_normalize_line_endings():
    assert ra.normalize("\r\n a\r\nb\r") == "a\nb"
