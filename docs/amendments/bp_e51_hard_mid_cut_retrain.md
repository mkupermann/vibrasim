# BP-E51 — Hard mid-hop cut + mid-only retrain (3-hop)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E50 NULL (soft mid restore failed); PRIM12 hard cut  
**Discipline:** not E50 soft retune — **hard kill** mid-link only, retrain A–B

## Hypothesis
L–A–B–R. I at midpoint A–B with small `fire_kill_bridge_radius=8` covering only A–B region.
1. Fire L → R ON ≥0.90  
2. Fire I → bridges drop; fire L → R OFF ≥0.90  
3. Retrain A–B only → fire L → R ON ≥0.85  

## Bars
B1 ≥0.90 · B2 ≥0.90 · B3 ≥0.85

Seeds {1541,1551} trials 8.

## Prediction
🔮 LEAN PASS if kill is spatial-local to A–B; miss if L–A or B–R also killed.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Hard kill at geometric A–B mid with `fire_kill_bridge_radius=8` never silences: A and B sit at dist≈11 from I, so endpoint-radius kill never touches path bridges. Not a soft-retune of E50 — geometry miss under pre-registered r=8.
