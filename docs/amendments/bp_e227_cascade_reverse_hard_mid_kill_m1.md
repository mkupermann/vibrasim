# BP-E227 — Cascade reverse hard mid-kill M1; reverse p0 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E220 hard mid-kill M0 PASS; E226 soft mid-kill M1 PASS  
**Discipline:** hard kill **M1** silences reverse p1; reverse p0 survives. Completes hard-kill symmetry (not soft M re-probe).

## Hypothesis
1. Pre: fire R1 → L1 reverse ≥0.90  
2. Hard kill M1: fire R1 → L1 reverse **fails** ≥0.70  
3. Hard kill M1: fire R0 → L0 reverse ≥0.80  

## Bars
B1 pre rev p1 ≥0.90 · B2 post hard rev p1 fail ≥0.70 · B3 rev p0 survives ≥0.80  

Seeds {6721,6731} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if hard mid isolation is symmetric to E220.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard kill M1 silences reverse p1; reverse p0 survives. Symmetric to E220.
