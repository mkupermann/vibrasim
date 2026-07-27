# Pattern: Coincidence AND gate

## Source
PRIM9-D0 PASS · E38 NULL (OR without gate)

## Claim
With `coincidence_and_enabled` and `k_coincidence_gate[mid]=1`, bridge prop into mid requires **≥2 distinct firers same tick**. Downstream M→R is ungated.

## Use
Fan-in AND logic. Pair with E34 OR (gate off).

## Wipe-restore
Soft dual wipe both L inputs then full restore recovers dual-fire AND (E128 PASS). Hard dual wipe + restore same (E129 PASS). Multi-trial soft (E130) and hard (E132) wipe-restore cycles PASS.

**Selective re-arm after dual wipe:** Soft dual wipe + restore L1 only (with or without M–R rewrite) already dual ON (E131/E134 NULL — soft residual L2–M). **Hard dual wipe** + restore one arm only keeps dual OFF until the other is restored — L1-first (E133), L2-first (E136), multi-trial L1 cycle (E135). Doctrine: selective single-arm re-arm of AND after dual silence needs **hard** dual wipe, not soft; order-symmetric.

Hard single-arm disable/restore still E63/E64.

**Hybrid AND∨OR hard selective:** Hard dual wipe of AND arm + OR bypass, then restore AND-only (E137) or OR-only (E138) — both PASS. Completes hard matrix alongside soft E75/E76. Multi-trial hard path-switch both orders (E139/E140) matches soft E78. Cascade multi-hop (L1∧L2)→M→A→R: soft/hard wipe-restore (E141/E142), hard selective L1/L2 orders + multi-trial (E143–E145) all PASS. Hybrid cascade (+ OR bypass): hard selective cascade AND (E146) or OR (E147) PASS; multi-trial hard path-switch both orders (E148/E149) PASS. Dual parallel cascade ANDs: hard selective path0/path1 (E150/E153), multi-trial selective (E152), hard wipe-restore both (E151) PASS.

## Honesty
Engineered coincidence filter — not emergent free chemistry.
