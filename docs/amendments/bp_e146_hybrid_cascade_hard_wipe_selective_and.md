# BP-E146 — Hybrid cascade: (L1∧L2)→M→A→R + L3→R hard dual wipe → selective cascade AND restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E137 hybrid hard selective AND; E141–E145 cascade  
**Discipline:** **new topology** = cascade multi-hop AND with OR bypass; hard dual wipe then cascade AND-only restore

## Hypothesis
Cascade AND path + L3→R OR. Hard dual-cut I1+I3.  
1. Both paths silent ≥0.80  
2. Restore cascade AND (L1,L2,M,A,R + gate): dual ON ≥0.80  
3. L3 still OFF ≥0.80  

## Bars
B1 both silent ≥0.80 · B2 cascade AND restored ≥0.80 · B3 OR still OFF ≥0.80  

Seeds {3921,3931} trials 6. Budget ~14 min, hard cap 28 min.

## Prediction
🔮 LEAN PASS. Cascade AND + hybrid selective restores compose.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hybrid cascade hard dual wipe + selective cascade AND restore; OR stays OFF.
