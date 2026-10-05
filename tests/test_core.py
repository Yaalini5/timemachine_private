import subprocess
import sys
from datetime import date

from eval import score
from timemachine.index import HybridIndex
from timemachine.ingest import load_corpus


def test_ingest_counts():
    clauses = load_corpus()
    assert len({c.doc_id for c in clauses}) == 44
    assert all(c.clause_id.startswith(c.doc_id + ":") for c in clauses)


def test_in_force_window_boundaries():
    c = next(c for c in load_corpus() if c.clause_id == "D001:C1")  # 2021-01-01 .. 2022-06-30
    assert c.in_force(date(2021, 1, 1)) and c.in_force(date(2022, 6, 30))
    assert not c.in_force(date(2020, 12, 31)) and not c.in_force(date(2022, 7, 1))


def test_allowed_hook_restricts_retrieval():
    ix = HybridIndex(load_corpus(), "tfidf")
    hits = ix.search_corpus("work from home days per week", None, 5, allowed={"D003"})
    assert hits and all(h.clause.doc_id == "D003" for h in hits)


def test_score_basic():
    rows = [
        {"label": "answerable", "governing": ["A:C1"], "decision": "answer", "citations": ["A:C1"], "retrieved": ["A:C1"]},
        {"label": "refuse", "governing": [], "decision": "answer", "citations": ["B:C1"], "retrieved": ["B:C1"]},
    ]
    s = score(rows)
    assert s["faithfulness"] == 1.0 and s["refusal_acc"] == 0.0 and s["hit@1"] == 1.0


def test_heldout_is_sealed():
    r = subprocess.run([sys.executable, "eval.py", "--split", "heldout", "--backend", "offline"], capture_output=True, text=True)
    assert r.returncode != 0 and "sealed" in (r.stderr + r.stdout)
