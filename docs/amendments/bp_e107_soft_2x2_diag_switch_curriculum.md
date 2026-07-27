# BP-E107 — Soft 2×2 multi-trial diagonal switch after full restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E105/E106 diagonal cuts; E82/E83 wipe reconfig  
**Discipline:** full restore; cut identity→swap; restore identity diag + cut swap→identity again

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all (full).
1. Soft-cut 00+11 → pure swap ≥0.80  
2. Soft-cut 01+10; restore 00+11 → pure identity ≥0.80  
3. Soft-cut 00+11; restore 01+10 → pure swap again ≥0.75  

## Bars
B1 swap ≥0.80 · B2 identity ≥0.80 · B3 swap again ≥0.75  

Seeds {3041,3051} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS with disarm doctrine. Miss if multi-step soft residual accumulates.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Multi-trial swap↔identity via diagonal soft-cuts after full restore.
