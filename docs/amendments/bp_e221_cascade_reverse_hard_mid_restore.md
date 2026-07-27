# BP-E221 — Cascade reverse hard mid-kill M0 then retrain-restore reverse p0

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E220 hard mid-kill PASS; E219 soft mid-restore PASS  
**Discipline:** multi-trial: hard kill M0 silences reverse p0; reverse p1 survives; retrain path0 restores reverse p0. Completes hard mid-kill restore.

## Hypothesis
1. Hard kill M0: fire R0 → L0 reverse **fails** ≥0.70  
2. Hard kill M0: fire R1 → L1 reverse ≥0.80  
3. Retrain path0 hops: fire R0 → L0 reverse ≥0.80  

## Bars
B1 post hard rev p0 fail ≥0.70 · B2 rev p1 survives ≥0.80 · B3 restore rev p0 ≥0.80  

Seeds {6471,6481} trials 6. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if retrain rebuilds after hard mid-kill like soft E219 restore.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard mid-kill M0 silences reverse p0; reverse p1 survives; retrain path0 restores reverse p0.
