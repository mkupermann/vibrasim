# JEP-149 — spatial reasoning with frames of reference (perspective transform)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: transitive spatial inference (A left B, B left C => A left C); inverse (A left B => B right A); and the
  PERSPECTIVE transform (A left B from the OPPOSITE viewpoint => A right B; above/below viewpoint-invariant). MOST-
  LIKELY MISS: the left/right (and front/behind) flip vs above/below invariance.

## Acceptance
- PASS: spatial battery = 100% (transitive + inverse + perspective). Established (qualitative spatial reasoning +
  frames of reference; Levinson), named; no novelty.

## Result — PASS (HIT)
Spatial battery 9/9: transitive (cup left plate, plate left fork => cup left fork); inverse (plate right cup, fork
right cup); default view (cup NOT right plate); PERSPECTIVE — from the opposite viewpoint cup is RIGHT of plate
(left<->right flip) and NOT left of plate; above/below VIEWPOINT-INVARIANT (lamp above table from either side).
Prediction HIT; tally 44/63; 39 tests gated green. A genuinely distinct faculty (qualitative spatial reasoning +
frames of reference, Levinson) — the perspective transform (allocentric left/right flip, above/below invariant) is
the part pure ordering can't capture. Established (qualitative spatial calculi + frames of reference), named; no
novelty. HONEST: a single opposite-viewpoint transform (not arbitrary rotations); qualitative (no metric distances).
