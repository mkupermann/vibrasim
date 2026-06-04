# JEP-33 — fix the is_a sibling residual with a lateral-displacement feature

## Motivation
JEP-32's calibrated is_a still false-positived on SIBLINGS (is_a(cat,dog)=True): siblings are close in distance
with ~0 norm gap, near the classifier boundary. Key geometric distinction: ancestor-descendant pairs are RADIAL
(distance ~= radius gap), siblings are LATERAL (distance > radius gap). Add lateral = d_hyp(a,b) - |rad(a)-rad(b)|
as a 3rd feature (~0 for ancestors, >0 for siblings) so the classifier can reject siblings.

## Pre-registration (locked BEFORE run)
- is_a classifier features: [hyperbolic distance, norm gap, lateral displacement]. Same calibration.
- Bars: is-a classification accuracy >= 0.90 AND is_a(cat,dog)=False (sibling rejected) AND the JEP-32
  cross-branch cases still correct (rose NOT is_a animal, cat is_a mammal). PASS = sibling residual fixed without
  regressing. NULL/PARTIAL otherwise. Entailment-cone idea (Ganea 2018) established - named as such.

## Result — NULL (lateral feature did not fix siblings; reverted)
| sibling | is_a (with lateral feature) | expected |
|---------|------------------------------|----------|
| cat/dog | True | False |
| eagle/sparrow | True | False |
| oak/pine | False | False |
classification acc 0.952 (TNR 0.905) - basically unchanged from JEP-32's 0.96/0.92.

**VERDICT: NULL - geometric assumption refuted.** The lateral-displacement feature (d - radius-gap) did NOT
reject siblings: cat/dog and eagle/sparrow stayed false-positive, accuracy slightly DROPPED (0.96 -> 0.952). The
assumption was wrong: the ancestor-RANKING loss pulls siblings CLOSE (both near their shared parent), so siblings
have SMALL distance and SMALL lateral displacement - they look like ancestor pairs. Distance-based features
cannot separate them; the proper fix is ENTAILMENT CONES (angular containment - a is in b's cone only if
angularly within b's aperture, which siblings violate; Ganea et al. 2018), which I did not implement (diminishing
returns on this specialized point). REVERTED to the JEP-32 2-feature classifier (0.96). Honest residual stands:
is_a is reliable for cross-branch + ancestor/non-ancestor but can false-positive on same-parent siblings. Bars
locked, not tuned.
