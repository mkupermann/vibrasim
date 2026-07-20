# BP-E54 — Hard mid kill (r=12) + full three-hop restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E51 NULL (r=8 miss); E43 retrain after hard cut; E52 soft full restore  
**Discipline:** not E51 bar retune — r=12 hits A/B (dist≈11); restore **all three hops**

## Hypothesis
Path L–A–B–R. I at A–B mid with `fire_kill_bridge_radius=12` (reaches A and B endpoints; also kills bridges sharing those endpoints).
1. Fire L → R ON ≥0.90  
2. Fire I → fire L → R OFF ≥0.90  
3. Restore L–A + A–B + B–R → fire L → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 initial ON | ≥0.90 |
| B2 hard mid OFF | ≥0.90 |
| B3 full restore ON | ≥0.85 |

Seeds {1601,1611} trials 8. Budget ~3 min, hard cap 6 min.

## Prediction
🔮 LEAN PASS (E43-class retrain after structural kill on longer chain).  
Miss if kill removes nodes/emitters needed for ILW rewrite, or if r=12 still insufficient on this geometry.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Hard mid kill r=12 silences 3-hop; full three-hop ILW retrain restores. Complements E51 (r=8 miss) and E52 (soft full restore).
