"""Judge backends for the automated screening instruments (judge.py, screen_items.py).

The default backend is the Google AI Studio free tier (a non-Anthropic model):

    GEMINI_API_KEY   AI Studio key (read from the environment only; never written anywhere)
    JUDGE_BACKEND    "gemini" (default)
    JUDGE_MODEL      model name, default DEFAULT_GEMINI_MODEL

Every backend implements one method, complete(prompt, temperature) -> str. Calls are cached
on disk by a hash of (backend, model, temperature, sample, prompt), so a rerun after a quota
stop resumes without repeating work. The cache holds model output only, never the key.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Protocol

DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
KEY_ENV = "GEMINI_API_KEY"
RETRY_STATUSES = {429, 500, 503}


class JudgeError(RuntimeError):
    pass


class JudgeUnavailable(JudgeError):
    """Quota or service exhausted after retries; progress is cached and the run can resume."""


class Backend(Protocol):
    name: str
    model: str

    def complete(self, prompt: str, temperature: float) -> str: ...


class GeminiBackend:
    name = "gemini"

    def __init__(self, api_key: str, model: str = DEFAULT_GEMINI_MODEL, *, min_interval: float = 6.0,
                 max_retries: int = 5, backoff: float = 20.0, sleep: Callable[[float], None] = time.sleep,
                 opener: Callable = urllib.request.urlopen) -> None:
        if not api_key:
            raise JudgeError(f"{KEY_ENV} is not set")
        self._key, self.model = api_key, model
        self._min_interval, self._max_retries, self._backoff = min_interval, max_retries, backoff
        self._sleep, self._open = sleep, opener
        self._last = 0.0
        self.log: Callable[[str], None] = lambda message: print(message, file=sys.stderr, flush=True)

    def complete(self, prompt: str, temperature: float) -> str:
        body = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"},
        }).encode("utf-8")
        for attempt in range(self._max_retries + 1):
            wait = self._min_interval - (time.monotonic() - self._last)
            if wait > 0:
                self._sleep(wait)
            self._last = time.monotonic()
            request = urllib.request.Request(GEMINI_URL.format(model=self.model), data=body, method="POST",
                                             headers={"Content-Type": "application/json",
                                                      "x-goog-api-key": self._key})
            try:
                with self._open(request, timeout=300) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in RETRY_STATUSES and attempt < self._max_retries:
                    wait = self._backoff * (2 ** attempt)
                    self.log(f"judge HTTP {exc.code}; retry {attempt + 1}/{self._max_retries} in {wait:.0f}s")
                    self._sleep(wait)
                    continue
                if exc.code in RETRY_STATUSES:
                    raise JudgeUnavailable(f"judge HTTP {exc.code} after {attempt + 1} attempts") from None
                raise JudgeError(f"judge HTTP {exc.code}: {exc.reason}") from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self._max_retries:
                    self.log(f"judge network error ({getattr(exc, 'reason', exc)}); retry {attempt + 1}")
                    self._sleep(self._backoff * (2 ** attempt))
                    continue
                raise JudgeUnavailable(f"judge unreachable: {exc.reason}") from None
            try:
                return "".join(p.get("text", "") for p in payload["candidates"][0]["content"]["parts"])
            except (KeyError, IndexError, TypeError):
                raise JudgeError(f"judge returned no text (finish: {json.dumps(payload)[:200]})") from None
        raise JudgeUnavailable("judge retries exhausted")


def backend_from_env(env: dict[str, str] | None = None, **kwargs) -> Backend:
    env = dict(os.environ) if env is None else env
    kind = env.get("JUDGE_BACKEND", "gemini")
    if kind != "gemini":
        raise JudgeError(f"unknown JUDGE_BACKEND '{kind}'")
    if not env.get(KEY_ENV):
        raise JudgeError(f"{KEY_ENV} is not set. Create a free key at Google AI Studio and set it in this "
                         "shell's environment (never in a file inside the repository).")
    return GeminiBackend(env[KEY_ENV], env.get("JUDGE_MODEL", DEFAULT_GEMINI_MODEL), **kwargs)


class CachedJudge:
    """Wraps a backend with an on-disk cache keyed by the exact request."""

    def __init__(self, backend: Backend, cache_dir: Path, progress: bool = False) -> None:
        self.backend, self.cache_dir, self.progress = backend, cache_dir, progress
        self.calls = self.hits = 0

    def ask(self, prompt: str, *, temperature: float = 0.0, sample: int = 0) -> str:
        key = hashlib.sha256(json.dumps([self.backend.name, self.backend.model, temperature, sample, prompt])
                             .encode("utf-8")).hexdigest()
        path = self.cache_dir / key[:2] / f"{key}.json"
        if path.is_file():
            self.hits += 1
            return json.loads(path.read_text(encoding="utf-8"))["text"]
        started = time.monotonic()
        text = self.backend.complete(prompt, temperature)
        self.calls += 1
        if self.progress:
            print(f"judge call {self.calls} ({time.monotonic() - started:.0f}s)", file=sys.stderr, flush=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json.dumps({"backend": self.backend.name, "model": self.backend.model,
                                     "temperature": temperature, "sample": sample, "text": text},
                                    sort_keys=True).encode("utf-8"))
        return text


def parse_json_object(text: str) -> dict:
    """The first JSON object in a model reply (tolerates code fences and surrounding prose)."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        value = json.loads(cleaned)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    while start != -1:
        depth = 0
        for end in range(start, len(text)):
            depth += {"{": 1, "}": -1}.get(text[end], 0)
            if depth == 0:
                try:
                    value = json.loads(text[start:end + 1])
                    if isinstance(value, dict):
                        return value
                except json.JSONDecodeError:
                    pass
                break
        start = text.find("{", start + 1)
    raise JudgeError(f"no JSON object in judge reply: {text[:120]!r}")
