# BP-E199 — Split-port + G12 soft-kill wrong arm (fix E198 shared-port spill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E198 NULL shared-port soft spill; E177 split-port hard kill; E194–E197 G12  
**Discipline:** spatial split L0/R0 (c0,pid1) and L1/R1 (c1,pid2); train-time tags; soft kill R1 only

## Hypothesis
1. Pre: active_pattern_id=2; fire L1 → R1 select ≥0.90  
2. Soft kill R1: fire L1 → R1 select **fails** ≥0.70  
3. Soft kill R1: active_pattern_id=1; fire L0 → R0 select ≥0.80  

## Bars
B1 pre pid2 ≥0.90 · B2 post pid2 fail ≥0.70 · B3 pid1 survives ≥0.80  

Seeds {5521,5531} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if spatial split isolates soft kill (E177 + E180 class with G12).

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill R1 silences pid2; pid1 on split L0/R0 survives. Fixes E198 shared-port spill: G12 + spatial split isolates soft surgery.
