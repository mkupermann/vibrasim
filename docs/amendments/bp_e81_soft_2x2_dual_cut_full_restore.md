# BP-E81 — Soft 2×2 dual-cut then full restore all arms

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E79/E80 selective restores  
**Discipline:** soft-cut all four arms; disarm; restore **00+01+10+11**; concurrent + isolation

## Hypothesis
1. Soft-cut all → concurrent both R OFF ≥0.80  
2. Disarm; restore all four arms → concurrent both R ON ≥0.80  
3. Under full restore, L0 lights **both** R0 and R1 (OR fan-out) ≥0.80  

Wait - with all arms, L0 should light R0 and R1 both. Yes fan-out.

## Bars
| ID | thr |
|----|-----|
| B1 both OFF after cut | ≥0.80 |
| B2 concurrent both ON after full restore | ≥0.80 |
| B3 L0 lights both R0 and R1 | ≥0.80 |

Seeds {2461,2471} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Miss if dual cut permanently damages nodes.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut then full four-arm restore; concurrent ON; L0 fan-out both R.
