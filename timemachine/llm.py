"""Gemini wrapper: temperature 0, on-disk response cache, rate-limit pacing and retries.

The cache is what makes a Gemini-only evaluation reproducible and quota-friendly: an identical
(model, prompt) pair is never sent twice, so re-running `make eval` replays the same answers.
"""
import hashlib
import json
import time
from pathlib import Path

from . import config


class DiskCache:
    def __init__(self, name: str):
        self.dir: Path = config.CACHE_DIR / name
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.dir / (hashlib.sha256(key.encode()).hexdigest() + ".json")

    def get(self, key: str):
        p = self._path(key)
        return json.loads(p.read_text()) if p.exists() else None

    def put(self, key: str, value) -> None:
        self._path(key).write_text(json.dumps(value))


_last_call = 0.0


def _pace() -> None:
    global _last_call
    wait = config.GEMINI_MIN_INTERVAL - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def _client():
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set (copy .env.example to .env), or use --backend offline.")
    from google import genai

    return genai.Client(api_key=config.GEMINI_API_KEY)


def with_retries(fn, attempts: int = 5):
    for i in range(attempts):
        try:
            _pace()
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(2 ** (i + 2))  # 4, 8, 16, 32s: free-tier 429s are usually per-minute


class GeminiLLM:
    def __init__(self, model: str = config.GEMINI_MODEL):
        self.model = model
        self.cache = DiskCache("llm")

    def generate_json(self, prompt: str) -> dict:
        key = f"{self.model}\n{prompt}"
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        from google.genai import types

        client = _client()
        resp = with_retries(
            lambda: client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"),
            )
        )
        try:
            out = json.loads(resp.text)
        except (json.JSONDecodeError, TypeError):
            out = {"decision": "refuse", "answer": "", "citations": [], "parse_error": True}
        self.cache.put(key, out)
        return out
