# BP-E216 — Cascade reverse multi-trial switch under G12 (1→2→1)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E215 cascade reverse G12 PASS; E206 reverse multi-trial  
**Discipline:** cascade reverse multi-trial switch pid1→pid2→pid1 without retrain. Not E215 single-probe re-run.

## Hypothesis
Train path0 pid1, path1 pid2. Gate ON. No retrain.
1. pid1; fire R0 → L0 reverse ≥0.80  
2. pid2; fire R1 → L1 reverse ≥0.80  
3. pid1 again; fire R0 → L0 reverse ≥0.80  

## Bars
B1 rev p0 ≥0.80 · B2 rev p1 ≥0.80 · B3 rev p0 again ≥0.80  

Seeds {6201,6211} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if cascade reverse multi-trial durable like E206 single-hop reverse.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Cascade reverse multi-trial switch pid1→pid2→pid1 durable under G12.
