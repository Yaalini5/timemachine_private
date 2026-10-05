# AI-use appendix

| Assistant | Used for | Kept | Rejected / had to fix |
|---|---|---|---|
| Claude Code (Anthropic) | Explained the brief; scaffolded M2 (ingest, hybrid index, baseline, eval harness, tests) | Module split, RRF fusion, eval metrics | See below |

**Integrity note:** while checking how many gold questions have no `as_of_date`, a helper script also printed two rows from the sealed held-out file (Q004 and Q058: the metadata only, no answers tuned against). They were not used for tuning. All eval scripts now read dev only.
