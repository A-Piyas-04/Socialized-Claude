"""Stand-in for `claude -p --output-format stream-json` used by tests/test_collect_cc.py.

Behaviour is chosen by FAKE_CLAUDE_MODE:
  normal             honour skillOverrides; invoke the Skill tool when asked to use the skill
  ignore_overrides   list the skill even when --settings turns it off
  read_skill_off     with the skill off, Read its SKILL.md anyway
  ratelimit          always fail with a 429
  ratelimit_once     fail with a 429 on the first call (counter in FAKE_CLAUDE_STATE), then succeed
  auth               fail as "Not logged in"
  apikey             report apiKeySource ANTHROPIC_API_KEY
  no_init            never emit the init event
Every call appends its argv and cwd to FAKE_CLAUDE_LOG when set.
"""

import json
import os
import sys
from pathlib import Path


def emit(event: dict) -> None:
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def main() -> int:
    args = sys.argv[1:]
    mode = os.environ.get("FAKE_CLAUDE_MODE", "normal")
    message = sys.stdin.buffer.read().decode("utf-8")
    log = os.environ.get("FAKE_CLAUDE_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as stream:
            stream.write(json.dumps({"argv": args, "cwd": os.getcwd(),
                                     "config": os.environ.get("CLAUDE_CONFIG_DIR"),
                                     "has_token": bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"))}) + "\n")
    settings = json.loads(Path(args[args.index("--settings") + 1]).read_text(encoding="utf-8"))
    installed = (Path.cwd() / ".claude" / "skills" / "explanation-lab" / "SKILL.md").is_file()
    off = settings.get("skillOverrides", {}).get("explanation-lab") == "off"
    listed = installed and (not off or mode == "ignore_overrides")
    skills = ["deep-research", "debug"] + (["explanation-lab"] if listed else [])
    tools = args[args.index("--tools") + 1].split(",")
    if mode != "no_init":
        emit({"type": "system", "subtype": "init", "tools": tools, "skills": skills,
              "slash_commands": list(skills), "model": "claude-fake-1", "claude_code_version": "9.9.9",
              "permissionMode": "dontAsk", "apiKeySource": "ANTHROPIC_API_KEY" if mode == "apikey" else "none"})

    state = os.environ.get("FAKE_CLAUDE_STATE")
    if mode == "ratelimit_once" and state:
        count = int(Path(state).read_text()) if Path(state).exists() else 0
        Path(state).write_text(str(count + 1))
        if count == 0:
            mode = "ratelimit"
    if mode == "ratelimit":
        emit({"type": "result", "subtype": "success", "is_error": True, "api_error_status": 429,
              "result": "API Error: 429 rate limit reached"})
        return 1
    if mode == "auth":
        emit({"type": "assistant", "error": "authentication_failed",
              "message": {"content": [{"type": "text", "text": "Not logged in · Please run /login"}]}})
        emit({"type": "result", "subtype": "success", "is_error": True, "result": "Not logged in · Please run /login"})
        return 1
    if listed and "explanation-lab skill" in message:
        emit({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "explanation-lab"}}]}})
    if mode == "read_skill_off" and off:
        emit({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read",
             "input": {"file_path": str(Path.cwd() / ".claude/skills/explanation-lab/SKILL.md")}}]}})
    answer = f"Fake answer to: {message.strip().splitlines()[-1]}"
    emit({"type": "assistant", "message": {"content": [{"type": "text", "text": answer}]}})
    emit({"type": "result", "subtype": "success", "is_error": False, "result": answer, "num_turns": 1,
          "duration_ms": 5, "usage": {"output_tokens": 7}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
