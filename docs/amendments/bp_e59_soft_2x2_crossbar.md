# BP-E59 — Soft 2×2 crossbar switch

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E49 MUX; E57 DEMUX; E45 selective soft  
**Discipline:** full bipartite L0,L1 × R0,R1 with soft arm select (not single-path MUX)

## Hypothesis
Four arms: L0–M00–R0, L0–M01–R1, L1–M10–R0, L1–M11–R1 (distinct y/z). Soft I on each M.  
1. **Identity select:** cut M01+M10; fire L0 → only R0 ON; fire L1 → only R1 ON ≥0.80  
2. **Swap select:** restore all, cut M00+M11; fire L0 → only R1; fire L1 → only R0 ≥0.80  
3. Re-select identity again ≥0.75 (multi-trial curriculum)

## Bars
| ID | thr |
|----|-----|
| B1 identity routing | ≥0.80 |
| B2 swap routing | ≥0.80 |
| B3 re-identity | ≥0.75 |

Seeds {1721,1731} trials 6. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS if soft radii local. Miss if shared L/R ports cross-contaminate latches.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft 2×2 crossbar: identity and swap routing via soft arm select; re-identity holds.
