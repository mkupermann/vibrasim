# BP-E50 — Soft-cut mid hop of three-hop path

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E32 three-hop PASS; E44 soft weaken PASS

## Hypothesis
Path L–A–B–R. I near A–B mid-link only (radius covers A and B, not L/R). Soft weaken (frac=1).
1. Fire L: R ON ≥0.90  
2. Fire I then L: R OFF ≥0.90  
3. Restore only A–B (not full path): fire L: R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 initial ON | ≥0.90 |
| B2 mid-cut OFF | ≥0.90 |
| B3 mid-only restore ON | ≥0.85 |

Seeds {1521,1531} trials 8.

## Prediction
🔮 PASS lean; miss if I also weakens L–A or B–R.

## RESULT
**NULL** (2026-07-20). B1=**1.0**, B2=**1.0**, B3_mid_restore=**0.0**.  
Mid-cut silences path; A–B-only restore insufficient (I also weakens L–A and/or B–R).
