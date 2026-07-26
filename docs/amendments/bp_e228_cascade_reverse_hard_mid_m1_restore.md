# BP-E228 — Cascade reverse hard mid-kill M1 then retrain-restore reverse p1

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E227 hard mid-kill M1 PASS; E221 hard mid M0 restore PASS  
**Discipline:** multi-trial hard kill M1 silences reverse p1; reverse p0 survives; retrain path1 restores reverse p1. Completes hard M1 restore (not soft mid re-probe).

## Hypothesis
1. Hard kill M1: fire R1 → L1 reverse **fails** ≥0.70  
2. Hard kill M1: fire R0 → L0 reverse ≥0.80  
3. Retrain path1 hops: fire R1 → L1 reverse ≥0.80  

## Bars
B1 post hard rev p1 fail ≥0.70 · B2 rev p0 survives ≥0.80 · B3 restore rev p1 ≥0.80  

Seeds {6761,6771} trials 6. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if retrain path1 rebuilds after hard mid-kill like E221 path0.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard kill M1 silences reverse p1; reverse p0 survives; retrain path1 restores reverse p1.
