# BP-E29 — Two-hop charge relay L→M→R

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E14/E21 peak+latch; PRIM5 pair-link

## Hypothesis
Three ports x=20,40,60 (midplane OFF so bridges span). PRIM5 links L–M and M–R (exclusive pairs). Force-fire L; peak/latch charge on R ≥ **1.0** in ≥0.90 trials.  
Control: only L–M link (no M–R) → peak R latch ≤ **0.25** in ≥0.90 trials.  
Both links present in treat ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: max R latch peak ≥1.0 rate | ≥0.90 |
| B2 | No M–R link: max R latch peak ≤0.25 rate | ≥0.90 |
| B3 | Treat has ≥2 cross-span bridges | ≥0.90 |

Seeds {961,971} trials 10. N_write=12. Smoke 1×3.

## Prediction
🔮 PASS — charge prop along path.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Two-hop L→M→R charge relay works; no M–R silent.
