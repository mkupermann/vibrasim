# Flux Substrate F1 — Phase-1 Robustness Sprint

> **For autonomous-prototype-build:** This brief covers three items — R-1b, R-1c, R-1d. Each is its own pre-registered slot. Work on the one named in `~/.eqmod/autopilot/current_item.txt`. Do not jump ahead.

**Why this sprint exists:** R-1 (flux F1c) was marked PASSED on 2026-05-14T00:11, but its honest phase-log entry says the T2 Bénard test only fires on a single lucky seed (seed=42, cube=80×40×10, buoyancy_g=2.0, damping_mu=0.5). Across 10 seeds the pass rate is 30%, the FFT signal-to-noise ratio on the T-profile is ~1.5, and the negative control (buoyancy_g=0) fails to trigger 0/10 times — which is good for the control but indicates the trained signal is weak. The phase-log explicitly says the limit is *architectural*, not parametric: the substrate has no horizontal force coupling, so Bénard cells cannot form for fluid-dynamical reasons.

**User instruction (2026-05-14 12:25):** "Sorge dafür dass die Physik und Biologie funktioniert bevor der nächste Schritt angefangen wird." Translation: make sure the physics is robust before the next layer is added. R-2 (F2 plan) and R-3 (F2 implementation) are paused until Phase 1 is solid.

## Acceptance contract (per item)

### R-1b — F1c Architecture Extension: Horizontal Force Term

Goal: extend the flux substrate's physics so Bénard-style convection cells can form **for fluid-dynamical reasons**, not because a specific RNG seed happened to scatter quanta into a horizontally-modulated configuration by chance. The phase-log diagnosis is clear: the substrate currently has only `vel_z += g * (T_local - T_ref) * dt` (vertical buoyancy) and `vel *= (1 - μ * dt)` (isotropic damping). What's missing is a mechanism that produces *horizontal* mass/quanta movement in response to a vertical temperature gradient — i.e., the return flow that closes a Bénard cell.

Candidates that fit the spec's "energy flux + minimal interaction rules" envelope:

1. **Pressure-gradient surrogate** — compute local density (count of quanta per voxel), derive a pressure proxy P = ρ × T, apply a force per quantum proportional to -∇P. Cheap (one numpy gradient call per tick), preserves the "no continuum equations baked in" stance because the field is computed from the same quanta the substrate already tracks.
2. **Return-flow injector at the cold ceiling** — symmetric to the hot-floor injector, but with downward initial velocity. Closes the loop by physical recirculation rather than a continuum force. Has the cost of doubling injection bookkeeping.
3. **Quanta-quanta horizontal repulsion** — a short-range pair force that pushes quanta apart, biased by local T. Closest to the spec's "minimal pair interactions" philosophy but expensive (O(N²) without spatial hashing).

The autopilot session is free to pick any of these (or another, justified) approach. The pick must be documented in `docs/flux/phase-log.md` before implementation begins.

**Pre-registered acceptance for R-1b:**

- `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_responds_to_T_gradient PASSES` — NEW unit test the session creates: set up a voxel grid with a horizontal T gradient (warm left, cold right), inject quanta uniformly, run one tick, assert at least 80% of alive quanta acquired a non-zero horizontal velocity component pointing from warm to cold (or vice versa, depending on sign convention). Threshold pre-registered so a half-built force won't pass.
- `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_zero_when_no_gradient PASSES` — NEW: same setup with uniform T, assert mean horizontal velocity magnitude < 0.01 after the tick. Confirms the force only fires on real gradients.
- `tests/flux/test_conservation.py PASSES` — existing T1 must still hold with the new force active.
- `tests/flux/test_crystallization.py PASSES` — existing T3 unaffected.
- `tests/flux/test_decay.py PASSES` — existing T4 unaffected.
- `tests/flux/test_thermal.py PASSES` — existing thermal unit tests still pass.
- `tests/flux/test_dynamics.py PASSES` — existing dynamics smoke tests still pass.

**Negative control** for R-1b: the horizontal force must NOT fire spuriously. The two `test_horizontal_dynamics.py` tests above include the zero-gradient case as the negative control.

Time budget: 12 hours (3 sessions × 4h cap).

### R-1c — F1c Bénard Multi-Seed Robustness Audit

Goal: confirm the existing T2 Bénard test passes robustly across many seeds with the R-1b extension in place. This is the audit the original F1c never had — Claude's own phase-log flagged the lucky-seed risk and skipped this audit by pre-registration choice.

**Pre-registered acceptance for R-1c:**

