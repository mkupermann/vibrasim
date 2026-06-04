# JEP-134 — does REDUNDANCY rescue noisy structure learning? (the constructive follow-up to JEP-133)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 redundancy rescues it: at ~30% per-observation noise, inference accuracy recovers toward 1.0 as redundancy k
  grows (k=1 fails, k~5-10 recovers) via majority-vote denoising (error drops exponentially in k). MOST-LIKELY
  MISS: needing more redundancy than expected.

## Acceptance
- Report accuracy vs redundancy k at fixed per-observation noise. PASS if accuracy recovers to >= 0.9 at feasible
  k. Established (majority-vote denoising), named; no novelty.

## Result — PARTIAL (calibration MISS again); the honest insight: closures COMPOUND errors
| k (redundancy) | accuracy (transitive + non-transitive) |
|----------------|----------------------------------------|
| 1 | 0.50 | 
| 3 | 0.52 |
| 5 | 0.52 |
| 9 | 0.64 |
| 15 | 0.78 |
| 25 | 0.89 |

Redundancy DOES rescue noisy structure learning, but needs k~25 at 30% per-obs noise to reach 0.89 — MORE than
predicted (I said k~5-10). CALIBRATION: MISS (over-optimistic; UNDER-predicted noisy-structure difficulty a 2nd
time, JEP-133+134). THE INSIGHT (why it's hard): structure inference COMPOUNDS errors — a transitive closure needs
MANY constituent facts ALL correct, so a single residual mis-denoised pair corrupts the whole closure. Per-fact
denoising must therefore be NEAR-PERFECT (not just better-than-chance), which demands high redundancy. This is the
fundamental reason noisy structure learning is harder than noisy single-fact prediction: errors compound through
the closure. HONEST SYNTHESIS (JEP-133+134): noisy structure learning is rescuable with SUBSTANTIAL repeated
observation (k~25 at 30% noise), but not cheaply, and one-shot/rare facts can't be denoised this way. So the
genuine open problem is structure learning from NOISY, SPARSE, ONE-SHOT data (as humans do) — which needs more than
redundancy (strong structural priors, active querying, incremental high-confidence bootstrapping). Tally 30/48.
Established (majority-vote denoising), named; no novelty.
