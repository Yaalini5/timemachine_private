# Decision log

Every non-obvious choice, with the alternatives rejected. Graded; it is the script for the viva.

| # | Milestone | Decision | Why | Rejected alternatives |
|---|---|---|---|---|
| 1 | M0 | LangGraph for orchestration (from charter) | Pipeline is a directed graph with a 4-way branch | ADK, OpenAI Agents SDK, CrewAI, AutoGen (see charter §4) |
| 2 | M2 | Gemini free tier for answering AND embeddings, including the final run | Team decision: no local models. One provider keeps setup identical on every laptop | Ollama (laptop RAM/speed), OpenRouter free (models rotate, tight limits), HF (setup cost) |
| 3 | M2 | temperature 0 + pinned model names in `.env` + on-disk response cache (`.cache/`) | Hosted models drift; the cache replays identical (model, prompt) pairs, so `make eval` is reproducible and spends no extra quota | Uncached calls (non-reproducible numbers, burns free quota) |
| 4 | M2 | Chunk = one clause (`D003:C1`) | Clause is the unit of citation, so retrieval granularity equals evaluation granularity. Corpus clauses are 1-2 sentences, so there is nothing to split | Fixed-size token chunks (cannot cite a clause id) |
| 5 | M2 | Index text = document title + clause text | Short clauses lose their policy name otherwise ("Employees may ... 2 days" is ambiguous) | Clause text only |
| 6 | M2 | Hybrid BM25 + dense, fused by Reciprocal Rank Fusion (k=60), top-k=5 | Rank-based fusion needs no score calibration between the two retrievers. hit@5 is 98% on dev, so k=5 is enough | Weighted score sum (needs calibration), dense only |
| 7 | M2 | Baseline ignores `as_of_date` on purpose | M2 must fail T1/T3 so M3's gain is measurable | n/a |
| 8 | M2 | Missing `as_of_date` means "currently in force" (dev Q005 expects the current doc). M3 will resolve it to today | Matches the gold set convention | Ask the user (kept for M4's clarify path) |
| 9 | M2 | Sunset date is inclusive (last valid day) | Matches `metadata.csv`, e.g. D001 sunset 2022-06-30, D002 effective 2022-07-01 | Exclusive end |
| 10 | M2 | Operational definition of **faithful**: answered AND cites >=1 gold governing clause AND every citation was in the retrieved set | Catches stale-version citations (T1/T3) and invented ids | Judge-LLM scoring (circular, costs quota) |
| 11 | M2 | `offline` backend (TF-IDF + extractive answerer) exists only to test the harness without a key | Lets tests and CI run with no network. Never used for reported numbers | Mocking the API |
| 12 | M2 | Held-out split sealed in code: needs `--split heldout --final` | Brief requires it be unseen until M5 | Honour system |

## Known limits of the M2 metrics
- `decision_acc` is inflated by the share of answerable questions (about 75% of dev). Read it per trap.
- Answer *text* correctness is not scored yet, only citation correctness. Add an LLM-judge or exact-match check in M5 if time allows.
