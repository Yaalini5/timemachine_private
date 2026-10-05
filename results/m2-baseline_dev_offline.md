# Eval: m2-baseline | split=dev | backend=offline

| slice | n | hit@1 | hit@3 | hit@5 | faithfulness | refusal_acc | false_refusal | decision_acc |
|---|---|---|---|---|---|---|---|---|
| ALL | 56 | 0.54 | 0.94 | 0.98 | 0.535 | 0.167 | 0.0 | 0.786 |
| trap T1 | 1 | 0.0 | 1.0 | 1.0 | 0.0 | - | 0.0 | 1.0 |
| trap T2 | 3 | 0.667 | 1.0 | 1.0 | - | - | - | 0.0 |
| trap T3 | 6 | 0.4 | 1.0 | 1.0 | 0.4 | 0.0 | 0.0 | 0.833 |
| trap T4 | 5 | - | - | - | - | 0.2 | - | 0.2 |
| trap T5 | 4 | 0.5 | 1.0 | 1.0 | - | - | - | 0.0 |
| trap none | 37 | 0.568 | 0.919 | 0.973 | 0.568 | - | 0.0 | 1.0 |

## Misses (32)

| id | trap | label | as_of | decision | gold | cited |
|---|---|---|---|---|---|---|
| Q002 | none | answerable | 2023-01-10 | answer | D002:C1 | D001:C1 |
| Q003 | none | answerable | 2024-03-01 | answer | D003:C1 | D001:C1 |
| Q005 | T1 | answerable | none | answer | D014:C1,D014:C2,D014:C3 | D012:C1 |
| Q006 | T3 | answerable | 2024-03-01 | answer | D013:C3 | D014:C3 |
| Q010 | none | answerable | 2024-01-01 | answer | D010:C1 | D009:C1 |
| Q012 | T3 | answerable | 2023-11-01 | answer | D019:C2 | D020:C1 |
| Q015 | T4 | refuse | 2025-06-01 | answer | - | D009:C2 |
| Q017 | T5 | escalate | 2023-06-01 | answer | D004:C2,D025:C2 | D004:C1 |
| Q020 | none | answerable | 2023-01-01 | answer | D006:C1 | D005:C1 |
| Q021 | none | answerable | 2024-06-01 | answer | D007:C1 | D005:C1 |
| Q025 | none | answerable | 2022-05-01 | answer | D006:C4 | D005:C4 |
| Q026 | none | answerable | 2024-08-01 | answer | D007:C3 | D005:C4 |
| Q027 | none | answerable | 2022-06-01 | answer | D027:C1 | D028:C1 |
| Q030 | none | answerable | 2024-01-01 | answer | D028:C2 | D027:C2 |
| Q033 | none | answerable | 2022-01-01 | answer | D015:C1 | D016:C1 |
| Q038 | none | answerable | 2022-01-01 | answer | D021:C1 | D022:C1 |
| Q040 | none | answerable | 2023-01-01 | answer | D021:C3 | D022:C3 |
| Q042 | none | answerable | 2024-06-01 | answer | D024:C2 | D023:C2 |
| Q043 | T3 | refuse | 2022-06-01 | answer | - | D024:C3 |
| Q049 | none | answerable | 2024-01-01 | answer | D038:C1 | D037:C1 |
| Q056 | T4 | refuse | 2022-01-01 | answer | - | D036:C3 |
| Q059 | T3 | answerable | 2023-01-01 | answer | D030:C1,D030:C2 | D031:C3 |
| Q061 | T2 | conflict | 2024-01-01 | answer | D017:C2,D041:C1 | D015:C2 |
| Q063 | T2 | conflict | 2024-10-20 | answer | D036:C2,D043:C1 | D043:C1 |
| Q064 | T2 | conflict | 2024-09-01 | answer | D014:C3,D044:C1 | D044:C1 |
| Q065 | T4 | refuse | 2025-06-01 | answer | - | D001:C2 |
| Q067 | T4 | refuse | 2025-06-01 | answer | - | D009:C2 |
| Q068 | T5 | escalate | 2025-06-01 | answer | D007:C1 | D007:C1 |
| Q070 | T5 | escalate | 2025-06-01 | answer | D024:C1,D025:C2 | D024:C1 |
| Q071 | T5 | escalate | 2025-06-01 | answer | D038:C1 | D037:C1 |
| Q073 | none | answerable | 2025-06-01 | answer | D024:C1 | D023:C1 |
| Q074 | none | answerable | 2024-01-01 | answer | D028:C1 | D027:C1 |