- `tests/flux/test_benard_robustness.py::test_T2_passes_on_at_least_8_of_10_seeds PASSES` — NEW: parametrise the existing `test_T2_benard_horizontal_wavelength` across 10 deterministic seeds (e.g. 7, 13, 21, 42, 100, 137, 256, 314, 500, 1000), assert at least 8/10 pass. Below 8 is a NULL verdict, not a tweak-the-threshold opportunity.
- `tests/flux/test_benard_robustness.py::test_T2_FFT_SNR_above_3 PASSES` — NEW: for the 8+ passing seeds, compute the FFT signal-to-noise ratio (peak amplitude vs mean amplitude of non-peak bins) of the horizontal T-profile at mid-height. Assert mean SNR ≥ 3.0 across the passing seeds. The R-1 phase-log measured ~1.5; we want at least 2× that.
- `tests/flux/test_benard_robustness.py::test_T2_negative_control_fails_all_10_seeds PASSES` — NEW: same setup as the main test but with `buoyancy_g=0` (no thermal driver), run 10 seeds, assert ALL 10 fail to satisfy the wavelength check. Confirms the substrate isn't accidentally producing horizontal structure from RNG alone.
- `tests/flux/test_benard.py PASSES` — existing seed=42 test still passes (regression).

Discipline: if the 8/10 pass-rate or 3.0 SNR threshold isn't met, the verdict is NULL with a phase-log entry explaining what was observed. The thresholds in this brief are pre-registered — they don't move after the run.

Time budget: 12 hours.

### R-1d — Phase-1 Joint Robustness

Goal: confirm all four Phase-1 falsifiers (T1, T2, T3, T4) hold *jointly* on the same 10 seeds, not separately. Single-test-pass-rate is necessary but not sufficient — the substrate must be in a state where conservation, Bénard, crystallization, and decay all work *at once*, in the same configuration.

**Pre-registered acceptance for R-1d:**

- `tests/flux/test_phase1_robustness.py::test_all_T_tests_pass_jointly_on_8_of_10_seeds PASSES` — NEW: for each of the same 10 seeds used in R-1c, run T1+T2+T3+T4 in sequence in a single session, assert all four pass on at least 8 of the 10 seeds. (Different seeds may use slightly different cube dimensions per the existing tests; the parameter envelope must be identical across the 10 seeds — no per-seed tweaks.)
- `tests/flux/test_phase1_robustness.py::test_no_T_test_regresses_under_extension PASSES` — NEW: compare each T-test's pass criteria with the R-1b extension active vs without it. Assert no regression: each T-test must pass on at least as many seeds as it did before R-1b.

Discipline: R-1d is the final gate on Phase-1 robustness. If it NULLs, the substrate is not ready for F2. R-2 / R-3 stay blocked. The next launchd slot picks R-2 only when R-1d shows status=passed on main.

Time budget: 8 hours.

## File structure (locked decisions)

R-1b creates:
- `world/flux/<horizontal-force-module>.py` — NEW module containing the picked approach. Name decided by the implementing session; record in phase-log.
- `tests/flux/test_horizontal_dynamics.py` — NEW

R-1b modifies:
- `world/flux/dynamics.py` — wire the new force into the tick (placement decided by session; record in phase-log).
- `world/flux/__init__.py` — re-export.
- `docs/flux/phase-log.md` — R-1b entries.

R-1c creates:
- `tests/flux/test_benard_robustness.py` — NEW

R-1c modifies:
- `docs/flux/phase-log.md` — R-1c entries.

R-1d creates:
- `tests/flux/test_phase1_robustness.py` — NEW

R-1d modifies:
- `docs/flux/phase-log.md` — R-1d entries.

No edits anywhere outside `world/flux/`, `tests/flux/`, `docs/flux/phase-log.md`, `world/flux/__init__.py`, `README.md`.

## Open calibration choices

| Param | Default | Purpose | Notes |
|---|---|---|---|
| `horizontal_force_strength` | TBD by R-1b session | strength of the new horizontal mechanism | Pick a default that passes the test_horizontal_dynamics tests; document the value in phase-log. Same value used in R-1c and R-1d. |
| Seed grid for robustness | `[7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]` | which 10 seeds R-1c and R-1d run on | Locked here — no per-seed tweaks. |
| FFT SNR threshold | `3.0` | acceptance threshold for R-1c | Locked. |
| Joint pass-rate threshold | `8/10` | acceptance threshold for R-1c and R-1d | Locked. |

## Notes for autonomous execution

- **Read the F1c phase-log entries before starting R-1b.** They contain Claude's own diagnostic of why T2 was lucky-seed. The new force must address that gap, not paper over it with a different lucky configuration.
- **No "I'll just retune buoyancy_g" temptation.** Phase-log already says architectural, not parametric. If R-1b's only change is parameter values, the verdict is NULL.
- **Negative controls are mandatory** per CHARTER §"Negative controls are required". The test_horizontal_dynamics zero-gradient test and the test_benard_robustness buoyancy_g=0 test are the negative controls for R-1b and R-1c respectively. R-1d's negative control is the no-extension baseline (the second R-1d test).
- **NULL is a valid verdict.** If the substrate fundamentally can't sustain Bénard cells (e.g., 4/10 seeds at best), a NULL with a clean phase-log post-mortem is the right outcome. Michael will read it on return and decide whether the flux hypothesis needs a deeper revision.
- **Branch convention:** the session is on `autopilot/<item-id>` (e.g. `autopilot/R-1b`). Postflight pushes to that branch and per-item-syncs main. Do not push main directly.
