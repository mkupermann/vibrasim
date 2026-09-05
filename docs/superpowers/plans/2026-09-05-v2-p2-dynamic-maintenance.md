# V2-P2 dynamic-maintenance implementation plan

**Goal:** Implement and execute the frozen P2 replacement-foundation experiment
without generating a P2 trajectory until identity, invariants, artifacts, and
tests are in place.

## 1. Identity and immutable domain values

- Add `vibrasim2/p2/registration.py` with committed document digests and paths.
- Add immutable P2 configuration, arms, cells, bond state, and full state types.
- Test exact registered values, candidate generation, immutability, and invalid
  state rejection.

## 2. Energy and bond-event primitives

- Test and implement bounded positive-work capture with exact kinetic debit.
- Test and implement deterministic formation, valence limit, finite ageing,
  expiry, spring-potential return, and formation sink accounting.
- Test local force antisymmetry and formation-time zero spring energy.

## 3. Integrator and ledger

- Test and implement the registered split-step order and all three arms.
- Add total-accounted-energy and bond-time measurements.
- Test no-capture impossibility, deterministic events, and short-run energy
  tolerance before any registered trajectory.

## 4. Persistence, verdict, and guards

- Add append-only cell journals, run manifest, result, canonical digest, resume
  rejection, and finite-value validation.
- Add frozen gate evaluation and tests for PASS, NULL, INCONCLUSIVE, and FAIL.
- Add a P2 budget ledger and scientific-core digest guard.

## 5. Visible observation

- Extend observation envelopes with live/dormant candidate states and reservoir
  intensity without changing scientific identity.
- Extend the PyVista renderer and add a replay loop option.
- Test projection isolation and observer-failure containment.

## 6. Registered execution and closeout

- Run the complete non-experimental suite.
- Commit the frozen scientific core and its digest.
- Launch exactly one registered run with the visible observer.
- Verify artifacts independently, classify without threshold changes, update
  README/LOGBOOK/FRONTIER, and rerun the complete suite.

