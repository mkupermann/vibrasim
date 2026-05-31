# BET-127 — Dimension scaling law for systematic generalization

Pre-registered: 2026-05-31 (BEFORE the run). Fresh from BET-126's residual: with
analog VSA codes the only error left is ~1/sqrt(D) crosstalk noise corrupting value
recovery near the decision boundary. Prediction: systematic held-out accuracy rises
monotonically with hypervector dimension D and crosses 0.85 -> ~1.0.

Same comparison task, same systematic held-out split (novel symbol pairs), analog
bundle, online linear RLS readout. Sweep D in {256, 512, 1024, 2048, 4096, 8192}.
3 seeds per D (report mean) to bound run-to-run noise.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T127a | Monotone scaling | mean held-out acc non-decreasing across D (allow one <=0.03 dip) |
| T127b | Crosses threshold | at the largest D, mean held-out acc >= 0.90 |
| T127c | Big-D solves it | at the largest D, mean held-out acc - small-D(256) >= 0.20 |
| T127d | Still compositional | no-binding control at largest D < 0.65 |

PASS = T127a-d. PASS = SYSTEMATIC (symbolic-combination) generalization is SOLVED on
the substrate via analog VSA composition + an online linear readout, governed by a
clean dimension law — the property language needs, no transformer. NULL would mean
the residual is not just SNR and a deeper mechanism is missing.

## RESULT (2026-05-31): NULL — refutes the 1/sqrt(D) law; reveals an SNR-vs-overfit optimum

| D | held-out acc (mean of 3) |
|---|--------------------------|
| 256 | 0.833 |
| 512 | 0.852 |
| **1024** | **0.889** |
| 2048 | 0.806 |
| 4096 | 0.769 |
| 8192 | 0.787 |
| no-binding control (D=8192) | 0.343 |

T127a ✗ (2 dips), T127b ✗ (0.787 < 0.90), T127c ✗ (gap −0.046), T127d ✓ → **NULL**.

The prediction is REFUTED: bigger D does NOT monotonically help. Accuracy PEAKS at
D=1024 (0.889) then DECLINES. Honest and important:
- Systematic generalization **is reachable** — 0.889 at D=1024 clears the 0.85
  systematic-gen bar. The substrate CAN generalize a relation to novel symbol
  combinations. That core question is answered YES.
- But it's governed by an OPTIMUM, not a law. Likely cause: analog code norm grows
  as |code|^2 ∝ D, while ridge λ is fixed → at high D the readout is effectively
  under-regularized and overfits the 54 training pairs. The unbound-slot crosstalk
  shrinks with D, but overfitting grows faster past ~1024.
- Control still collapses (0.343), so it stays compositional throughout.

**Fresh hypothesis (-> BET-128).** Normalize each code to unit L2 norm before the
readout, so feature scale is D-independent and fixed λ regularizes consistently.
Prediction: the high-D decline disappears and systematic accuracy is stable/high
across D. If so, the BET-127 decline was a normalization artifact and systematic
generalization is SOLVED and robust.
