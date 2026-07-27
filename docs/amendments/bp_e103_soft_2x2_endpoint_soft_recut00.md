# BP-E103 — Soft 2×2 full restore then soft re-cut 00 at R0 endpoint

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E101 NULL (I at mid fails)  
**Discipline:** not E101 mid retune — soft I placed at **R0 endpoint** for re-cut 00 (endpoint-local soft)

## Hypothesis
Same wide 2×2 as E101/E102. Soft dual-cut all; restore all; soft re-cut with I at R0 (not mid), r=8.
1. After full restore: L0 fan-out both R ≥0.80  
2. Soft-cut at R0: L0 → R0 OFF, R1 ON ≥0.80  
3. L1 → both ON ≥0.80  

## Bars
B1 L0 fan-out ≥0.80 · B2 endpoint soft cut R0 ≥0.80 · B3 L1 both ≥0.80  

Seeds {2921,2931} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if soft at R0 only hits bridges to R0. Miss if R0 shared with 10 path (L1–R0).

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0.  
Endpoint soft at R0 silences L0→R0 while keeping L0→R1 (B2 PASS), but **kills L1→R0 path too** (shared R0 endpoint) so B3 fails. Shared endpoints block single-arm selective soft cut on bipartite 2×2.
