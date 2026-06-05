# JEP-243 — robust FULL engine on the substrate: apply the JEP-241 aggregation cure to composed queries

Pre-registered 2026-06-05 (BEFORE the run). JEP-242 ran the full multi-relation engine through the substrate from
prose (battery 1.00/0.93) but the 2-step part-of × is-a INTERACTION was brittle on seed 7 — a single-retrieval flake
broke the bare composition. JEP-241 showed per-hop AGGREGATION (independent retrievals + majority vote) is the robust
cure for substrate retrieval errors. This BET applies that cure to the full-engine queries and tests robustness
across both seeds.

## Method (no transformer)
- Identical to JEP-242 (one typed EnergyNet holding is-a/part-of/causal/comparison/temporal edges from prose), but
  every substrate hop is REPLACED by an aggregated hop: R independent retrievals (different random init), keep those
  whose overlap clears SIM_STOP, MAJORITY-VOTE the winner (the chain stop-gate is PRESERVED — a hop with no gated
  retrieval stops the chain). R = 5. Same battery + interaction + leak guard. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J243a | Battery robust on BOTH seeds | aggregated battery match vs symbolic = 1.00 (both seeds) — closes the 0.93 dip |
| J243b | Interaction holds on BOTH seeds | part-of × is-a UP True + leak guard False, both seeds (closes J242c) |
| J243c | Aggregation ≥ single-retrieval | aggregated battery match ≥ the JEP-242 single-retrieval match for each seed (no regression) |
| J243d | Above an untrained control | untrained net aggregated battery match ≤ 0.60 (both seeds) |

PASS = J243a–d → per-hop aggregation makes the full multi-relation engine run robustly on the substrate, closing the
JEP-242 composed-query gap. NULL (honest): J243a/b fail → aggregation does not fix it (the error is systematic, not a
flake — then the codes/capacity, not retrieval noise, are the issue). No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS. The seed-7 failure was a single-retrieval flake (battery 0.93 = 1/15 wrong) on a 2-step composition with no
redundancy; R=5 gated voting drives the per-hop error far below the point where it breaks a 2-step chain (JEP-241
showed R=7 lifts single-hop 0.67→1.00), so J243a (1.00 both) and J243b (interaction both) hold, with no regression
(J243c) and control failing (J243d). RISK (in-rung): the gated vote must keep SIM_STOP per-retrieval so a chain still
stops at its root (the bug that invalidated the JEP-242 quick check — fixed here by gating each retrieval before
voting); verify a negative/off-chain target still returns False. Established (ensemble voting + content-addressable
retrieval), named; no novelty — the value is the robust integrated engine-on-substrate, the 241 cure at integration
scale.

## RESULT (2026-06-05): NULL — aggregation does NOT fix it; the real cause is a DIAGNOSED-LESSON RECURRENCE (SIM_STOP root-stop)

| seed | aggregated battery | JEP-242 single-shot | interaction+leak | control |
|------|--------------------|--------------------|------------------|---------|
| 42 | 1.00 | 1.00 | True | 0.33 |
| 7  | 0.87 | 0.93 | False | 0.33 |

- **J243a/b/c ✗** — aggregation did NOT fix seed 7; it mildly HURT (0.87 < 0.93). **J243d ✓** (control 0.33).

**Why aggregation failed → the real diagnosis (dug in instead of accepting my hypothesis).** A determinism probe
showed every STORED-edge hop is DETERMINISTIC and CORRECT across 8 random inits (heart→dog, dog→mammal, …). So the
failure is not a random flake (which voting would cure, JEP-241) — it is SYSTEMATIC. A root-stop probe pinned it: at
ROOTS (animal/weakness/peace — no stored is-a parent), `hop(root, isa)` returns a SPURIOUS node, and the chain-stop
gate `SIM_STOP` (value-overlap) FAILS to stop it (seed 7: `hop(animal,isa)→cat` at sim 36 ≥ 24), so the is-a chain
runs PAST the root into `cat` → `heart part-of cat` becomes True → the leak guard breaks. The ENERGY gate (JEP-237)
stops correctly at every root (energy −35…−60 > the −64 threshold, both seeds).

**This is a DIAGNOSED-LESSON RECURRENCE (the forbidden outcome — recorded honestly).** JEP-236→237 established that
value-overlap CANNOT detect an untrained key (the value always settles to an attractor) and that the KEY→VALUE
ENERGY is the correct detector. I applied that fix to DAG slot-detection (237) but then RE-USED `SIM_STOP`
(value-overlap) for the chain ROOT-stop in JEP-235/242/243 — the identical bug, one layer over. It stayed hidden
until JEP-242's leak-guard query (checking a sibling) exposed a chain running past its root. Aggregation (JEP-243)
was the wrong cure because the error is systematic, not random — consistent with the independent-vs-systematic
distinction (JEP-158/240): voting averages INDEPENDENT noise, not SYSTEMATIC bias.

**CALIBRATION:** I predicted aggregation fixes it (mis-diagnosing the seed-7 error as a random flake in JEP-242).
Wrong — but digging into the NULL (rather than trusting the hypothesis) surfaced the real, diagnosed-lesson-recurrence
cause. The fix is the ENERGY-gated chain stop (JEP-237 applied to chaining), pursued in JEP-244 — NOT aggregation.
Verdict: **NULL** (a/b/c fail; the value is the corrected diagnosis). Lesson re-filed: when a fix (energy gate) is
found for "detect a stored vs untrained key," apply it to EVERY place that detection happens (slot-detection AND
chain-root-stop), not just the one that surfaced it — the JEP-94/99 "fix it in EVERY parser" lesson, recurring.
