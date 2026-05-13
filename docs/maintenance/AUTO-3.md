# AUTO-3 — Deterministic regression snapshot for default growth config

**Status: pre-registered. Not implemented.**
**Frozen: 2026-05-13. Author (pre-registration): Claude (autopilot setup session).**
**Reviewer at return: Michael Kupermann.**

## Why this exists

The growth-foundation config in `tests/test_substrate_growth_e2e.py::_growth_config(rng_seed=42)` is the project's reference substrate. Existing G-amendment tests (G1, G13, G14, etc.) already exercise specific substrate behaviors with seed 42 and assert exact counts (see `test_amendment_G1_bind_vibrations_jit.py`'s `_run_n_ticks` + count comparisons).

But the substrate as a whole has no end-to-end determinism canary. A future refactor that subtly changes RNG threading, ordering of binding-pair iteration, or numba kernel rewrite could silently break determinism — and the affected G-tests might still pass because they assert on subsets that happen to remain stable.

AUTO-3 adds one strict snapshot regression test: run the growth config for a fixed sim-duration, fixed seed, and assert the full structure-count vector matches a frozen snapshot. If anything changes the substrate's deterministic output, this test surfaces it loudly.

## What is built

Two new files:

1. `tests/test_regression_snapshot.py` — a fast snapshot test (≤30 sec, marked NOT slow) that:
   - Builds `_growth_config(rng_seed=42)`.
   - Evolves for 30 sim-seconds with a single burst injection every 0.5 sim-sec at `[30, 30, 30]` (same shape as F1).
   - Captures the structure-count vector: `(n_alive_vibrations, n_electrons, n_pairs, n_triads, n_atoms, n_molecules)` from `world.k_level` histogram.
   - Captures one scalar: total `world.k_count` (monotonic counter).
   - Compares to the snapshot file `tests/regression_snapshots/growth_default_seed42_30s.json`.
   - Fails on ANY difference (`==` comparison, no tolerance).

2. `tests/regression_snapshots/growth_default_seed42_30s.json` — the snapshot, captured by the autopilot during the run and committed.

The snapshot's structure:

```json
{
  "config_hash": "<sha256 of the dataclass repr>",
  "rng_seed": 42,
  "sim_duration_seconds": 30.0,
  "tick_dt": 0.016666,
  "burst_period_seconds": 0.5,
  "burst_position": [30.0, 30.0, 30.0],
  "expected": {
    "n_alive_vibrations": <int>,
    "n_electrons": <int>,
    "n_pairs": <int>,
    "n_triads": <int>,
    "n_atoms": <int>,
    "n_molecules": <int>,
    "k_count_total": <int>
  },
  "captured_at_commit": "<git sha at capture time>",
  "captured_at": "<iso datetime>"
}
```

The `config_hash` field guards against silent config drift: if `_growth_config()` is later edited, the hash changes, the test fails, and the snapshot must be re-captured deliberately.

## Acceptance — pre-registered

Test target: `tests/test_regression_snapshot.py`. The autopilot session implements this file AND captures the snapshot.

All five test items must hold for AUTO-3 to be marked **passed**:

