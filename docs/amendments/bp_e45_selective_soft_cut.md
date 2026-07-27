# BP-E45 — Selective soft cut (one of two paths)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E44 soft restore PASS; E31 parallel isolation

## Hypothesis
Two chains L1–M1–R1 and L2–M2–R2 (y-separated). I near M1 only (`fire_weaken` radius covers M1 not M2).
1. Fire L1 and L2 before cut: both R ≥1.0 ≥0.85  
2. Fire I (weaken path1), then fire L1: R1 ≤0.25 ≥0.85; fire L2: R2 ≥1.0 ≥0.85  
3. Full restore path1 only: fire L1 → R1 ≥1.0 ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 both ON pre-cut | ≥0.85 |
| B2 after I: R1 OFF and R2 ON | ≥0.85 |
| B3 restore path1: R1 ON | ≥0.85 |

Seeds {1391,1401} trials 10.

## Prediction
🔮 PASS if radius selective.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Selective soft cut: path1 off, path2 on; restore path1.
