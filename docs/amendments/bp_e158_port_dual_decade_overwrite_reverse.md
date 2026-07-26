# BP-E158 — Port dual decade content overwrite reverse

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E154 PASS dual decade; E6 content overwrite  
**Discipline:** sequential dual-side ILW overwrite — last write wins reversed decades; not free talent

## Hypothesis
Wall ON. Write L-low R-high; idle; write L-high R-low; idle.  
1. After first write: ordered L < R ≥0.90  
2. After reverse overwrite: reversed mean_decade L > R ≥0.80  
3. Both sides still populated after reverse ≥0.90  

## Bars
B1 first ordered ≥0.90 · B2 reverse ordered (L > R) ≥0.80 · B3 pop after reverse ≥0.90  

Seeds {4201,4211} trials 8. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS. E6 last-content wins extends to dual decade reverse.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. First dual decade ordered OK; reverse overwrite does **not** flip mean decades (multislot may retain prior bands). Content overwrite of dual decade not last-write-dominant under multislot.
