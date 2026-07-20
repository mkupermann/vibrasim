# BP-E28 — Curriculum overwrite with PRIM8 replace

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM8-D0  
**Not** E27 bar retune — **new mechanism** = pair_replace

## Hypothesis
Same maps as E27. With `ilw_pair_replace_enabled=True`: after A→B, match B ≥0.85, residual A ≤0.25; A-only match A ≥0.85; bridged ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | A→B match B | ≥0.85 |
| B2 | A→B residual A | ≤0.25 |
| B3 | A-only match A | ≥0.85 |
| B4 | bridged L present | ≥0.90 |

Seeds {911,921} trials 10.

## Prediction
🔮 PASS if PRIM8-D0 works.

## RESULT
**PASS** (2026-07-20). B1_match_B=**1.000**, B2_residual_A=**0.000**, B3_A_only=**1.000**, B4=**1.000**.  
Curriculum overwrite works with PRIM8 replace (E27 boundary closed by new mechanism).
