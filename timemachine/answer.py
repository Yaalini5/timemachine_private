"""Baseline (M2) answerer: retrieve top-k, then answer or refuse with clause-level citations.

Deliberately naive: no temporal filter, no conflict detection, no escalation. Its only decisions
are `answer` and `refuse`. M3/M4 add the rest; the gap is what the evaluation report measures.
"""
from dataclasses import dataclass, field
from datetime import date

from .index import HybridIndex

PROMPT = """You are a corporate policy assistant. Answer ONLY from the policy clauses below.

Question: {question}
(Question date: {as_of})

Clauses:
{clauses}

Rules:
- Cite the exact clause id(s) you relied on, copied verbatim from the list (e.g. "D003:C1").
- If the clauses do not answer the question, set decision to "refuse" and cite nothing.
- Do not use outside knowledge.

Reply as JSON: {{"decision": "answer" | "refuse", "answer": "<text>", "citations": ["<clause id>", ...]}}"""

# Offline backend only: refuse when the best dense similarity is below this (crude, documented).
OFFLINE_REFUSE_BELOW = 0.20


@dataclass
class Result:
    decision: str  # answer | refuse (M4 adds clarify | escalate | conflict)
    answer: str
    citations: list[str]
    retrieved: list[str] = field(default_factory=list)


class BaselineAnswerer:
    def __init__(self, index: HybridIndex, llm=None, k: int = 5):
        self.index, self.llm, self.k = index, llm, k

    def run(self, question: str, as_of: date | None) -> Result:
        hits = self.index.search_corpus(question, as_of, self.k)  # as_of ignored on purpose (M2)
        retrieved = [h.clause.clause_id for h in hits]
        if self.llm is None:  # offline extractive baseline: quote the top clause
            top = hits[0]
            if top.dense < OFFLINE_REFUSE_BELOW:
                return Result("refuse", "", [], retrieved)
            return Result("answer", top.clause.text, [top.clause.clause_id], retrieved)
        clauses = "\n".join(f"[{h.clause.clause_id}] {h.clause.text}" for h in hits)
        out = self.llm.generate_json(PROMPT.format(question=question, as_of=as_of.isoformat() if as_of else "not given", clauses=clauses))
        cites = [c for c in out.get("citations", []) if isinstance(c, str)]
        decision = "refuse" if out.get("decision") == "refuse" else "answer"
        return Result(decision, str(out.get("answer", "")), cites, retrieved)
