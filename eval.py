"""Evaluation harness. One command: `make eval`.

Metrics (definitions are logged in decision_log.md):
  hit@k          any gold governing clause in the top-k retrieved   (questions with gold clauses)
  faithfulness   answered AND cites >=1 gold governing clause AND every citation was retrieved
                 (answerable questions)
  refusal acc.   system refused (label=refuse)
  false refusal  system refused an answerable question
  decision acc.  system decision == gold label mapped to {answer, refuse, escalate, conflict}

The held-out split is sealed: it only runs with --split heldout --final, once, in M5.
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import date

from timemachine import config
from timemachine.answer import BaselineAnswerer
from timemachine.index import HybridIndex
from timemachine.ingest import load_corpus
from timemachine.llm import GeminiLLM

LABEL_TO_DECISION = {"answerable": "answer", "refuse": "refuse", "escalate": "escalate", "conflict": "conflict"}
KS = (1, 3, 5)


def load_gold(split: str) -> list[dict]:
    path = config.GOLD_DEV if split == "dev" else config.GOLD_HELDOUT
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def score(rows: list[dict]) -> dict:
    def rate(num, den):
        return round(num / den, 3) if den else None

    gold_rows = [r for r in rows if r["governing"]]
    ans_rows = [r for r in rows if r["label"] == "answerable"]
    ref_rows = [r for r in rows if r["label"] == "refuse"]
    out = {"n": len(rows)}
    for k in KS:
        out[f"hit@{k}"] = rate(sum(any(g in r["retrieved"][:k] for g in r["governing"]) for r in gold_rows), len(gold_rows))
    out["faithfulness"] = rate(
        sum(
            r["decision"] == "answer"
            and any(c in r["governing"] for c in r["citations"])
            and all(c in r["retrieved"] for c in r["citations"])
            for r in ans_rows
        ),
        len(ans_rows),
    )
    out["refusal_acc"] = rate(sum(r["decision"] == "refuse" for r in ref_rows), len(ref_rows))
    out["false_refusal"] = rate(sum(r["decision"] == "refuse" for r in ans_rows), len(ans_rows))
    out["decision_acc"] = rate(sum(r["decision"] == LABEL_TO_DECISION[r["label"]] for r in rows), len(rows))
    return out


def run(split: str, backend: str, k: int) -> list[dict]:
    index = HybridIndex(load_corpus(), backend)
    answerer = BaselineAnswerer(index, GeminiLLM() if backend == "gemini" else None, k)
    rows = []
    for q in load_gold(split):
        as_of = date.fromisoformat(q["as_of_date"]) if q["as_of_date"] else None  # None = "currently in force"
        res = answerer.run(q["question"], as_of)
        rows.append({**q, "decision": res.decision, "answer": res.answer, "citations": res.citations, "retrieved": res.retrieved})
    return rows


def report(rows: list[dict], split: str, backend: str, tag: str) -> str:
    cols = ["n", "hit@1", "hit@3", "hit@5", "faithfulness", "refusal_acc", "false_refusal", "decision_acc"]
    by_trap = defaultdict(list)
    for r in rows:
        by_trap[r["trap"]].append(r)
    lines = [f"# Eval: {tag} | split={split} | backend={backend}", "", "| slice | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for name, rs in [("ALL", rows)] + [(f"trap {t}", by_trap[t]) for t in sorted(by_trap)]:
        s = score(rs)
        lines.append(f"| {name} | " + " | ".join("-" if s[c] is None else str(s[c]) for c in cols) + " |")
    bad = [r for r in rows if r["decision"] != LABEL_TO_DECISION[r["label"]] or (r["governing"] and not any(g in r["citations"] for g in r["governing"]))]
    lines += ["", f"## Misses ({len(bad)})", "", "| id | trap | label | as_of | decision | gold | cited |", "|---|---|---|---|---|---|---|"]
    for r in bad:
        lines.append(f"| {r['id']} | {r['trap']} | {r['label']} | {r['as_of_date'] or 'none'} | {r['decision']} | {','.join(r['governing']) or '-'} | {','.join(r['citations']) or '-'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "heldout"], default="dev")
    ap.add_argument("--backend", choices=["gemini", "offline"], default="gemini" if config.GEMINI_API_KEY else "offline")
    ap.add_argument("--k", type=int, default=config.DEFAULT_K)
    ap.add_argument("--tag", default="m2-baseline")
    ap.add_argument("--final", action="store_true", help="required to touch the sealed held-out split (M5 only)")
    a = ap.parse_args()
    if a.split == "heldout" and not a.final:
        sys.exit("Held-out split is sealed until M5. Pass --final only for the one final run.")
    rows = run(a.split, a.backend, a.k)
    md = report(rows, a.split, a.backend, a.tag)
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stem = config.RESULTS_DIR / f"{a.tag}_{a.split}_{a.backend}"
    stem.with_suffix(".md").write_text(md)
    stem.with_suffix(".jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
