# P3: seeded open-system maintenance — engineering experiment

Authorised by Michael on 2026-09-06 after the P2 closeout. This decision
supersedes the programme-wide stop, not P2's INCONCLUSIVE result or one-run lock.
P3 is an engineering construction, not the charter's organisational-memory rung.
It replaces the wave Hamiltonian with an explicitly dissipative energy-transport
network. It cannot establish physical matter, emergence or individuation.

## Frozen model, before data

Six sites on a ring; candidates are consecutive neighbours including (0,5).
All six initial bonds are supplied and their total formation cost 1.2 is
accounted as initial consumed energy. No later target or repair table exists.
Each bond expires after exactly 5 time units. A candidate forms whenever each
endpoint holds 0.1 energy; 0.2 is consumed per formation. Pair priority is
lexicographic. Initial field and reservoirs are zero.

Nonnegative site energy e diffuses along every candidate with conductance
0.02 + 2*b, where b is live-bond presence. A constant source supplies site zero
with 1 energy/unit time. Each site transfers 0.3*e per unit time to its local
reservoir. Reservoir leakage is 0.2*R, capacity is 0.3; leakage and overflow are
exported heat. The initial ring is deliberately engineered. This model tests
whether transport supports paid local renewal, not spontaneous ring formation.

Explicit simultaneous Euler transport and absorption use the old field;
then reservoir leakage, capacity overflow, scheduled intervention, bond expiry
and lexicographic funded formation. All transfers enter a conservation ledger:
field + reservoirs + consumed formation + exported heat + damage export
= initial supplied formation energy + cumulative source input.
Lifetime uses integer birth ticks, avoiding accumulated float age errors.

Arms: full; no_feedback (conductance 0.02 regardless of bonds); no_capture
(absorption becomes exported heat); drive_off (source zero from t=40);
damaged (at t=40 remove edges (1,2),(4,5) and export all reservoir energy).
Damage is an intervention only; formation rules have no knowledge of removed edges.
Duration 120; dt=0.02 primary and 0.01 convergence, all five arms. Repeat full
primary once. Eleven cells total, no seed or calibration. Snapshots every 0.2
simulation units, persisted and emitted during stepping. Display pacing is
wall-clock only, does not enter equations. Field is shown as height, reservoir
as point colour; live bonds as lines in the existing 3D observer.

## Frozen verdict and stop

FAIL: missing/invalid artifacts or configuration. INCONCLUSIVE: nonfinite or
negative state, ledger residual >1e-9, any arm's late mean bond count differs
by >0.25 between timesteps, or full reproduction differs in ordered events.
Otherwise PASS only if mean live bonds over [100,120] is >=5 for full and
damaged, <=3 for no_feedback, exactly zero for no_capture and drive_off;
damaged must reach >=5 live bonds by t=60. Otherwise NULL.
These gates support only the engineered maintenance claim. One run allowed;
no parameter sweep or post-data retuning. Stop and document any failed gate.
Estimated implementation/verification/run budget 45 minutes; hard ceiling 90
minutes from this registration's commit. Record elapsed time honestly.

## Implementation and validation

Implement an isolated P3 module, exact ledger, streamed snapshots, manifest
bound to source/registration hashes, readback-based verdict, and CLI replay.
Test energy balance, finite lifetimes, local payment, damage accounting and
streaming before running the registered matrix. Run affected V2 tests; the
unchanged historical V1 suite already passed and need not be repeated.
