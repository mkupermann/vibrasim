# BP-E219 — Cascade reverse soft mid-kill M0 then retrain-restore reverse p0

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E217 PASS soft mid-kill; E210 reverse soft restore  
**Discipline:** multi-trial: soft kill M0 silences reverse p0; reverse p1 survives; retrain L0–M0–R0 restores reverse p0. New vs closed E214–E218 curriculum bars.

## Hypothesis
1. Soft kill M0: fire R0 → L0 reverse **fails** ≥0.70  
2. Soft kill M0: fire R1 → L1 reverse ≥0.80  
3. Retrain path0 hops: fire R0 → L0 reverse ≥0.80  

## Bars
B1 post soft rev p0 fail ≥0.70 · B2 rev p1 survives ≥0.80 · B3 restore rev p0 ≥0.80  

Seeds {6321,6331} trials 6. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if retrain rebuilds reverse multi-hop after soft mid-kill like E210 single-hop reverse restore.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft mid-kill M0 silences reverse p0; reverse p1 survives; retrain path0 restores reverse p0.
