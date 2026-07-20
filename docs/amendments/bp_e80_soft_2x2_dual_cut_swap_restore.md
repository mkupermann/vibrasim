# BP-E80 — Soft 2×2 dual-cut then selective swap restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E79; E68 swap concurrent  
**Discipline:** soft-cut all arms; disarm; restore **only 01+10**; concurrent + single-L swap map

## Hypothesis
1. Soft-cut all → concurrent both R OFF ≥0.80  
2. Disarm; restore swap arms 01+10 → concurrent both R ON ≥0.80  
3. L0 only → R1 ON R0 OFF ≥0.80  

## Bars
B1 both OFF ≥0.80 · B2 swap concurrent ON ≥0.80 · B3 L0→R1 only ≥0.80  

Seeds {2441,2451} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS (E79 mirror for swap). Miss if identity residual bridges survive dual cut.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut; selective swap restore recovers concurrent routing and L0→R1 map.
