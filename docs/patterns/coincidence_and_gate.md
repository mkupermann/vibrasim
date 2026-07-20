# Pattern: Coincidence AND gate

## Source
PRIM9-D0 PASS · E38 NULL (OR without gate)

## Claim
With `coincidence_and_enabled` and `k_coincidence_gate[mid]=1`, bridge prop into mid requires **≥2 distinct firers same tick**. Downstream M→R is ungated.

## Use
Fan-in AND logic. Pair with E34 OR (gate off).

## Wipe-restore
Soft dual wipe both L inputs then full restore recovers dual-fire AND (E128 PASS). Hard dual wipe + restore same (E129 PASS). Multi-trial soft wipe-restore cycle (E130 PASS). Hard single-arm disable/restore still E63/E64.

## Honesty
Engineered coincidence filter — not emergent free chemistry.
