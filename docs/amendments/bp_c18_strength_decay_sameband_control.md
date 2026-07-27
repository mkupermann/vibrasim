# BP-C18 — Strength-decay same-band negative control

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 PASS  
**Discipline:** decay ON, but **both sides same band** [100,10000] — specialisation must NOT pass

## Hypothesis
With `ilw_strength_decay_tau=30` but identical frequency bands L and R, mean_decade_L < mean_decade_R success rate stays low (≤0.60). Decay alone must not fabricate decade structure without band difference.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Same-band + decay: natural success rate | ≤0.60 |
| B2 | Both sides populated | ≥0.80 |
| B3 | Matched dual-band + decay (positive check, same seeds) success | ≥0.80 |

Seeds {2331,2341,2351} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN PASS (B1 low, B2 high, B3 high). NULL if decay invents false specialisation on same-band.

## RESULT
**PASS** (2026-07-20). B1_sameband=0.111 B2_pop=1.0 B3_dualband=1.0.  
Decay does **not** invent decade structure without band difference; dual-band + decay still specialises on these seeds.
