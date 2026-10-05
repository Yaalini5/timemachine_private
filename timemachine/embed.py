"""Embedders behind one interface: embed_docs / embed_queries -> L2-normalised float32 matrix.

  gemini : Gemini embedding API (cached on disk). Used for real runs.
  tfidf  : offline TF-IDF (word 1-2grams). No network/key needed; for tests and harness checks.
"""
import numpy as np

from . import config
from .llm import DiskCache, _client, with_retries


def _norm(m: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(m, axis=1, keepdims=True)
    return (m / np.where(n == 0, 1, n)).astype(np.float32)


class GeminiEmbedder:
    name = "gemini"

    def __init__(self, model: str = config.GEMINI_EMBED_MODEL):
        self.model = model
        self.cache = DiskCache("emb")

    def _embed(self, texts: list[str], task: str) -> np.ndarray:
        from google.genai import types

        out, todo = {}, []
        for t in texts:
            hit = self.cache.get(f"{self.model}|{task}|{t}")
            if hit is None:
                todo.append(t)
            else:
                out[t] = hit
        client = _client() if todo else None
        for i in range(0, len(todo), 50):
            batch = todo[i : i + 50]
            resp = with_retries(
                lambda: client.models.embed_content(
                    model=self.model, contents=batch, config=types.EmbedContentConfig(task_type=task)
                )
            )
            for t, e in zip(batch, resp.embeddings):
                out[t] = list(e.values)
                self.cache.put(f"{self.model}|{task}|{t}", out[t])
        return _norm(np.array([out[t] for t in texts], dtype=np.float32))

    def fit(self, docs: list[str]) -> None:
        pass

    def embed_docs(self, texts):
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_queries(self, texts):
        return self._embed(texts, "RETRIEVAL_QUERY")


class TfidfEmbedder:
    name = "tfidf"

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")

    def fit(self, docs: list[str]) -> None:
        self.vec.fit(docs)

    def embed_docs(self, texts):
        return _norm(self.vec.transform(texts).toarray())

    def embed_queries(self, texts):
        return _norm(self.vec.transform(texts).toarray())


def make_embedder(backend: str):
    return GeminiEmbedder() if backend == "gemini" else TfidfEmbedder()
