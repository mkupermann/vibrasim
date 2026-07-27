# BP-E53 — Mid soft-cut + outer-only restore (skip A–B)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E50 NULL (A–B-only fail); E52 PASS (full three-hop restore)  
**Discipline:** same E50 mid soft geometry; restore **L–A + B–R only** (no A–B rewrite)

## Hypothesis
Path L–A–B–R. Soft mid I (`fire_weaken_bridge_radius=12`).  
E50: A–B-only restore fails. E52: full restore works.  
If I collaterally zeros **all three** hop classes, then restoring only outer hops L–A and B–R (leaving mid A–B unrestored) still fails.

1. Fire L → R ON ≥0.90  
2. Fire I → fire L → R OFF ≥0.90  
3. Restore **L–A + B–R only** → fire L → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 initial ON | ≥0.90 |
| B2 mid-cut OFF | ≥0.90 |
| B3 outer-only restore ON | ≥0.85 |

Seeds {1581,1591} trials 8. Budget ~3 min, hard cap 6 min.

## Prediction
🔮 LEAN **NULL** (A–B also damaged by mid I; outer-only insufficient).  
PASS would mean mid A–B bridges survive soft cut better than outer hops.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Outer-only restore insufficient — mid A–B hop also damaged by soft I. Together with E50 (A–B-only fail) and E52 (full PASS): **all three hops must be restored** after mid soft-cut.
