# BP-E68 — Soft 2×2 concurrent dual-drive under swap

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E67 concurrent identity PASS; E59 swap  
**Discipline:** not E67 retune — **swap** arm select (01+10) with concurrent L0+L1

## Hypothesis
Soft-select swap (keep 01+10, cut 00+11).  
1. Concurrent L0+L1 → R0 ON and R1 ON ≥0.80  
2. L0 only → R1 ON, R0 OFF ≥0.80 (swap map)  
3. L1 only → R0 ON, R1 OFF ≥0.80  

## Bars
B1 concurrent both ≥0.80 · B2 L0→R1 only ≥0.80 · B3 L1→R0 only ≥0.80  

Seeds {1991,2001} trials 6. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS (E67+E59 composition). Miss if swap residual arms leave identity bleed.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Concurrent dual-drive under swap: both R ON; L0→R1 and L1→R0 isolation holds.
