# V2-P0 implementation-budget successor

**Status: FROZEN BEFORE THE CORRECTION; NO V2-P0 SCIENTIFIC DATA.**

## 1. Trigger and preserved record

The original registered implementation interval ended at
`2026-09-04T14:35:03.134629Z` after a ceiling-rounded 25,592 seconds. It exceeded
the frozen 19,800-second ceiling and is preserved verbatim in
`docs/vibrasim2/P0_BUDGET_LEDGER_OVERRUN_2026-09-04.json`. It is not extended,
reopened, or reclassified.

No V2-P0 scientific run was started under that ledger.

## 2. Authorized successor scope

This successor authorizes only implementation corrections found during the
post-implementation review, beginning with the following closure invariant:

> `finish_budget_interval` must reject a scientific-run or review closure when
> the active ledger's `scientific_core_sha256` differs from the immutable value
> captured in the corresponding `BudgetLease`.

The correction must be proved by a regression test that changes a budgeted file
and updates the active ledger digest to match that changed file. Closure must
still fail because the active digest is no longer the leased digest.

No model, fixture, scientific constant, threshold, evidence predicate, verdict
ordering, or registered execution matrix may change. This successor authorizes
no scientific execution.

## 3. Identity and budget

The scientific preregistration remains
`28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1`
because the scientific design is unchanged.

The successor uses a new machine-readable ledger at
`docs/vibrasim2/P0_BUDGET_LEDGER.json`, independently capped at 19,800 seconds.
The superseded overrun is retained in the archival ledger named above and is
not counted as time in the successor. All wall-clock intervals in the successor
must be recorded with actual UTC timestamps and ceiling-rounded whole seconds.
The existing 2,700-second run-and-review reserve remains unchanged.

Schema version 1 requires a first `implementation` interval. The successor
ledger therefore records its creation as a closed zero-second bootstrap interval
at the freeze instant: no budgeted source or test file is changed in that
interval. Every later source or test correction uses an actual
`implementation_correction` lease.

The productive guard may become runnable only after every authorized correction
interval is closed successfully, the active scientific-core digest matches the
repository, the cumulative successor duration remains below the ceiling, and
at least the existing reserve remains. A scientific run remains a separate,
explicitly approved action.
