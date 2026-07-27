# BP-E56 — Dual three-hop paths + selective hard kill

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E45 selective soft; E54 hard mid + full restore; E31 parallel isolation  
**Discipline:** hard analogue of E45 on **two 3-hop paths** with distinct mids

## Hypothesis
Path0: L0–A0–B0–R0. Path1: L1–A1–B1–R1. Spatially separated y.  
I0 at A0–B0 mid of path0 only; `fire_kill_bridge_radius=12`.
1. Fire L0 → R0 ON; fire L1 → R1 ON (≥0.90 each mean)  
2. Fire I0 → fire L0 → R0 OFF ≥0.90; fire L1 → R1 still ON ≥0.90  
3. Full restore path0 → fire L0 → R0 ON ≥0.85; path1 still ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 both initial ON | ≥0.90 |
| B2 selective (path0 OFF & path1 ON) | ≥0.90 |
| B3 restore path0 (both ON) | ≥0.85 |

Seeds {1641,1651} trials 6. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if y-separation keeps kill local. Miss if kill radius bleeds to path1.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard selective kill path0 with y-sep=14 and r=12; path1 intact; full path0 retrain restores. Hard analogue of E45 on dual 3-hop.
