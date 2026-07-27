# BP-E121 — Soft split R0 multi-trial selective: silence both → restore 00 → re-cut 00

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E119 PASS; E117 multi-trial shared (dual restore)  
**Discipline:** multi-trial **selective** cycle on non-shared R0a/R0b — not dual restore of both arms

## Hypothesis
Split topology E119. Soft dual-cut all; restore all.  
1. Soft-cut 00+10 → both R0a/R0b silent, R1 ON ≥0.80  
2. Soft restore only 00 → L0 R0a+R1 ON; L1 R0b OFF ≥0.80  
3. Soft re-cut only 00 → L0 R0a OFF R1 ON; L1 R0b still OFF ≥0.80  

## Bars
B1 dual silence ≥0.80 · B2 selective restore ≥0.80 · B3 selective re-cut ≥0.80  

Seeds {3341,3351} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS. Completes multi-trial L-selective reconfig on non-shared endpoints.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Multi-trial selective on split R0: silence both → restore 00 → re-cut 00, L1 stays isolated. Non-shared multi-trial L-selective reconfig closed.
