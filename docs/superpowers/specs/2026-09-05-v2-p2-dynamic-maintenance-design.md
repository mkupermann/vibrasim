# Vibrasim II P2: Dynamic-maintenance foundation candidate

**Status:** approved by the user's standing instruction to continue autonomously; frozen before implementation and before any P2 trajectory exists

## Why this is P2

P0 returned NULL: supplied cycle and branch topologies did not produce the
registered topology-dependent reciprocal channel. P1's read-only audit found no
pre-registered time-structure rescue. The original ladder therefore has no
admissible basis for its planned individuation experiment.

P2 is a replacement foundation experiment, not the original ladder's
individuation claim. It tests a different mechanism already required by the
charter: a closed causal loop in which field work can pay for finite-lived local
bonds and those bonds alter subsequent field propagation.

## One question

After one finite field pulse, does the fully reciprocal system accumulate more
post-drive live-bond time than matched systems in which either field-to-matter
energy capture or bond-to-field feedback is disabled?

## State and local laws

The field and matter coordinates retain P0's dimensionless lattice Hamiltonian.
P2 adds, per matter site, a non-negative energy reservoir and, per geometrically
local candidate pair, an optional bond with an age and two formation-time rest
offsets.

Candidate pairs are generated solely from the fixed spatial neighbourhood of
the coupling sites. They are not supplied as a target topology and are ordered
lexicographically only to make simultaneous events deterministic.

During each step, positive reciprocal field-to-matter work may be captured into
the local reservoir. The same amount is removed from matter kinetic energy.
Capture therefore transfers energy; it does not create it.

A candidate bond forms only when its two endpoint reservoirs can jointly pay
the fixed formation cost. The cost is debited equally. Its matter and field rest
offsets are the offsets at formation, so bond creation introduces no spring
potential discontinuity.

Every live bond has the same finite lifetime. While alive it applies the same
Hooke law to its matter endpoints and to the corresponding field sites. This is
the sole geometry-to-field constitutive law. At expiry, remaining matter and
field spring potential is returned equally to the endpoint reservoirs before
the bond disappears.

No identity, reward, label, target shape, learned parameter, or topology score
is available to the dynamics.

## Arms

- `full`: reciprocal field/matter force, energy capture, bond formation, and
  bond-to-field feedback are enabled.
- `no_capture`: identical forces and candidates, but field work cannot enter a
  formation reservoir; therefore no bond can be paid for.
- `no_field_feedback`: capture and matter bonds remain enabled, but live bonds
  do not alter the field.

All arms receive the identical pulse, seed, integration grid, and candidate
neighbourhood.

## Frozen primary measurement and verdict

The primary measurement is post-drive bond-time, the time integral of the live
bond count from the end of the pulse to the registered horizon.

P2 is `PASS` only if all of the following hold:

1. `full` exceeds `no_field_feedback` by at least one complete bond lifetime;
2. `no_capture` has zero bond-time;
3. the primary contrast has the same sign and remains within 20% relative error
   under the registered half-step convergence run;
4. an exact same-seed reproduction matches all discrete bond events and the
   primary statistic;
5. the energy ledger closes within the registered numerical tolerance.

It is `NULL` when execution is valid but either scientific contrast gate fails.
It is `INCONCLUSIVE` when convergence, reproduction, or energy-accounting gates
fail. Infrastructure failure is `FAIL` and has no scientific interpretation.

No threshold may be changed after a P2 trajectory exists. A NULL does not permit
a sweep; it closes this candidate.

## Observation

The existing process-isolated 3D observer will be extended to show candidate
sites, live bonds, reservoir intensity, pulse progress, arm, and tick. Frames
are copied only after persistence. Dropped or closed viewer frames cannot affect
the run, ledger, or verdict.

## Implementation order

1. Freeze exact constants and manifest identity.
2. Implement energy-transfer and bond-event primitives test-first.
3. Implement arms, ledger, artifacts, and verdict test-first.
4. Extend the observer projection and 3D rendering.
5. Run the complete software suite.
6. Start one registered visible run, then classify and document it without
   parameter changes.
