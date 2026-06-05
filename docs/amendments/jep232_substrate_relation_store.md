# JEP-232 — does the SUBSTRATE carry the Understanding Engine's relational knowledge?

Pre-registered 2026-06-05 (BEFORE the run). Answers Michael's recurring question — "where is the substrate
in the chain?" — for the *relational* knowledge specifically. The Understanding Engine (EQMOD-4) stores its
is-a / part-of facts in Python dicts + VSA fact-vectors; the SUBSTRATE (`world.energy.EnergyNet`, a modular
Hopfield/contrastive-Hebbian EBM, reconnected at JEP-81 for pattern completion + sequence) has never held the
*relations*. This BET tests whether the energy-based substrate can serve as the relational store: store is-a
facts as key→value attractors and retrieve the parent from a child cue THROUGH energy relaxation, not a dict.

## Method (no transformer; established associative key-value / Hopfield memory, named as such)
- EnergyNet, single dense module, N=80. KEY slot = units [0:40], VALUE slot = [40:80].
- Each concept → a fixed random ±1 code of length 40. A fact (child →is-a→ parent) → the bipolar pattern
  `concat(code[child], code[parent])`. Store K facts as attractors via `train_epoch` (contrastive-Hebbian, local).
- RETRIEVE(child): clamp KEY=code[child], relax VALUE free → read the settled VALUE slot → nearest concept code
  by dot product. Correct iff = the true parent. (Content-addressable relation retrieval via the substrate.)
- Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J232a | Substrate CARRIES relations | K=4 facts: child→parent recall ≥ 0.85 (mean over facts, both seeds) |
| J232b | Above an untrained control | untrained-W net at K=4: recall ≤ 0.40 (both seeds) |
| J232c | Content-addressable from a PARTIAL cue | clamp 60% of the KEY code: recall ≥ 0.70 at K=4 (both seeds) |
| J232d | Capacity is BOUNDED (the substrate signature) | recall(K=12) < recall(K=4) — degradation visible (both seeds) |

PASS = J232a–d → the substrate can hold the Understanding Engine's is-a relations as content-addressable
attractors with a bounded, measurable capacity: the relational knowledge lives IN the energy-based substrate,
not only in Python. NULL outcomes (all honest): J232a fails → the substrate cannot bind key→value at this scale
(e.g. contrastive-Hebbian under-trains, or the relax collapses to a mixed attractor); J232b fails → the readout
is trivially solvable without the substrate (metric confound); J232d fails → no capacity bound visible at K≤12.
No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J232a PASS (K=4 ⊂ Hopfield capacity ~0.14·80≈11 → recall ≥ 0.85); J232b control FAILS (untrained → value slot
is noise → argmax over K distinct codes ≈ 1/K ≈ 0.25 ≤ 0.40); J232c PASS (Hopfield completes from a partial key,
≥ 0.70); J232d degradation VISIBLE (K=12 approaches capacity → mixed-attractor cross-talk lowers recall below K=4).
Net: the substrate carries relations as an established associative key-value memory (named as such; NO novelty) —
bounded capacity, consistent with the substrate's broader capacity-limited memory story. RISKS (counter-cases run
in-rung per calibration error-class 11): (i) the parent-readout argmax must EXCLUDE the child's own code or it self-
matches; (ii) contrastive-Hebbian may under-train at low epochs → check recall vs epochs; (iii) at K=12 retrieval
could collapse entirely (recall→chance) rather than degrade gracefully — either way J232d's `<` holds.

## RESULT (2026-06-05): PARTIAL — substrate CARRIES relations (a/b/c PASS); capacity bound CONFIRMED but my K was wrong (d FAIL)

| seed | K=4 recall | K=4 partial(60%) | K=4 control | K=12 recall |
|------|-----------|------------------|-------------|-------------|
| 42 | 1.00 | 1.00 | 0.25 | 1.00 |
| 7  | 1.00 | 1.00 | 0.25 | 1.00 |

- **J232a ✓** — the energy-based substrate carries is-a relations: clamp the child code, relax, read the parent → **1.00** recall, both seeds.
- **J232b ✓** — untrained-W control **0.25** (≈1/K chance) ≤ 0.40. The substrate's learned attractors, not the readout, do the work.
- **J232c ✓** — content-addressable from a **60% partial** child cue → **1.00**. Genuine CAM.
- **J232d ✗** — K=12 recall **1.00**, NOT < K=4. The bar FAILED **as written**.

**Capacity sweep (the calibration — my K=12 guess was below the cliff):**

| K | 4 | 12 | 16 | 18 | 20 | 22 | 24 | 40 | 80 |
|---|---|----|----|----|----|----|----|----|----|
| mean recall | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.34 | 0.04 | 0.03 | 0.01 |

The capacity bound IS real and **SHARP** — perfect recall to **K≈20**, then a **catastrophic blackout at K≈22** (classic
Hopfield overload: above capacity ALL patterns become unrecoverable at once, not graceful decay). So J232d's *intent*
— bounded capacity — is **CONFIRMED**; the bar failed only because my pre-registered K=12 landed **below** the cliff.

**CALIBRATION [predict-calibrate]:** I mis-estimated capacity by applying the **0.14·N autoassociative** Hopfield bound
(≈11) when this is **heteroassociative** retrieval — the 40-unit KEY is fully clamped and only the VALUE slot settles,
which is far easier, giving ~**0.5 facts/value-unit** (≈20). Lesson (extends error-class 10 "don't carry intuition
across representations"): the relevant capacity bound depends on **how much is cued**; a fully-clamped key buys ~3-4×
the autoassociative capacity. The bar wasn't wrong in spirit, my *number* was — recorded honestly, not retuned.

**FINDING (the answer to "where is the substrate in the chain?" for relational knowledge):** the Understanding
Engine's is-a relations CAN live in the energy-based substrate as content-addressable key→value attractors — perfect,
partial-cue-robust retrieval up to ~20 facts/module, then a sharp capacity cliff. This is an established associative
key-value (Hopfield) memory, named as such — **no novelty**; the value is the demonstrated CONNECTION (substrate as
relational store) plus the measured capacity/blackout signature, which mirrors the substrate's broader capacity-limited
memory story but here on the POSITIVE side (within capacity it works perfectly). Scaling the store = more modules/units
(linear), not a new mechanism. Verdict: **PARTIAL** (3/4 pre-registered bars; core capability positive, capacity-bound
sub-claim's threshold miscalibrated and corrected by measurement).
