# JEP-236 — close the DAG boundary: multi-parent taxonomies in the substrate via slot-binding

Pre-registered 2026-06-05 (BEFORE the run). JEP-235 found the substrate relational store loses multi-parent (DAG)
edges: a key→value Hopfield is a FUNCTION (one attractor per key), so `poodle→dog` and `poodle→pet` collapse to one.
But the Understanding Engine's taxonomy IS a multi-parent DAG (`parents: dict[str, set]`). This BET closes the
boundary with the standard associative-multimap trick — SLOT-BINDING — and tests full DAG transitive closure
through the substrate.

## Method (no transformer; VSA slot-binding + Hopfield key→value, established, named)
- For a child with parents {p0, p1, …}, store each edge under a DISTINCT key `child_code ⊙ slot_i_code` → `p_i`,
  where slot_i are a few fixed random ±1 role codes (i = 0..MAXDEG-1). Each key is still a function (one value);
  multiplicity is carried by the slot index. (This is JEP-234 typing applied to edge multiplicity.)
- RECOVER parents(child): query `child ⊙ slot_0 … child ⊙ slot_{MAXDEG-1}`, keep retrievals whose overlap clears the
  confidence threshold (empty slots = low overlap → dropped).
- DAG is_a(x, y): BFS the ancestor set over multi-parent retrieval (branching walk, visited-set, depth cap).
- MAXDEG = 3. Read a multi-parent taxonomy FROM PROSE. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J236a | Multi-parent recovered | a 2-parent node returns BOTH parents through the substrate (both seeds) |
| J236b | DAG transitive closure matches symbolic | substrate DAG is_a vs symbolic on a battery (multi-parent positives + negatives) ≥ 0.90 (both seeds) |
| J236c | Above an untrained control | untrained net: match ≤ 0.60 (both seeds) |
| J236d | Capacity cost is bounded/known | within the reduced capacity (≈ J232-cliff / MAXDEG) the store holds; degradation begins only beyond it (report the number) |

PASS = J236a–c (the substrate now holds the engine's multi-parent DAG taxonomy and reasons over it); J236d records
the capacity cost. NULL (honest): J236a fails → slot-binding does not separate the edges (slot codes not distinct
enough); J236b fails → the branching walk desyncs or spurious slots inject false ancestors. No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J236a PASS — child⊙slot_0 and child⊙slot_1 are well-separated random keys (different slots → different bound
keys), each retrieving its own parent cleanly within capacity; J236b PASS (≥0.90, ~1.00) since each edge is a clean
single-valued attractor and the BFS reproduces the multi-parent closure; J236c control fails (≤0.60). J236d: the
slot scheme stores up to MAXDEG× more patterns, so the K≈20 cliff (J232) becomes ≈20 TOTAL edges still (each edge is
one pattern regardless of slot) — capacity is over total EDGES, ~20, not divided further (correction to my framing:
slot-binding adds keys, not patterns-per-edge; each edge is still one pattern). RISK (in-rung counter-checks): (i)
the confidence threshold must DROP empty slots (a child with 1 parent must not return a spurious 2nd from slot_1) —
verify a single-parent node returns exactly one; (ii) the BFS must dedupe and cap depth (diamond DAGs reconverge).
Established (VSA role/slot-binding, Hopfield CAM, BFS closure), named; no novelty — the value is closing the J235d
boundary so the substrate holds the engine's ACTUAL DAG taxonomy.

## RESULT (2026-06-05): PARTIAL/NULL — slot-binding recovers MULTIPLE (J236a) but the EMPTY-SLOT problem breaks closure

| seed | poodle parents | both? | DAG match | control | cat parents (should be ['pet']) |
|------|----------------|-------|-----------|---------|---------------------------------|
| 42 | dog, pet | ✓ | 0.68 | 0.50 | ['pet', 'animal'] ✗ |
| 7  | dog, mammal, pet | ✓ | 0.64 | 0.50 | ['pet', 'mammal'] ✗ |

- **J236a ✓** — slot-binding DOES store multiple parents: `poodle ⊙ slot_0/slot_1` recover dog AND pet. Multi-parent
  storage works.
- **J236b ✗** — DAG closure match only **0.64–0.68** (bar 0.90). **J236d ✗** — the single-parent node `cat` (only
  `cat→pet` stored) returns SPURIOUS extra parents ('animal'/'mammal').
- **J236c ✓** — control 0.50.

**DIAGNOSIS — the predicted-risk (counter-check i) materialized and my threshold FIX was wrong.** Querying an
UNTRAINED slot (`cat ⊙ slot_1`, cat having one parent) still returns a high-overlap parent: the value slot ALWAYS
relaxes to SOME stored attractor (the net's only value-slot attractors ARE the parent codes), so a value-overlap
threshold CANNOT distinguish a trained edge from a spurious key. Every empty slot injects a false parent → false
ancestors → closure corrupted, and single-parent nodes gain phantom parents. I FLAGGED this risk in the prediction
("the confidence threshold must DROP empty slots") but wrongly assumed the threshold would do it.

**CALIBRATION:** the right detector is not value-cleanliness but whether the (key,value) PAIR is a STORED attractor —
i.e. the ENERGY / self-consistency of the full settled pattern (trained edge = deep minimum; spurious slot = shallow,
the key was never an attractor). That's the JEP-237 fix. Lesson (extends error-class 3 "a metric must DISCRIMINATE
the failure mode"): to detect "was this key trained?", measure the KEY→VALUE BINDING energy, not the value's
cleanliness — in an attractor net the value is always clean. Verdict: **PARTIAL** (multi-parent STORAGE works,
J236a; multi-parent RETRIEVAL needs trained-edge detection, deferred to JEP-237). Pre-registered bar failed as
written — recorded, not retuned.
