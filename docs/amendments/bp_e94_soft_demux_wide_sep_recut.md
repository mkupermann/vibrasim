# BP-E94 — Soft DEMUX wide y-separation full restore + soft re-cut arm0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E92 NULL (collateral r=10 vs y-sep=13)  
**Discipline:** not E92 retune — **wider y-sep (10, 32, 48)** so mid distance ≥18 > soft r=10

## Hypothesis
Shared L; arms at y=10,32,48. Soft dual-cut all; restore all; soft re-cut arm0 (r=10).
1. After full restore: all three R ON ≥0.80  
2. Soft-cut arm0 → R0 OFF ≥0.80  
3. R1 and R2 still ON ≥0.80  

## Bars
B1 all ON ≥0.80 · B2 R0 OFF ≥0.80 · B3 R1&R2 ON ≥0.80  

Seeds {2721,2731} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if geometry was the E92 failure mode. Miss if shared-L soft cut is inherently non-local.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Wide y-sep (mid dist 18 > r=10) allows soft re-cut arm0 without collateral. Closes E92 geometry diagnosis.
