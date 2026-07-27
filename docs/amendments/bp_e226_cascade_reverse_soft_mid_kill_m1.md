# BP-E226 — Cascade reverse soft mid-kill M1; reverse p0 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E217 soft mid-kill M0 PASS (p1 survives)  
**Discipline:** symmetric arm: soft kill **M1** silences reverse p1; reverse p0 survives. Not M0 re-probe.

## Hypothesis
1. Pre: fire R1 → L1 reverse ≥0.90  
2. Soft kill M1: fire R1 → L1 reverse **fails** ≥0.70  
3. Soft kill M1: fire R0 → L0 reverse ≥0.80  

## Bars
B1 pre rev p1 ≥0.90 · B2 post soft rev p1 fail ≥0.70 · B3 rev p0 survives ≥0.80  

Seeds {6681,6691} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if spatial mid isolation is symmetric to E217.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill M1 silences reverse p1; reverse p0 survives. Symmetric to E217.
