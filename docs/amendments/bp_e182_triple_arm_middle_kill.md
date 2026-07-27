# BP-E182 — Triple-arm selective middle kill (c1 off; c0 and c2 survive)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E181 triple-arm capacity PASS; E177 dual-arm selective kill  
**Discipline:** hard kill R1 only; not re-running E181 capacity bars alone

## Hypothesis
Same three split-port arms as E181. After train:  
1. Hard kill R1: fire L0 → c0 select ≥0.80  
2. Hard kill R1: fire L1 → c1 select **fails** ≥0.70  
3. Hard kill R1: fire L2 → c2 select ≥0.80  

## Bars
B1 c0 survives ≥0.80 · B2 c1 fails ≥0.70 · B3 c2 survives ≥0.80  

Seeds {4861,4871} trials 8. Budget ~24 min, hard cap 48 min.

## Prediction
🔮 LEAN PASS if spatial segregation isolates middle arm kill (E177 doctrine at K=3).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Triple-arm middle kill: c1 silenced; c0 and c2 fire-select survive. Selective arm surgery scales to K=3.
