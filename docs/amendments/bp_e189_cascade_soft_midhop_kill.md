# BP-E189 — Cascade soft mid-hop kill (parity with hard E187)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E187 hard mid-hop kill PASS  
**Discipline:** soft weaken at M0 only; path0 fails; path1 survives

## Hypothesis
Same dual cascade as E186/E187. Soft weaken M0.  
1. Pre: fire L0 → path0 select ≥0.90  
2. Soft M0: fire L0 select fails ≥0.70  
3. Soft M0: fire L1 → path1 select ≥0.80  

## Bars
B1 pre ≥0.90 · B2 post fail ≥0.70 · B3 p1 survives ≥0.80  

Seeds {5101,5111} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if soft mid-hop disruption matches hard (E174/E180 class).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Soft mid-hop weaken at M0 silences path0; path1 survives. Soft+hard mid-hop kill closed (E187/E189).
