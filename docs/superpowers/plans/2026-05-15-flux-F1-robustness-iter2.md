# Flux Substrate F1 — Robustness Sprint, Iteration 2

> **Added 2026-05-15 16:00** by Claude under user mandate "selbständig entscheiden bis zum Erfolg, auch wenn alles neu erdenken". Iteration 1 ended with three NULLs (R-1c, R-1c-bis, R-1d) and a new finding (T3 also 2/10 lucky). This brief covers the next two pre-registered items.

## What iteration 1 found

| Test | with R-1b pressure-grad | without R-1b |
|---|---|---|
| T1 conservation | 10/10 | 10/10 |
| **T2 Bénard wavelength** | **0/10** | **1/10** |
| **T3 crystallization** | **2/10** | **2/10** |
| T4 decay | 10/10 | 10/10 |

Two independent fragility classes:

1. **T2 (Bénard convection)** — both attempted architectural fixes (pressure-gradient force, return-flow injector) NULLed. Phase-log diagnosis: the FFT-of-T-profile metric is dominated by short-range Poisson density noise; the smooth thermal gradient that should drive Bénard is drowned out.

2. **T3 (Crystallization)** — also 2/10 lucky-seed, but the mechanism is different (T3 is about atom formation, not convection). This was never robustness-audited before; the original F1c plan assumed T3 was solid.

The two are addressed separately because they're independent physics.

## R-1c-tris — Anti-Noise Pressure Field

Goal: address the Poisson-noise diagnosis directly. Two cheap, independent levers:

1. **Smooth T-field and density before computing gradient.** Use a Gaussian kernel (scipy.ndimage.gaussian_filter with sigma ≈ 2 voxels). High-spatial-frequency Poisson noise is suppressed; the smooth thermal gradient is preserved. This is a standard signal-processing fix.

2. **Increase quanta density per voxel.** Current `n_inject=20` per tick gives ~6M quanta over 10000 ticks but mostly transient. Boost to 50 or 100. More particles per voxel → density estimate's Poisson noise drops as 1/sqrt(N).

The session may keep, modify, or remove R-1b's pressure-gradient code; if it judges the return-flow injector approach (untried in code) is worth adding alongside, that's also in scope.

**Pre-registered acceptance for R-1c-tris** (identical thresholds — no retuning):

- `tests/flux/test_benard_robustness.py::test_T2_passes_on_at_least_8_of_10_seeds PASSES` — same 10-seed grid as R-1c.
- `tests/flux/test_benard_robustness.py::test_T2_FFT_SNR_above_3 PASSES` — mean SNR ≥3.0 across passing seeds.
- `tests/flux/test_benard_robustness.py::test_T2_negative_control_fails_all_10_seeds PASSES` — buoyancy_g=0 must FAIL on ALL 10 seeds.
- `tests/flux/test_benard.py PASSES` — original seed=42 test passes; `@pytest.mark.slow` marker removed.
- `tests/flux/test_horizontal_dynamics.py PASSES` — R-1b's tests (or their successors) still pass.
- `tests/flux/test_conservation.py PASSES` — T1 holds.
- `tests/flux/test_crystallization.py PASSES` — T3 unaffected by this item's changes (T3's own fix is R-1d-T3).
- `tests/flux/test_decay.py PASSES` — T4 unaffected.

If R-1c-tris NULLs: I (the supervising agent) will add R-1c-quad next, which switches the metric itself from FFT-peak to vorticity-based (a more noise-robust convection-cell detector). If R-1c-quad NULLs: R-1c-pentus will reframe Phase-1 acceptance to focus on phenomena the substrate demonstrably can do (T1, T4 work; we identify what about T2/T3 makes the substrate currently unable to meet them, then choose targets that match the substrate's actual capabilities). Each iteration is pre-registered separately when previous NULLs.

Time budget: 12 hours.

## R-1d-T3 — Crystallization Robustness

Goal: investigate why T3 (`test_crystallization.py`) passes only 2/10 on the same seed grid as T2. T3 is about atom formation — quanta with matching frequency that should bind into stable structures. It's spec §7 T3, distinct from convection.

The R-1d phase-log carries the audit numbers but does not include a mechanism analysis for T3 (R-1d's scope was T1+T2+T3+T4 joint passage, not individual diagnosis). R-1d-T3's first task is the diagnosis.

**Pre-registered acceptance for R-1d-T3:**

- `tests/flux/test_crystallization_robustness.py::test_T3_passes_on_at_least_8_of_10_seeds PASSES` — NEW: parametrise `test_crystallization.py` across the same 10 seeds (7, 13, 21, 42, 100, 137, 256, 314, 500, 1000), assert ≥8/10 pass.
- `tests/flux/test_crystallization_robustness.py::test_T3_negative_control_fails_all_10_seeds PASSES` — NEW: same setup but with binding disabled (or matched-wallclock no-binding control), assert ALL 10 seeds FAIL.
- `tests/flux/test_crystallization.py PASSES` — existing seed=42 test still passes.
- `tests/flux/test_conservation.py PASSES` — T1 unaffected.
- `tests/flux/test_decay.py PASSES` — T4 unaffected.
- `docs/flux/phase-log.md` contains an R-1d-T3 entry with: (a) the per-seed failure mode for T3 (e.g., "no atoms formed", "atoms formed but dissolved", "wrong frequency match rate"), (b) the mechanism diagnosis paragraph, (c) the architectural fix chosen.

The session has discretion on the fix mechanism. Candidates if the diagnosis points there: relax frequency-match tolerance, increase binding rate constant, increase quanta-pair encounter rate via density boost, add a "nucleation seed" boundary condition. The fix must be justifiable as a physics-level mechanism, not a test-side parameter twist.

Time budget: 12 hours.

## Notes

- These two items are independent — R-1c-tris (Bénard) and R-1d-T3 (Crystallization) work different physics. Either can pass while the other NULLs.
- The joint gate R-1d must be re-run after BOTH T2 and T3 are robust. R-1d's previous NULL stands as a record of the iteration-1 finding; re-running it is a new attempt.
- F2 work (R-3) stays blocked until Phase 1 is solid.
