# JEP-40 — compute-scaling curve: quantify the "under-convergence is compute" claim

## Motivation
Across JEP-29/31/39b I repeatedly said real-scale under-convergence is "compute, not fundamental" but never
quantified it. This rung measures held-out IS-A vs training iterations at fixed real scale (WordNet carnivore
366), to show whether accuracy monotonically climbs toward a ceiling with more compute.

## Pre-registration (locked BEFORE run)
- WordNet carnivore (366). Calibrated reasoner (default), hyp_dim=20, hold out 30% ancestor pairs. Sweep iters
  in {2k,4k,8k,16k,32k}; measure held-out IS-A (calibrated).
- This is a CHARACTERIZATION (no pass/fail): report the curve. Expectation: monotone increase toward a ceiling,
  confirming the limit is compute. Established methods (Poincare embeddings), named as such.

## Result — the curve PLATEAUS at ~0.78 (correcting my "just compute" over-claim)
| iters | held-out IS-A (calibrated) |
|-------|----------------------------|
| 2000 | 0.651 |
| 4000 | 0.734 |
| 8000 | 0.750 |
| 16000 | 0.778 |
| 32000 | 0.773 |

**VERDICT: important SELF-CORRECTION.** More compute helps (0.65 -> 0.78) but PLATEAUS at ~0.78 - it does NOT
climb to 0.9, and 32k iters is no better than 16k. So my framing across JEP-29/31/39b - "real-scale under-
convergence is JUST compute, not fundamental" - was an OVER-CLAIM. The truth: it is compute UP TO a ~0.78
ceiling, beyond which more iterations do nothing. The residual gap to the toy's 0.91 is NOT iterations - it is
something else (embedding DIMENSION, the calibrated readout, or the inherent difficulty of a 366-concept depth-12
hierarchy in a fixed-dim Poincare ball). I should have quantified this before claiming "just compute" repeatedly.
Honest corrected statement: real-scale accuracy improves with compute but has a method/representation ceiling
well below toy-level that iterations alone do not break. Whether more DIMENSION breaks it is untested here.
Bars: none (characterization). Established methods (Poincare embeddings), named as such.
