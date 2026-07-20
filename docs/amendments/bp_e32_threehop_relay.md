# BP-E32 — Three-hop charge relay L→A→B→R

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E29 two-hop PASS; replace OFF multi-hop doctrine

## Hypothesis
Ports L(12)–A(30)–B(50)–R(68); pair-links L–A, A–B, B–R; replace OFF. Fire L → peak latch R ≥1.0 ≥0.90. Control missing A–B link → R peak ≤0.25 ≥0.90. Treat ≥3 bridges ≥0.90.

## Bars
| ID | thr |
|----|-----|
| B1 treat R peak≥1 rate | ≥0.90 |
| B2 no A–B: R peak≤0.25 rate | ≥0.90 |
| B3 treat n_bridges≥3 | ≥0.90 |

Seeds {1021,1031} trials 8.

## Prediction
🔮 PASS.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Three-hop relay works; broken mid-link silent.