1. `tests/test_regression_snapshot.py::test_snapshot_file_exists PASSES` — the JSON snapshot file is present and parses.
2. `tests/test_regression_snapshot.py::test_config_hash_matches_snapshot PASSES` — the snapshot's `config_hash` matches the dataclass repr hash at test time.
3. `tests/test_regression_snapshot.py::test_growth_default_seed42_30s_matches_snapshot PASSES` — running the 30-sec evolution produces exactly the structure-count vector in the snapshot.
4. `tests/test_regression_snapshot.py::test_growth_default_seed43_differs_from_snapshot PASSES` — running with `rng_seed=43` produces a DIFFERENT vector (sanity: seed actually matters; if not, RNG is broken).
5. `tests/test_regression_snapshot.py::test_snapshot_captures_within_30_seconds PASSES` — the test itself completes in <30 wall-clock seconds (pytest's `--durations` confirms).

## Negative control

Acceptance item 4 IS the negative control: a different seed must produce a different snapshot. If `rng_seed=43` produces the same counts as `rng_seed=42`, the test passes trivially and detects nothing — that is, it would be a state detector for "the substrate exists" not "the substrate is deterministic."

No matched-wallclock no-engram substrate experiment is meaningful for a determinism canary. The discriminating control is built into the test design.

## Risks the autopilot must respect

1. **Do NOT tune the snapshot to make the test pass.** The snapshot is captured from a clean run of unmodified substrate code. If running the test fails because the substrate's behavior has drifted in some other way (e.g., a recent commit changed binding semantics), the autopilot must NOT re-capture the snapshot. Instead: write the situation to `HUMAN_NEEDED.md`, mark item `blocked`, exit.

2. **Do NOT change `_growth_config()`.** It is the existing reference config. Any edit to it requires a CONCEPT amendment per the project's discipline.

3. **Do NOT introduce randomness beyond `rng_seed`.** The test must use ONLY the seed-driven RNG path. If the substrate has wall-clock or process-id-dependent randomness anywhere (it should not, but check), the test will be flaky — which itself is a finding that should go to LOGBOOK.

4. **30 seconds is generous but not infinite.** If the snapshot run consistently exceeds 30 wall-clock seconds locally, item is `null` with a postmortem noting the substrate has gotten slower since Plan A.5 baseline. Do NOT bump the threshold to 60s to make the test green — Michael will decide whether the slowness or the threshold is the problem on return.

## What this does NOT claim

- Does not claim the snapshot values are scientifically meaningful or "correct" in any research sense. The claim is purely: this is what the unmodified code produced on this date with this seed. Future drift will be visible.
- Does not validate the substrate against any external reference. There is no external reference for emergent substrate dynamics; that is the project's whole point.
- Does not cover other configs (calibration_session3.toml etc.). One snapshot, one config, one seed — a canary, not a coverage matrix. Future autopilot items can extend.

## Implementation hints (for the autopilot)

- Reuse `_growth_config` and `_inject_burst` and `_evolve` from `tests/test_substrate_growth_e2e.py`. Import them directly.
- For `config_hash`: use `hashlib.sha256(repr(cfg).encode()).hexdigest()[:16]`. Sixteen hex chars is enough to detect a typo without bloating the JSON.
- For the structure-count vector: `np.bincount(world.k_level[world.k_alive[:world.k_count]], minlength=6)`. Levels are: 0 vibration, 1 electron, 2 pair, 3 triad, 4 atom, 5 molecule.
- For `n_alive_vibrations`: `int(world.s_alive[:world.n_alive].sum())`.
- The snapshot is captured by the autopilot at test-implementation time: the first time the test runs, it sees the snapshot is missing, computes the vector, writes the JSON, and PASSES. On all subsequent runs, the snapshot exists and the test asserts equality.
- Wait. That auto-capture-on-first-run pattern is itself a silent-pass trap of the kind AUTO-1 detects. DO NOT do that. The autopilot must explicitly capture the snapshot in a separate step before committing the test, and the test must fail loudly if the snapshot file is absent.

## Out of scope for AUTO-3

- Snapshots for other configs.
- Cross-seed bootstrap statistics.
- Performance benchmarks (use the existing AP performance tests).

## Budget

- **Realistic**: 1 day (one autopilot tick).
- **Hard ceiling**: 3 attempts × 4h = 12h compute.

## What FAILED looks like

- Snapshot is non-deterministic (running the same config twice produces different vectors). → autopilot writes the finding to LOGBOOK as a real bug discovery, item is `null`.
- Test takes >30 wall-clock seconds. → `null` with timing post-mortem.
- Snapshot file is committed but `_growth_config()` later drifted; on retry the autopilot tries to re-capture rather than block. → CHARTER violation, prevented by acceptance item 2 (config hash mismatch fails the test).
