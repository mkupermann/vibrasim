# BP-E151 — Dual cascade AND hard wipe both paths → full restore both

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E150 dual cascade; E142 cascade hard wipe-restore  
**Discipline:** hard dual-cut all four L ports on both cascades; full restore both paths

## Hypothesis
Same dual cascade topology as E150.  
1. Both dual ON ≥0.80  
2. Hard-cut I0a,I0b,I1a,I1b: both dual OFF ≥0.80  
3. Full restore both paths: both dual ON ≥0.80  

## Bars
B1 both dual ON ≥0.80 · B2 both dual OFF ≥0.80 · B3 restore both dual ON ≥0.80  

Seeds {4021,4031} trials 6. Budget ~16 min, hard cap 32 min.

## Prediction
🔮 LEAN PASS. Dual cascade hard wipe-restore of both paths.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual cascade hard wipe both paths + full restore both closed. Dual cascade curriculum closed with E150 selective.
