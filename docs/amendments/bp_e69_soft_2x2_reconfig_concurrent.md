# BP-E69 — Soft 2×2 reconfigure curriculum with concurrent probes

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E67 identity concurrent; E68 swap concurrent; E59 sequential reconfig  
**Discipline:** multi-step identity→swap→identity with **concurrent** L0+L1 probe each step

## Hypothesis
Same four arms. Soft select:
1. Identity → concurrent both R ON ≥0.80  
2. Swap → concurrent both R ON ≥0.80  
3. Identity again → concurrent both R ON ≥0.75  

## Bars
| ID | thr |
|----|-----|
| B1 identity concurrent | ≥0.80 |
| B2 swap concurrent | ≥0.80 |
| B3 re-identity concurrent | ≥0.75 |

Seeds {2041,2051} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Miss if multi-step soft cuts accumulate collateral damage.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft 2×2 reconfig identity→swap→identity with concurrent dual-drive probes.
