# G177 — L0 frozen execution contract

2026-09-16. Michael authorised the next step with "go": freeze, execute the
30-seed G176 matrix, verify artifacts and report the unchanged verdict.

G176 defines the candidate, tasks, controls and all scientific thresholds.
No parameter, threshold, seed or task is changed here. This contract adds
execution/provenance requirements, not another scientific hypothesis.

## Fixed execution

- One run only; seeds 0–29 in ascending order. Five arms per seed, 1200 training
  attempts per phase, 200 held-out contexts per task, blocks of 20.
- Run manifest records SHA-256 of code, both protocols and the resource report;
  Python and NumPy versions; constants, stream mapping and data budgets.
- Manifest and output directory are created exclusively before seed 0. No
  overwrite, resume, seed replacement or automatic retry of a failed matrix.
- Runtime budget is **7140 seconds**, measured with a monotonic clock starting
  before manifest creation. It includes original generation, deterministic
  artifact replay and final evaluation. Memory ceiling is 2 GiB peak resident
  process memory; individual learner state ceiling remains 100 MiB.
- The 59-minute earlier projection concerned generation only. Full-memory
  charging of every arm was conservative; the fixed 119-minute ceiling is
  retained for generation plus verification. If insufficient, report FAIL;
  do not extend it after observing results.
- Check the original deadline before/after each block, evaluation and seed,
  and on finalisation. Suspension does not reset the deadline.
- Resource checks are cooperative between bounded operations, not an OS kill
  limit. A limit breach invalidates the entire run even if all scores exist.

## Artifact verification

For every seed, reproduce the identical fixed sequence in a temporary directory.
This is a deterministic audit of the same data, not another independent seed or
an opportunity to choose better results. Compare every training event, checkpoint,
evaluation action/reward and metric exactly. Compare NPZ datasets by array content
because ZIP timestamps are not scientific data. Compare the exact file inventory.
Delete only the temporary replay directory through its scoped context manager.

Retain original raw data, per-seed file hashes, the frozen manifest, process
duration/memory and all 30 seed metrics. Before final judgment recheck source/
environment hashes and the complete original inventory. `summarize` consumes
only these verified metrics. Hashes establish consistency, not a trusted third-party
timestamp or authenticity signature.

## Ordered verdict and stop

1. Any code/manifest/data/replay/resource violation → FAIL, stop, preserve evidence.
2. A documented external interruption with incomplete seeds → INCONCLUSIVE.
3. Otherwise apply G176's PASS-LERNEN / NULL, with baseline advantage, adaptation
   and retention reported independently. No post-data threshold tuning.

Both positive and negative results end this candidate run. No automatic new
variant, parameter search or P0–P3 rerun. Mathematical novelty remains unproven.

## Delivery budget and forecast before data

Launcher work begins 2026-09-16 12:05 Europe/Berlin: plan 30 minutes, ceiling
60 minutes to implement/test/freeze. Then the independent 7140-second experiment
budget starts. This is a newly authorised task; the previous implementation
budget failure remains recorded and is not erased.

Qualitative expectation: detectable phase-A learning is plausible, but the
absolute 0.50 bar and superiority over the nearest-positive reference are
uncertain. The conflicting A/B tasks may cause substantial interference.
This is not a numerical probability forecast and does not change the criteria.
