# BP-E177 — Split-port arm-selective hard kill (c0 path off, c1 path on)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E176 NULL (shared-port c0-band kill not arm-selective); circuit 2×2 spatial separation  
**Discipline:** **finer mechanism** = spatially split ports for c0 vs c1; hard kill R0 only; fire-select by port neighborhood latch

## Hypothesis
c0: L0↔R0 at y=15, freqs 500↔5000.  
c1: L1↔R1 at y=35, freqs 5000↔500.  
Pair-link train both.  

1. Pre: fire near L0 → peak latch at R0 ≥1 and R0 > R1 ≥0.90  
2. Hard kill R0 only: fire L0 select **fails** ≥0.70  
3. After R0 kill: fire L1 → R1 select still ≥0.80  

## Bars
B1 pre c0 select ≥0.90 · B2 post c0 fail ≥0.70 · B3 c1 survives ≥0.80  

Seeds {4701,4711} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if spatial split segregates bridges (E176 failed on shared ports). NULL if cross-talk bridges share graph.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Spatially split ports enable arm-selective hard kill: R0 kill silences c0 fire-select while c1 survives. Fixes E176 shared-port failure via spatial segregation.
