# JEP-139 — confidence-graded reasoning: path-count confidence improves precision under noise (operationalizes JEP-138)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 path-count confidence is HIGHER for true conclusions than spurious ones under noisy knowledge, so a confidence
  threshold (>=2 paths) improves PRECISION over boolean is_a (at some recall cost). MOST-LIKELY MISS: spurious
  paths also accumulating, blurring the separation.

## Acceptance
- PASS: confidence-thresholded is_a has higher precision than boolean is_a under noise. Established (evidence
  aggregation / graded belief), named; no novelty.

## Result — NULL (calibration MISS); honest correction: redundancy is a RECALL tool, not precision-via-path-count
| noise | boolean prec/rec | conf>=2 prec/rec |
|-------|------------------|-------------------|
| 0.1 | 0.95 / 0.89 | 0.95 / 0.36 |
| 0.2 | 0.89 / 0.88 | 0.91 / 0.37 |

The conf>=2 path-count threshold gives NEGLIGIBLE precision gain (0.00 at noise 0.1; +0.02 at 0.2) while CRATERING
recall (0.89 -> 0.36). The script's printed verdict ("raises precision") OVER-CLAIMS — corrected. WHY it failed:
(1) boolean precision is ALREADY high (few false positives -> nothing to gain); (2) many TRUE conclusions have only
ONE path in this DAG, so requiring >=2 over-filters them. CORRECTION of my own reasoning: JEP-138's redundancy
benefit is for RECALL (a true conclusion survives if ANY of its paths survives the noise), NOT a precision tool via
path-counting. I MIS-APPLIED the insight (recall vs precision). CALIBRATION: MISS (predicted precision improvement;
got none + catastrophic recall loss); tally 34/53. The is_a_confidence method is kept as a valid GRADED signal
(path count = degrees of derivational support) but is NOT a precision filter in this regime. Honest NULL. Established
(evidence aggregation), named; no novelty. LESSON: when operationalizing an insight, be precise about WHICH metric
it improves (138 = recall robustness) — don't assume it transfers to a different metric (precision).
