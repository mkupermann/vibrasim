# BP-E73 — Hard-kill OR bypass then restore L3–R

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E70 hard-cut PASS; E43 retrain after hard cut; E71 soft restore NULL  
**Discipline:** hard kill L3 then full L3–R retrain (structural recovery of OR bypass)

## Hypothesis
AND L1/L2–M–R + OR L3–R. Hard I at L3, r=8.
1. Hard-cut → L3 OFF ≥0.90  
2. Restore L3–R (kill emitters cleared after cut by restore writes) → L3 ON ≥0.85  
3. AND still ON ≥0.90  

## Bars
B1 OFF ≥0.90 · B2 restore ON ≥0.85 · B3 AND ON ≥0.90  

Seeds {2151,2161} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS (E43-class). Miss if hard kill destroys R ports needed for L3 rewrite.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard-kill OR bypass + disarm kill emitters + L3–R restore recovers bypass; AND intact.
