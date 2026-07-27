# BP-E187 — Cascade mid-hop selective kill (M0 off; path1 survives)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 content+cascade fire-select PASS  
**Discipline:** hard kill mid node M0 only; path0 fire-select fails; path1 still selects

## Hypothesis
Same dual cascade as E186.  
1. Pre: fire L0 → path0 select ≥0.90  
2. Hard kill M0: fire L0 select **fails** ≥0.70  
3. Hard kill M0: fire L1 → path1 select ≥0.80  

## Bars
B1 pre p0 ≥0.90 · B2 post p0 fail ≥0.70 · B3 p1 survives ≥0.80  

Seeds {5061,5071} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if mid-hop is critical and spatially isolated (E186 doctrine + E177 arm-kill class).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Mid-hop hard kill at M0 silences path0 cascade fire-select; path1 survives. Multi-hop content cascade is mid-hop critical and path-local.
