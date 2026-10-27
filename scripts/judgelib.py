"""Judge backends for the automated screening instruments (judge.py, screen_items.py).

All backends are non-Anthropic models on free tiers. Keys are read from the environment only and
never written anywhere.

    JUDGE_BACKEND    "groq" (default) or "gemini"
    GROQ_API_KEY     Groq key, for the groq backend (OpenAI-compatible API)
    GEMINI_API_KEY   Google AI Studio key, for the gemini backend (Gemini and Gemma models)
    JUDGE_MODEL      model name; defaults: DEFAULT_GROQ_MODEL, DEFAULT_GEMINI_MODEL

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

# Free tier, 2026-10-27: Pro-class models have no quota, gemini-3.8-flash mostly returns 503, and
# gemini-3.6-flash is capped at 20 requests/day/model, far below a sweep's ~1,300 calls. 2.5-flash
# is served with a usable quota; forced-choice pairwise with both-order control, not model strength,
# is what removes the archive judge's ceiling.
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
KEY_ENV = "GEMINI_API_KEY"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_KEY_ENV = "GROQ_API_KEY"
# Confirm against GET https://api.groq.com/openai/v1/models when the key is first used.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
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
        config = {"temperature": temperature}
        if not self.model.startswith("gemma"):
            config["responseMimeType"] = "application/json"
        body = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": config,
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
                daily = daily_quota(exc)
                if daily:
                    raise JudgeUnavailable(f"free-tier daily quota for {self.model} exhausted ({daily} requests "
                                           "per day); not retrying until it resets") from None
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
            served = str(payload.get("modelVersion") or "")
            if served and not served.startswith(self.model):
                raise JudgeError(f"requested {self.model} but the service answered with {served}; "
                                 "set JUDGE_MODEL to the model actually served")
            try:
                return "".join(p.get("text", "") for p in payload["candidates"][0]["content"]["parts"])
            except (KeyError, IndexError, TypeError):
                raise JudgeError(f"judge returned no text (finish: {json.dumps(payload)[:200]})") from None
        raise JudgeUnavailable("judge retries exhausted")


class OpenAICompatibleBackend:
    """Chat-completions API (Groq). The key goes in the Authorization header, never in the URL."""

    def __init__(self, name: str, url: str, api_key: str, model: str, *, min_interval: float = 2.0,
                 max_retries: int = 5, backoff: float = 10.0, sleep: Callable[[float], None] = time.sleep,
                 opener: Callable = urllib.request.urlopen) -> None:
        if not api_key:
            raise JudgeError(f"no API key for the {name} backend")
        self.name, self.model, self._url, self._key = name, model, url, api_key
        self._min_interval, self._max_retries, self._backoff = min_interval, max_retries, backoff
        self._sleep, self._open = sleep, opener
        self._last = 0.0
        self.log: Callable[[str], None] = lambda message: print(message, file=sys.stderr, flush=True)

    def complete(self, prompt: str, temperature: float) -> str:
        body = json.dumps({"model": self.model, "temperature": temperature,
                           "messages": [{"role": "user", "content": prompt}],
                           "response_format": {"type": "json_object"}}).encode("utf-8")
        for attempt in range(self._max_retries + 1):
            wait = self._min_interval - (time.monotonic() - self._last)
            if wait > 0:
                self._sleep(wait)
            self._last = time.monotonic()
            request = urllib.request.Request(self._url, data=body, method="POST",
                                             headers={"Content-Type": "application/json",
                                                      "Authorization": f"Bearer {self._key}"})
            try:
                with self._open(request, timeout=300) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                message = error_message(exc)
                if exc.code == 429 and re.search(r"(?i)per day|\bRPD\b|\bTPD\b", message):
                    raise JudgeUnavailable(f"{self.name} daily limit for {self.model} reached "
                                           f"({message[:160]}); not retrying until it resets") from None
                if exc.code in RETRY_STATUSES and attempt < self._max_retries:
                    retry_after = exc.headers.get("retry-after") if exc.headers else None
                    wait = float(retry_after) if retry_after and retry_after.replace(".", "", 1).isdigit() \
                        else self._backoff * (2 ** attempt)
                    self.log(f"judge HTTP {exc.code}; retry {attempt + 1}/{self._max_retries} in {wait:.0f}s")
                    self._sleep(wait)
                    continue
                if exc.code in RETRY_STATUSES:
                    raise JudgeUnavailable(f"judge HTTP {exc.code} after {attempt + 1} attempts") from None
                raise JudgeError(f"judge HTTP {exc.code}: {message[:200]}") from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self._max_retries:
                    self.log(f"judge network error ({getattr(exc, 'reason', exc)}); retry {attempt + 1}")
                    self._sleep(self._backoff * (2 ** attempt))
                    continue
                raise JudgeUnavailable(f"judge unreachable: {getattr(exc, 'reason', exc)}") from None
            served = str(payload.get("model") or "")
            if served and served != self.model:
                raise JudgeError(f"requested {self.model} but the service answered with {served}; "
                                 "set JUDGE_MODEL to the model actually served")
            try:
                return str(payload["choices"][0]["message"]["content"] or "")
            except (KeyError, IndexError, TypeError):
                raise JudgeError(f"judge returned no text ({json.dumps(payload)[:200]})") from None
        raise JudgeUnavailable("judge retries exhausted")


def error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = json.loads(exc.read().decode("utf-8") or "{}")
    except (ValueError, OSError):
        return str(exc.reason)
    error = body.get("error", body)
    return str(error.get("message", exc.reason)) if isinstance(error, dict) else str(error)


def daily_quota(exc: urllib.error.HTTPError) -> str | None:
    """The per-day request limit named in a 429 body, if that is the limit that was hit."""
    if exc.code != 429:
        return None
    try:
        body = json.loads(exc.read().decode("utf-8") or "{}")
    except (ValueError, OSError):
        return None
    for detail in body.get("error", {}).get("details", []):
        for violation in detail.get("violations", []):
            if "PerDay" in str(violation.get("quotaId", "")):
                return str(violation.get("quotaValue", "?"))
    return None


def backend_from_env(env: dict[str, str] | None = None, **kwargs) -> Backend:
    env = dict(os.environ) if env is None else env
    kind = env.get("JUDGE_BACKEND", "groq")
    if kind == "groq":
        if not env.get(GROQ_KEY_ENV):
            raise JudgeError(f"{GROQ_KEY_ENV} is not set. Create a free key at console.groq.com and set it in "
                             "this shell's environment (never in a file inside the repository), or set "
                             "JUDGE_BACKEND=gemini.")
        return OpenAICompatibleBackend("groq", GROQ_URL, env[GROQ_KEY_ENV].strip(),
                                       env.get("JUDGE_MODEL", DEFAULT_GROQ_MODEL), **kwargs)
    if kind == "gemini":
        if not env.get(KEY_ENV):
            raise JudgeError(f"{KEY_ENV} is not set. Create a free key at Google AI Studio and set it in this "
                             "shell's environment (never in a file inside the repository).")
        return GeminiBackend(env[KEY_ENV], env.get("JUDGE_MODEL", DEFAULT_GEMINI_MODEL), **kwargs)
    raise JudgeError(f"unknown JUDGE_BACKEND '{kind}' (use groq or gemini)")


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
