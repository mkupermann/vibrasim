# V2-P2 closeout: dynamic maintenance

**Run:** `archive/run-logs/v2-p2/2026-09-05-observed-001/`

**Verdict:** `INCONCLUSIVE`

**Scientific digest:** `530feabb76da1b4e8a5ec40dc10842e975a9cdba486088290eccf50def50a1f9`

## What ran

The one authorised P2 matrix ran on 2026-09-05 with the process-isolated 3D
observer attached. All 18 registered cells completed. The observer consumed
only snapshots that had already been persisted and had no path back into the
simulation or verdict.

The complete repository suite had passed immediately before execution: 957
tests passed, 5 were skipped, and 2 were expected failures. The P2 budget guard
bound the run to scientific-core SHA-256
`b0d356b515a06c8194d11479fcb45102e9b168ccbafe3f4ffcb4e2561199c9fd`.
The ledger closed as `used` after 366 seconds.

## Registered evidence

- All values were finite and all persisted scientific artifacts were valid.
- Maximum absolute energy drift was below `6.24e-5` in every primary cell and
  below `1.56e-5` in every half-step cell, inside the frozen `2e-4` limit.
- Every `no_capture` cell produced exactly zero bond-time.
- Every reproduction cell matched its primary `full` cell exactly in event
  order and bond-time.
- Aggregate primary contrast (`full - no_field_feedback`) was `-5.875`, below
  the frozen `+30.0` scientific gate.
- Half-step aggregate contrast was `-8.7125`. It had the same sign, but its
  relative difference from the primary contrast was approximately `0.483`,
  above the frozen `0.20` convergence limit.

Verdict precedence makes a failed numerical-validity gate `INCONCLUSIVE`, even
when the scientific contrast also fails. The result is therefore neither a
PASS nor a clean NULL.

## Why there is no rerun

The persisted evidence and code review identify no artifact, reproduction,
energy-accounting, or implementation defect that can be repaired while leaving
the scientific identity unchanged. The residual failure is sensitivity of the
thresholded bond-event sequence to the registered timestep. Changing the
integrator, event rule, timestep, horizon, constants, aggregation, or gates
would change the experiment after seeing its data.

The preregistration permits a rerun after `INCONCLUSIVE` only for a documented
repair that leaves scientific constants and gates unchanged. No such repair is
identified. P2 therefore closes without a rerun. P3 is not opened: doing so
without a new independent physical argument would be result-driven mechanism
search, not continuation of the registered question.

## Claim boundary

P2 does not show that field feedback sustains bonds. It also does not establish
that no possible dynamic-maintenance mechanism can work. It shows that this
specific deterministic six-site construction did not yield a numerically
converged positive field-feedback advantage under its frozen test.
