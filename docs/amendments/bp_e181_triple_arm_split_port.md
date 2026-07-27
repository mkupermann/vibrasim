# BP-E181 — Triple-arm split-port fire-select capacity

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E177 dual-arm split-port PASS  
**Discipline:** three spatially segregated associations; fire each L → correct R; not farming dual-arm kill bars

## Hypothesis
Arms at y=10, 25, 40:  
c0: L0↔R0 freqs 300↔3000  
c1: L1↔R1 freqs 1000↔10000  
c2: L2↔R2 freqs 500↔5000  

Pair-link train all three multi-trial.  
1. Fire L0 → peak R0 > R1 and R0 > R2 and R0≥1 ≥0.80  
2. Fire L1 → R1 wins ≥0.80  
3. Fire L2 → R2 wins ≥0.80  

## Bars
B1 c0 select ≥0.80 · B2 c1 select ≥0.80 · B3 c2 select ≥0.80  

Seeds {4821,4831} trials 8. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if dual-arm spatial doctrine scales to K=3. NULL if cross-talk collapses third arm.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Triple-arm split-port fire-select capacity closed; dual-arm spatial doctrine scales to K=3.
