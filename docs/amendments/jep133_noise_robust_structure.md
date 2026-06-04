# JEP-133 — noise-robust structure learning (the noisy-data limit from JEP-131)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a noise-tolerant inference (transitive iff closure contradicts <= tau fraction of observed-false pairs)
  correctly classifies transitive vs non-transitive up to MODERATE noise (~20-30%), then degrades as noise makes
  the classes indistinguishable. Strict (JEP-128) fails immediately under noise. MOST-LIKELY MISS: high-noise
  indistinguishability / threshold choice.

## Acceptance (characterization)
- Report classification accuracy across noise levels for strict vs noise-tolerant. The robustness gain + the
  high-noise breakdown are the finding. Established (robust/statistical consistency), named; no novelty.

## Result — calibration MISS (over-optimistic); CORRECTED finding: noisy structure learning is HARD
| noise | strict (tau=0) | tolerant (tau=0.15) |
|-------|----------------|----------------------|
| 0.00 | 0.98 | 0.98 |
| 0.10 | 0.52 | 0.65 |
| 0.20 | 0.51 | 0.53 |
| 0.35 | 0.50 | 0.50 |

CORRECTION: the script's pre-written "finding" claimed the tolerant version is robust to moderate noise — the DATA
CONTRADICTS it. BOTH strict and noise-tolerant collapse toward chance by 10-20% label noise (tolerant only
marginally better at 10%). WHY: noise corrupts the observed-TRUE set too, so the transitive CLOSURE is computed from
noisy pairs and is itself WRONG -> contradictions become spurious -> a tolerance on contradictions can't fix a
corrupted closure. So the noisy-data limit (JEP-131) is REAL and HARD: a simple tolerance does NOT rescue structure
learning under noise. CALIBRATION: MISS (predicted robust to 20-30%; collapses by ~15%). META-INSIGHT: I am
miscalibrated on structure-learning in BOTH directions — I OVER-predicted difficulty on CLEAN data (JEP-129/131,
exact-match is strong) and UNDER-predicted it on NOISY data (here, noise corrupts the closure). The honest balanced
picture: clean-data structure learning is EASY (up to search cost); NOISY-data structure learning is GENUINELY HARD
and needs more than a tolerance (robust statistics, much more data, structural priors, or incremental high-
confidence bootstrapping). Tally 30/47. This is the honest noisy-structure frontier. Established (robust consistency
checking), named; no novelty.
