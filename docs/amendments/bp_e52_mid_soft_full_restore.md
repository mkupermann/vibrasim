# BP-E52 — Mid soft-cut + full three-hop restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E50 NULL (mid soft silences; A–B-only restore fails); E44 full-path restore  
**Discipline:** not E50 bar retune — same cut geometry, restore **all three hops**

## Hypothesis
Path L–A–B–R. Same soft mid-cut as E50 (`fire_weaken_bridge_radius=12`, I at A–B mid).
1. Fire L → R ON ≥0.90  
2. Fire I → fire L → R OFF ≥0.90  
3. Restore **L–A + A–B + B–R** → fire L → R ON ≥0.85  

If E50 failed because I collaterally weakens L–A and B–R, full three-hop restore must recover.

## Bars
| ID | thr |
|----|-----|
| B1 initial ON | ≥0.90 |
| B2 mid-cut OFF | ≥0.90 |
| B3 full restore ON | ≥0.85 |

Seeds {1561,1571} trials 8. Time budget ~3 min, hard cap 6 min.

## Prediction
🔮 LEAN PASS (mirrors E44). Miss if soft weaken permanently damages nodes not just bridge strength.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Full three-hop restore recovers path after mid soft-cut. Closes E50 implication: mid I collaterally weakens outer hops; A–B-only insufficient; full L–A+A–B+B–R retrain works (E44-class).
