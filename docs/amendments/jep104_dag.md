# JEP-104 — multi-parent (DAG) taxonomy: a concept can have several parents

## Why
Real taxonomies are DAGs: a poodle is BOTH a dog and a pet. The engine's single-parent dict silently OVERWROTE
(second "is a" lost the first). Make parents: dict[str, set]; ancestors = transitive closure across all parents.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 multi-parent works; is_a True across all lineages; 15 tests stay green. MOST-LIKELY MISS: explain chain (BFS)
  or WH 'what is X' (parents now a set).

## Result — capability PASS, but a MISS on the "tests stay green" prediction
DAG battery 7/7: poodle parents {dog,pet}; is_a poodle->dog, ->pet, ->animal (via dog), ->owned (via pet),
->living thing; "what is a poodle?" -> "A poodle is a dog and a pet." explain picks a shortest path (BFS).
BUT the prediction that "15 tests stay green" was WRONG: my predicted risks (explain/WH) actually WORKED; the real
break was TESTS/RUNNERS that inspect parents.get() as a STRING (now a set) — and it took TWO fix rounds to find all
of them. CALIBRATION: MISS (failure-location); tally 10/16. LESSON: a data-structure TYPE change breaks EVERY
reader of that structure - grep for all readers (tests, runners, logic) before predicting green, don't just reason
about the logic. Gate caught it both rounds. Established (DAG transitive closure; concept reasoner already DAG,
JEP-51), named; no novelty. HONEST: single-path explanation for multi-parent (picks one shortest path).
