"""Indexer + hybrid retriever (BM25 + dense vectors fused with Reciprocal Rank Fusion).

search_corpus(query, as_of_date, k) is the agent tool from brief A.6. In M2 (baseline) the
as_of_date is deliberately IGNORED: that is the T1/T3 failure M3 fixes. M3 plugs in through
the `allowed` hook (a set of doc_ids from the temporal filter), so retrieval needs no rewrite.
"""
import re
from dataclasses import dataclass
from datetime import date

import numpy as np
from rank_bm25 import BM25Okapi

from .embed import make_embedder
from .ingest import Clause

RRF_K = 60
_tok = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _tok.findall(text.lower())


@dataclass
class Hit:
    clause: Clause
    score: float  # fused RRF score
    dense: float  # cosine similarity (used by the offline refusal threshold)
    rank: int


class HybridIndex:
    def __init__(self, clauses: list[Clause], backend: str = "gemini"):
        self.clauses = clauses
        self.by_id = {c.clause_id: c for c in clauses}
        # Index text = title + clause text so clauses stay findable by policy name.
        self.texts = [f"{c.title}. {c.text}" for c in clauses]
        self.bm25 = BM25Okapi([tokenize(t) for t in self.texts])
        self.embedder = make_embedder(backend)
        self.embedder.fit(self.texts)
        self.matrix = self.embedder.embed_docs(self.texts)

    def get_clause(self, clause_id: str) -> Clause:
        return self.by_id[clause_id]

    def search_corpus(
        self, query: str, as_of_date: date | None = None, k: int = 5, allowed: set[str] | None = None
    ) -> list[Hit]:
        sparse = self.bm25.get_scores(tokenize(query))
        dense = self.matrix @ self.embedder.embed_queries([query])[0]
        mask = np.array([allowed is None or c.doc_id in allowed for c in self.clauses])
        fused = np.zeros(len(self.clauses))
        for scores in (sparse, dense):
            order = np.argsort(-scores, kind="stable")
            for rank, i in enumerate([i for i in order if mask[i]]):
                fused[i] += 1.0 / (RRF_K + rank + 1)
        top = [i for i in np.argsort(-fused, kind="stable") if mask[i]][:k]
        return [Hit(self.clauses[i], float(fused[i]), float(dense[i]), r + 1) for r, i in enumerate(top)]
