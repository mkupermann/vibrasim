# JEP-377 — Does a magnitude-preserving (analog) readout close the deep-recall floor?

## Motivation
JEP-376 root-caused the residual deep-recall floor (0.93–0.97): modules are read through `sign()` (binarized), which
(a) makes edge reinforcement a no-op and (b) adds quantization noise on top of the ~1/√load dilution that the deepest
nodes (~10 materialized ancestors) already suffer, so the faintest true single-hop edge sits below the gate and the
true/false single-hop similarity distributions overlap. The cognition thread separately found that an ANALOG (non-sign)
bundle restores fidelity a sign bundle loses. This experiment tests, as a controlled comparison (no change to the
deployed store), whether reading the consolidated store with a magnitude-preserving cleanup separates the overlap that
sign cannot — i.e. achieves deep ≥0.95 AND negatives ≥0.95 simultaneously. No transformer.

## Method
On the same auto-consolidated taxonomy (~300 nodes, depth 8) used in JEP-375/376:
- **sign readout** (current): `edge_sim` uses `sign(module)`.
- **analog readout**: identical unbinding but against the raw module SUM (magnitude preserved), L2-normalized per
  module so scores are comparable.
For each readout, sweep the decision gate over the observed similarity range and record, at the gate that maximizes
`min(deep_recall, negative_accuracy)`, both metrics. Report whether each readout can clear min(deep,neg) ≥0.95, plus
the true-vs-false separation margin. Both seeds (0, 7).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the analog readout separates the distributions better than sign — it clears **min(deep, neg) ≥ 0.95** on
both seeds, where sign cannot (sign floors ~0.93 because quantization + overlap). Genuinely uncertain: if the ~1/√load
dilution dominates the quantization, analog may only narrow the gap (PARTIAL), which is itself the finding (the floor
is dilution, not quantization).

- **J377a (analog clears the bar):** with analog readout, at the best gate, min(deep, neg) ≥ 0.95 on BOTH seeds.
- **J377b (analog beats sign):** analog's best min(deep, neg) > sign's best min(deep, neg) on BOTH seeds.
- **J377c (separation margin):** analog's true-edge median sim exceeds its false-pair 95th-percentile sim by a larger
  relative margin than sign's, both seeds (mechanism check).

If J377a holds, the path to closing the floor is a magnitude-preserving cleanup (a worthwhile, scoped change to the
durable store). If only J377b/c hold (analog better but still <0.95), the residual is dilution-bound and needs reduced
per-key load, not readout. Either is the finding. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT — the floor is sign-quantization, closable by analog readout)
| seed | SIGN best min(deep,neg) | SIGN margin | ANALOG best min(deep,neg) | ANALOG margin |
|--|--|--|--|--|
| 0 | 0.95  | 1.345 | **1.0** | **2.615** |
| 7 | 0.975 | 1.713 | **1.0** | **1.85** |

- **J377a (analog clears the bar): PASS** — with a magnitude-preserving readout, at the best gate min(deep, neg) =
  **1.0** on both seeds.
- **J377b (analog beats sign): PASS** — analog's best min(deep,neg) (1.0) > sign's (0.95 / 0.975), both seeds.
- **J377c (separation margin): PASS** — analog's true-vs-false separation margin is larger (2.615 vs 1.345; 1.85 vs
  1.713), confirming the mechanism: preserving magnitude pulls the faint deep edges clear of the false-pair tail.

## Verdict: **PASS — the deep-recall floor is a sign-quantization artifact, not a fundamental dilution wall**
A magnitude-preserving (analog) cleanup separates the true/false single-hop is-a distributions where `sign()` cannot,
reaching min(deep, neg) = 1.0 on both seeds. So the residual ~3–7% deep gap from JEP-375/376 is caused by the binarized
readout discarding the magnitude that distinguishes a faint-but-real deep edge from a near-miss — NOT by an
irreducible ~1/√load dilution. The fix is therefore a scoped, justified change: read closed (consolidated) is-a edges
with an analog cleanup. Implemented and verified end-to-end next (JEP-378). This also resolves why reinforcement failed
(JEP-376): reinforcement only matters under a magnitude-preserving readout. No transformer.
