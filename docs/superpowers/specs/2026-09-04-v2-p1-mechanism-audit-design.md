# V2-P1 Mechanism Audit Design

**Status:** APPROVED DESIGN; FROZEN BEFORE P1 ANALYSIS, AFTER V2-P0 DATA.

## 1. Purpose and scientific boundary

V2-P0 returned `NULL`: the reciprocal Hamiltonian channel was numerically
valid, but the registered peak-transfer contrast between CYCLE and BRANCH did
not exceed `0.02` at any source centre. P0 therefore does not admit the planned
conditional-persistence rung.

P1 is a diagnostic audit of the already persisted P0 trajectories. It asks one
narrow question: did the two registered topologies produce a reproducible
time-structure difference that the P0 peak statistic discarded, or was their
effect weak throughout the trajectory?

P1 creates no simulation data, changes no P0 threshold, and cannot change the
P0 verdict. It makes no claim about persistence, bond formation, individuation,
memory, talent, life or cognition.

## 2. Evidence status

The source data already exist at
`archive/run-logs/v2-p0/2026-09-04-observed-001/`. The P0 result and its summary
metrics have been read. The time-series comparisons defined below have not been
computed when this design is frozen. This is therefore a prospective analysis
plan over existing data, not a preregistration made before data collection.

P1 must read the persisted `energy.jsonl` records only. Snapshot geometry and
3D observer events are outside the scientific input. The input `result.json`
scientific digest must equal
`bdf94735ba80fb719ac7f8e5c78b75705f706b9e5d8a179f09c199b6d838826e`
before analysis starts.

## 3. Compared traces

For each registered source centre, load the CYCLE and BRANCH full-channel
energy traces at `dt=0.05` and the corresponding convergence traces at
`dt=0.025`. Define

`m(t) = H_matter(t) / H_total(0)`

and the signed topology trace

`d(t) = m_cycle(t) - m_branch(t)`.

The coarse and convergence traces cover the same physical interval. Every
comparison between them evaluates the convergence trace at coarse timestamps;
no fitted interpolation is permitted.

## 4. Frozen measurements

For every source centre and timestep resolution, report:

- signed peak contrast already used by P0;
- `max_abs_contrast = max_t |d(t)|`;
- `rms_contrast = sqrt(mean_t d(t)^2)`;
- earliest time and sign at `max_abs_contrast`;
- each arm's earliest peak time;
- normalized cross-correlation lag between the demeaned CYCLE and BRANCH
  traces, searching integer lags corresponding to `[-10, +10]` simulation
  time units; ties choose the smallest absolute lag, then the negative lag;
- zero-lag correlation and best-lag correlation.

A trace with zero variance makes its correlations undefined and yields
`INVALID`, not zero correlation. All reported numbers use unrounded float64
inputs. JSON serialization may use round-trip-safe decimal rendering.

## 5. Convergence and integrity gates

The audit is valid only if all of the following hold:

1. the input digest matches the fixed digest in section 2;
2. all twelve required full-channel traces exist, are finite and contain the
   exact registered tick sequence;
3. CYCLE and BRANCH have identical timestamps within each comparison;
4. recomputed P0 `A_B` values agree with `result.json` within `1e-12`;
5. for every source, coarse and convergence `max_abs_contrast` differ by less
   than `0.002`, and the signs of `d(t)` at each resolution's own
   `max_abs_contrast` agree;
6. repeating the audit produces byte-identical canonical scientific output.

Failure of any item yields `INVALID`. No partial interpretation is allowed.

## 6. Ordered diagnostic outcome

After the integrity gates pass, evaluate outcomes in this order:

1. **TIME_STRUCTURE_CANDIDATE** when at least two of three source centres have
   converged `max_abs_contrast > 0.02`, the sign at that contrast agrees between
   coarse and convergence traces, and either:
   - the absolute best lag is at least `0.10` simulation time units and
     best-lag correlation exceeds zero-lag correlation by at least `0.05`; or
   - converged `rms_contrast > 0.01`.
2. **WEAK_CHANNEL** when all three converged `max_abs_contrast < 0.01`.
3. **UNRESOLVED** otherwise.

The strict inequalities are intentional. Exact boundary values fall through
to `UNRESOLVED`. These labels are diagnostic outcomes, not PASS/NULL/FAIL
verdicts and not evidence that a replacement observable is scientifically
important.

## 7. Consequences

- `TIME_STRUCTURE_CANDIDATE` permits one new foundation proposal with a new
  experiment ID, new data and an observable selected from this audit. Its
  acceptance threshold must be frozen without reusing P0 as confirmatory data.
- `WEAK_CHANNEL` closes this reciprocal Hamiltonian channel as a Vibrasim-II
  foundation. No parameter sweep or reduced threshold follows.
- `UNRESOLVED` also closes this dataset for design selection. A new mechanism
  requires an independent physical argument, not another analysis of P0.
- `INVALID` permits correction of the named analysis defect only; scientific
  output remains absent until the full audit is rerun.

No outcome admits conditional persistence directly.

## 8. Architecture

Create a separate `vibrasim2/p1/` package. Its analysis functions consume
immutable trace records and return frozen dataclasses without importing the P0
runner. A P1 artifact layer validates the source digest, writes one canonical
`audit.json` atomically, reads it back, and verifies a content digest. A small
CLI accepts exactly one P0 run directory and one new empty P1 output directory.

P1 must not import or invoke `run_trajectory`, mutate P0 files, or create a 3D
observer. A replay viewer may later display existing P0 snapshots, but it is a
separate non-scientific feature and is not part of this design.

## 9. Error handling and tests

Malformed, incomplete, redirected or digest-mismatched inputs fail before an
output directory is created. Existing or redirected output paths are rejected.
Atomic-write and readback failures yield no scientific artifact.

Tests cover the metric definitions with hand-calculated traces, lag tie
breaking, all four ordered outcomes, each integrity gate, deterministic
canonical serialization, path confinement, and the prohibition on simulation
entry points. The real P0 audit is a separately approved execution after the
implementation and test suite are committed.

## 10. Budget

Implementation and tests: 2 hours. Review and correction: 45 minutes. Real
audit and result review: 15 minutes. Realistic total 3 hours; hard ceiling
5 hours. A machine-readable ledger must be frozen with the implementation plan
before implementation begins. Crossing the ceiling stops work and requires a
new registration; elapsed time is never reset silently.
