# JEP-235 — CAPSTONE: the Understanding Engine reasons through the substrate, end-to-end from prose

Pre-registered 2026-06-05 (BEFORE the run). JEP-232/233/234 showed the substrate can store/chain/type relations in
isolation. This capstone closes the loop: READ real prose with the engine, STORE the extracted is-a taxonomy in the
substrate (EnergyNet), and ANSWER multi-hop "is X a Y?" by chaining retrievals THROUGH energy relaxation — the
engine's actual learn→reason→answer loop running on the substrate, not Python dicts. Plus an honest boundary test.

## Method (no transformer)
- `e = UnderstandingEngine(); e.read(passage)` → the symbolic is-a taxonomy (`e.parents`, ground truth).
- Encode: each concept → a random ±1 code (length 40); each is-a edge (child→parent) → a key→value attractor
  `concat(child_code, parent_code)` trained into one EnergyNet (the JEP-232 store).
- ANSWER `is_a_substrate(x, y)`: from x, iterate retrieval (re-clamp the recovered parent as the next key) up to
  depth D, collecting the ancestor set; return `y ∈ ancestors`. Compare to the symbolic `e.is_a(x, y)` (truth).
- Two taxonomies: a single-parent TREE (within ~20 edges) and a MULTI-PARENT case (a node with 2 parents).
  Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J235a | Engine reasons through substrate (tree) | substrate is_a matches symbolic on a battery (incl. multi-hop positives + negatives) ≥ 0.90 (both seeds) |
| J235b | End-to-end FROM PROSE | the taxonomy is the one `read()` extracted (not hand-built), and a depth≥3 positive resolves through the substrate |
| J235c | Above an untrained control | untrained-W net: match ≤ 0.60 (both seeds) |
| J235d | DAG boundary characterized honestly | a multi-parent node: substrate recovers ONLY ONE parent (the other is lost) — documented, not hidden |

PASS = J235a–c (the engine reasons through the substrate from prose); J235d is a CHARACTERIZATION bar (records the
multi-parent limitation honestly — PASS = the limitation is exactly as predicted, NULL = it behaves differently).
NULL (honest): J235a fails → chaining/store breaks at this scale or the ancestor-set collection desyncs; J235c
fails → the readout solves it untrained (confound). No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J235a PASS (≥0.90, ~1.00): within capacity store=1.00 (232) and chain=1.00 (233), so collecting the ancestor set
by iterated retrieval reproduces the symbolic transitive closure on a tree; negatives resolve because a wrong y
simply never appears in the recovered ancestor set. J235b PASS (depth-3+ positive from read()-extracted facts).
J235c control fails (untrained → first hop is noise → ancestor set garbage → match ≤ 0.60). J235d: the multi-parent
node loses a parent — a key→value Hopfield maps one key to ONE attractor (argmax), so `concat(child, parentA)` and
`concat(child, parentB)` are two patterns sharing a KEY; retrieval settles to ONE (or a mix that decodes to one),
so `is_a(child, parentB)` via substrate = FALSE while symbolic = True. This is the honest DAG limitation: the basic
store is a FUNCTION (one value/key); DAGs need value-superposition + multi-cleanup (a known extension, not done
here). RISK (in-rung counter-check): the ancestor-set walk must STOP at roots (a concept with no stored parent
retrieves a spurious nearest code) — cap depth at the taxonomy height and detect fixed points / self-loops.

## RESULT (2026-06-05): PASS — all 4 bars; the engine reasons through the substrate, DAG boundary as predicted

| seed | tree match | control | deep poodle→organism | DAG: symbolic → substrate (loses one?) |
|------|-----------|---------|----------------------|----------------------------------------|
| 42 | 1.00 | 0.50 | True | {dog, pet} → 'pet' (yes) |
| 7  | 0.93 | 0.50 | True | {dog, pet} → 'pet' (yes) |

- **J235a ✓** — substrate-answered is_a matches the engine's symbolic is_a over a 44-query battery (multi-hop
  positives + negatives): **1.00 / 0.93**, both ≥ 0.90. The engine's reasoning runs on the substrate.
- **J235b ✓** — the depth-4 chain `poodle → dog → canine → mammal → animal → organism` (in NO single sentence,
  extracted by `read()`) resolves through iterated energy relaxation, both seeds.
- **J235c ✓** — untrained control **0.50** (chance on the balanced battery): the trained attractors do the reasoning.
- **J235d ✓** — the multi-parent node `poodle` (symbolic parents {dog, pet}) recovers ONLY ONE through the substrate
  ('pet'), losing the other — **exactly the predicted DAG limitation**: a key→value Hopfield is a FUNCTION (one
  attractor per key), so two edges sharing a child-key collapse to one. DAGs need value-superposition + multi-cleanup
  (a known extension, deliberately not done here). Characterized honestly, not hidden.

**HONEST note:** seed-7 tree match is 0.93, not 1.00 — ~3 of 44 queries flip at a root boundary (the SIM_STOP
threshold occasionally accepts/rejects a spurious top-of-tree retrieval). Within the pre-registered ≥0.90 bar;
reported, not rounded up.

**FINDING — the arc's capstone:** the Understanding Engine's actual LEARN(read prose)→REASON(multi-hop is_a)→ANSWER
loop runs ON the energy-based substrate end-to-end: prose → `read()` taxonomy → EnergyNet key→value attractors →
ancestor-set walk by relaxation → is_a answer matching the symbolic closure (within capacity, on trees). The
concrete, end-to-end answer to "where is the substrate in the chain?": it is the relational MEMORY and the INFERENCE
engine, not just an isolated demo. The two boundaries are precise and honest: ~20 facts/module capacity (J232) and
single-parent trees (J235d — DAGs need the superposition extension). Established methods throughout (Hopfield CAM +
iterated associative recall + the engine's symbolic extractor as the front-end), named; no novelty — the value is
the demonstrated end-to-end connection. Verdict: **PASS** (predict-calibrate HIT — all 4 bars incl. the DAG boundary,
as forecast).
