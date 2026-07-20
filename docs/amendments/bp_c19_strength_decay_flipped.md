# BP-C19 — Strength-decay flipped dual-band reverse specialisation

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 provisional; C18 same-band PASS  
**Discipline:** decay ON; **L=high band, R=low band** — expect mean_decade_L > mean_decade_R

## Hypothesis
With `ilw_strength_decay_tau=30` and flipped inject (left HIGH, right LOW), natural reverse success (mean_L > mean_R ∧ both n≥1) ≥0.80. Control without decay ≤0.70 on reverse.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Decay ON reverse success | ≥0.80 |
| B2 | Decay OFF reverse success | ≤0.70 |
| B3 | Decay ON both populated | ≥0.80 |
| B4 | Decay − control reverse delta | ≥0.10 |

Seeds {2361,2371,2381} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN PASS if decay amplifies true band structure either orientation. NULL if effect is one-sided artifact.

## RESULT
**NULL** (2026-07-20). B1=0.556 B2=0.667 B3=1.0 B4=−0.11.  
Flipped (L-high R-low) reverse specialisation fails under decay; control slightly better. Decay does not symmetrically amplify either orientation.
