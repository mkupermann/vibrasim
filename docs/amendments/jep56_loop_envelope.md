# JEP-56 — grounded-loop operating envelope: how noise propagates through form->reason->act

## Motivation
JEP-55 demonstrated the complete loop at LOW noise (1.00). Honest completion: its OPERATING ENVELOPE. Sweep
feature noise; measure both concept-FORMATION purity and end-to-end PLANNING success. Does planning track
formation purity (errors propagate, per JEP-37/46) or does the loop tolerate some formation errors?

## Pre-registration (locked BEFORE run)
- Same loop as JEP-55, sweep feature-noise sigma {0.3, 0.8, 1.5, 2.5}. Per sigma: discovered-category true-purity
  and grounded-planning success (reached an entity truly in the goal category's TRUE branch).
- CHARACTERIZATION: report (purity, planning) vs sigma. Expectation: both degrade with noise; whether planning
  tracks or lags purity shows error propagation. Established (clustering, SR/TD, Poincare), named as such.

## Result — graceful degradation; the loop is FORGIVING of formation errors
| sigma | formation purity | loop planning success |
|-------|------------------|-----------------------|
| 0.3 | 1.000 | 1.000 |
| 0.8 | 0.890 | 0.913 |
| 1.5 | 0.722 | 0.783 |
| 2.5 | 0.692 | 0.757 |

**VERDICT: graceful degradation + forgiving loop.** Two honest findings: (1) the complete form->reason->act loop
NEVER COLLAPSES - it degrades gracefully from 1.0 to ~0.76 as feature noise rises; (2) planning success is
SLIGHTLY HIGHER than formation purity at every noise level (e.g. 0.78 vs 0.72 at sigma 1.5). So the loop is
FORGIVING: concept-formation errors do NOT fully propagate to action, because navigating to the NEAREST grounded
entity still usually reaches a majority-(correct-)branch member even when a discovered category is impure. This
CONTRASTS with JEP-37/46 (where component errors propagated/amplified through grounding) - here the planning step
ABSORBS some formation noise. Honest operating envelope of the grounded loop: reliable (>=0.9) to moderate noise
(sigma<=0.8), graceful to ~0.76 at high noise. Established methods (clustering, SR/TD, Poincare), named.
