# Flux Substrate F1 — Robustness Sprint, Iteration 3

> **Added 2026-05-15 23:10** after five NULLs (R-1c, R-1c-bis, R-1d, R-1c-tris, R-1d-T3). Two final pre-registered items before declaring iteration exhausted and surfacing to user on return.

## Iteration tally

| Item | Approach | Verdict |
|---|---|---|
| R-1c | Bénard multi-seed audit (R-1b baseline) | NULL: 0/10 trained, 2/10 spurious neg-control |
| R-1c-bis | Return-flow injector at cold ceiling | NULL: didn't fix |
| R-1d | Joint robustness gate (T1+T2+T3+T4) | NULL: T2 0/10, T3 2/10 |
| R-1c-tris | Smoothing + density-boost against Poisson noise | NULL: didn't fix |
| R-1d-T3 | Crystallization-specific binding + density tuning | NULL: 6/10 (improved from 2/10) but missed 8/10 threshold; trimodal z-regime identified |

Two independent findings:

1. **T2 (Bénard)**: FFT-of-T-profile metric is too noise-sensitive. Three architectural variants attempted; none reached robust regime. The metric itself may be the wrong falsifier for a point-particle substrate (not a continuous fluid).
2. **T3 (Crystallization)**: R-1d-T3 reached 6/10 — substantial improvement from 2/10. Trimodal z-regime is documented. R-1d-T3 phase-log specifically suggests "R-1d-T3-bis: lift bridge-flux starvation" as the next targeted fix.

## R-1c-quad — Vorticity-Based Bénard Falsifier

Goal: change the Bénard test metric from FFT-of-T-profile to **vorticity field analysis** — a more noise-robust signature of fluid circulation. This is NOT retuning of acceptance thresholds; it is replacing a noise-fragile measurement with the classical mechanical signature of convection cells (curl of velocity field).

Vorticity ω = ∇×v. For a Bénard cell, ω has a characteristic spatial pattern: alternating bands of positive and negative curl along the horizontal axis, period ≈ 2× cube height. The metric:

1. Compute `v_field[x, y, z]` = mean velocity of alive quanta in each voxel, weighted by quanta count.
2. Compute `ω_y = ∂v_z/∂x - ∂v_x/∂z` (rotation about the y-axis — the curl component that captures the circulation we expect).
3. Check that |ω_y| has structure: take the FFT along x (at mid-height z), check the peak is at k≈4 (matching λ≈20 for the standard 80-voxel cube).

This is different from the FFT-of-T-profile because:
- Vorticity directly measures *motion*, not *temperature* — it's not aliased by density Poisson noise.
- The Bénard cell's hallmark in fluid mechanics is exactly the alternating-curl signature, by definition.
- The metric integrates over many quanta within each voxel (averaging suppresses individual-particle noise).

**Pre-registered acceptance for R-1c-quad** (same statistical discipline — 10-seed grid, ≥8/10, neg-control 0/10):

- `tests/flux/test_benard_vorticity.py::test_T2_vorticity_passes_on_at_least_8_of_10_seeds PASSES` — NEW: parametrise across seeds 7, 13, 21, 42, 100, 137, 256, 314, 500, 1000. Each seed: run the F1c setup, compute v-field from alive quanta at the final state, compute ω_y at mid-height, FFT along x, assert peak at k=4 ±20%. ≥8/10 must pass.
- `tests/flux/test_benard_vorticity.py::test_T2_vorticity_negative_control_fails_all_10_seeds PASSES` — NEW: buoyancy_g=0 setup, same metric. ALL 10 seeds must FAIL (peak at k=0 or no clear peak).
- `tests/flux/test_conservation.py PASSES` — T1 unaffected.
- `tests/flux/test_crystallization.py PASSES` — T3 unaffected by metric change.
- `tests/flux/test_decay.py PASSES` — T4 unaffected.
- `tests/flux/test_horizontal_dynamics.py PASSES` — R-1b's horizontal-dynamics tests still pass.

If R-1c-quad passes, the original FFT-of-T-profile test (`test_benard.py`) stays marked slow (it's deprecated as a falsifier, but kept for historical regression).

Time budget: 12 hours.

## R-1d-T3-bis — Lift Bridge-Flux Starvation

Goal: address the R-1d-T3 phase-log diagnosis directly. R-1d-T3's session found a **trimodal z-regime**: floor decays, middle band accumulates, ceiling starves. The mechanism per the phase-log: bridge-flux plasticity (the F1b layer) was siphoning quanta toward middle-band bridges, leaving the ceiling without enough density to satisfy the top/bottom>5× crystallization metric.

The fix candidate from the R-1d-T3 phase-log: **lift bridge-flux starvation**. Concretely the session is expected to either:

1. Reduce bridge-flux drain rate so ceiling density is maintained (parameter level), OR
2. Add a ceiling-replenishment mechanism (architectural level — symmetric to floor injection or top-boundary density floor).

Option 2 is preferred because option 1 is a single-knob calibration twist that R-1d-T3's session already exhausted. Choice and justification documented in `docs/flux/phase-log.md` before measuring.

**Pre-registered acceptance for R-1d-T3-bis** (same statistical discipline):

- `tests/flux/test_crystallization_robustness.py::test_T3_passes_on_at_least_8_of_10_seeds PASSES` — same test from R-1d-T3, must now reach ≥8/10 (was 6/10).
- `tests/flux/test_crystallization_robustness.py::test_T3_negative_control_fails_all_10_seeds PASSES` — same negative control (no binding), must STILL fail 10/10.
- `tests/flux/test_crystallization.py PASSES` — seed=42 original.
- `tests/flux/test_conservation.py PASSES` — T1 unaffected.
- `tests/flux/test_decay.py PASSES` — T4 unaffected.
- Bridge-flux layer remains functional: `tests/flux/test_bridges.py PASSES`, `tests/flux/test_plasticity.py PASSES` (the fix must not break F1b).

Time budget: 12 hours.

## After both

If R-1c-quad passes AND R-1d-T3-bis passes: queue R-1d-iter2 (joint robustness gate re-audit with both new T2 and T3 metrics+fixes). If THAT passes, Phase 1 is genuinely solid and R-3 (F2 implementation) can proceed.

If either NULLs: write a comprehensive Phase-1 postmortem in LOGBOOK.md summarizing all eight robustness attempts (R-1c through R-1d-T3-bis), enumerate the three structural findings (FFT-noise sensitivity, trimodal z-regime, bridge-flux starvation), and propose specific spec amendments the user should consider on return. Set STOP marker. Wait for user judgment.

This iteration is the final autonomous attempt. If both NULL, Bénard- and crystallization-style falsifiers may be unattainable in the current substrate model, and the spec needs amendment, not the implementation.
