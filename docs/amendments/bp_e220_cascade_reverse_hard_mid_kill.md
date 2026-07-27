# BP-E220 — Cascade reverse hard mid-kill M0; reverse p1 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E217 soft mid-kill PASS; E187 forward hard mid-kill  
**Discipline:** dual cascade train; reverse works; **hard kill M0** silences reverse p0; reverse p1 survives. Complements soft E217.

## Hypothesis
1. Pre: fire R0 → L0 reverse ≥0.90  
2. Hard kill M0: fire R0 → L0 reverse **fails** ≥0.70  
3. Hard kill M0: fire R1 → L1 reverse ≥0.80  

## Bars
B1 pre rev p0 ≥0.90 · B2 post hard rev p0 fail ≥0.70 · B3 rev p1 survives ≥0.80  

Seeds {6431,6441} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if hard mid-hop kill isolates reverse path0 like soft E217.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Hard kill M0 silences reverse p0; reverse p1 survives.
