# BP-E60 — Hard 2×2 crossbar switch

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E59 soft 2×2 PASS; E58 hard MUX  
**Discipline:** same bipartite L0/L1 × R0/R1 as E59; **hard kill** select (not soft)

## Hypothesis
Four arms L0–M00–R0, L0–M01–R1, L1–M10–R0, L1–M11–R1.  
Hard I on each M, `fire_kill_bridge_radius=10`.
1. Identity (keep 00+11, kill 01+10): L0→R0 only, L1→R1 only ≥0.80  
2. Swap (keep 01+10): L0→R1 only, L1→R0 only ≥0.80  
3. Re-identity ≥0.75  

## Bars
| ID | thr |
|----|-----|
| B1 identity | ≥0.80 |
| B2 swap | ≥0.80 |
| B3 re-identity | ≥0.75 |

Seeds {1771,1781} trials 6. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS (E59+E58 composition). Miss if hard kill prevents multi-step restore curriculum.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard 2×2 crossbar identity/swap/re-identity.
