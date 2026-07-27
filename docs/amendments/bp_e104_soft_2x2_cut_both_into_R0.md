# BP-E104 — Soft 2×2 full restore then soft-cut both arms into R0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E101–E103 NULL (single-arm re-cut fails)  
**Discipline:** not single-arm retune — soft-cut **00 and 10** (all paths into R0) after full restore

## Hypothesis
Wide 2×2 full restore. Soft-cut 00 then 10 (both arms that terminate at R0).
1. After full restore: L0 fan-out both R ≥0.80  
2. Soft-cut 00+10: L0 → R0 OFF, R1 ON ≥0.80  
3. L1 → R0 OFF, R1 ON ≥0.80  

## Bars
B1 L0 fan-out ≥0.80 · B2 L0 only R1 ≥0.80 · B3 L1 only R1 ≥0.80  

Seeds {2941,2951} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if cutting both R0 in-edges silences R0 for all L. Miss if residual R0 bridges remain.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft-cut **both** R0 in-edges (00+10) after full restore silences R0 for L0 and L1 while R1 stays ON. Closes E101–E103: need cut all in-edges of a shared endpoint.
