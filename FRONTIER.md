# FRONTIER — Vibrasim II

## Active programme: Vibrasim II / P1

There is one active question: `V2-P1 P0 mechanism audit`.

P0 returned `NULL`: the reciprocal channel was valid, but the registered
topology-difference gate did not hold. P1 asks whether the already persisted
P0 energy traces contain a converged time-structure difference that the P0 peak
metric discarded, or whether the channel remained weak throughout.

## Authority

1. `docs/vibrasim2/CHARTER.md`
2. `docs/superpowers/specs/2026-09-04-v2-p1-mechanism-audit-design.md` — frozen P1 contract
3. `archive/run-logs/v2-p0/2026-09-04-observed-001/result.json` — fixed P0 NULL input
4. `docs/amendments/v2_p0_reciprocal_channel.md` — historical P0 registration
5. newest entry in `LOGBOOK.md`

## Current state

- P0 completed `NULL` with all 30 registered cells and a verified digest.
- P1 is frozen after P0 data but before P1 time-series analysis.
- P1 creates no simulation data and cannot change the P0 verdict.
- The visual layer is a replay instrument, not evidence and not a 3D-world claim.
- The next valid action is implementing the frozen read-only P1 audit, followed
  by its separately budgeted execution against the fixed P0 digest.

## Preserved history

Vibrasim I is closed and retained. Its latest result remains BP-C6 / G174:
`INVARIANT (NULL)`. The unexecuted G175 draft is archived, not a live question.
The previous board is preserved at
`docs/archive/vibrasim_i/FRONTIER_2026-08-13.md`.
