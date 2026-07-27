# BP-E180 — Split-port arm-selective **soft** weaken (parity with hard E177)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E177 hard split-port arm kill PASS; E174 soft full-R weaken PASS  
**Discipline:** soft weaken at R0 only; c0 fire-select fails; c1 survives

## Hypothesis
Same split ports as E177. Soft weaken R0 (not hard kill).  
1. Pre: fire L0 → c0 select ≥0.90  
2. Soft R0: fire L0 select fails ≥0.70  
3. Soft R0: fire L1 → c1 select ≥0.80  

## Bars
B1 pre c0 ≥0.90 · B2 post c0 fail ≥0.70 · B3 c1 survives ≥0.80  

Seeds {4781,4791} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if soft weaken is arm-local under spatial split (hard already is).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Soft weaken R0 silences c0 fire-select; c1 survives. Soft+hard split-port arm kill closed (E177/E180).
