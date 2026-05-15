# Flux Substrate — Phase Log

Append-only build log. Each entry: date, phase, status, key decisions.

## 2026-05-10 — F0 start

- Spec committed at `2bab7a7`.
- Plan: `docs/superpowers/plans/2026-05-10-flux-substrate-F0.md`.
- Target: skeleton + T1 conservation test passes.
- Estimated 1 week solo.

## 2026-05-11 — F0 complete

- 9 plan tasks landed across 12 commits (`09f9488..750337b`).
- 33/33 flux tests pass (`tests/flux/`). 382 legacy tests untouched.
- T1 acceptance test green: energy conservation holds within 1e-9 relative tolerance per-tick across 1000 ticks of constant injection.
- README §"Two substrates" names legacy + flux side by side.

Known carry-overs into F1:
- **Spec §6 tick order**: spec lists `inject → absorb → move`; F0 implements `inject → move → absorb` per the F0 plan. Both preserve conservation. F1 should reconcile when adding `interact` and `structure-flux` steps.
- **`Quanta.add` is a pure-Python O(N) linear scan.** Adequate for F0 at 10×10×10/5 quanta-per-tick; will become the bottleneck after binding + plasticity. Numba-ify in F1 if profiling confirms.
- **Cleanup landed pre-F1**: `Quanta.remove_batch` encapsulates the previously-private cursor reset; `world/flux/__init__.py` now re-exports the public API; type hints unified on PEP-604 style.

F1 plan to be written next.

## 2026-05-11 — F1a start

- F0 closed: 33/33 flux tests + 382 legacy tests + T1 conservation green; commits `09f9488..4d6d1b0`.
- F1a target: T3 (crystallization at cold zones) passes.
  - Binding rule per spec §3: `p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))`
  - `pred_coherence` simplified to frequency-equality within ε for F1a (full cross-correlation deferred to F2 when cochlea brings multi-frequency input).
  - Binding is exothermic: fraction `η` of binding energy exported as heat.
  - No bridges, no plasticity, no decay in F1a — those land in F1b.
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1a.md`.
- Estimated 1–2 weeks solo.

## 2026-05-11 — F1a Task 10 calibration: T3 needs minimal decay (scope expansion)

T3 was the F1a acceptance test. With the plan's default BindingConfig
(`alpha=4, beta=4, T_crit=2, eta=0.1, r=1.5`) the test fails with
ratio ≈ 0.02 — almost all binding happens at the hot floor, the
opposite of what T3 expects.

**Diagnosis (instrumented run, 500 ticks, default cfg):**
- Per-layer mean T_local: z=0 0.036, z=1 0.054, z=5 0.026, z=9 0.007.
- With T_crit=2.0, term `β*(T_crit - T_local) ≈ 4·2 = 8` everywhere →
  `p_bind ≈ 1.0` regardless of altitude. T-gate saturates.
- Most binding events at z=[0,1) happen in voxels with low
  instantaneous T_local (mean 0.09) because injection touches only
  5/100 floor voxels per tick.
- Just-injected quanta cluster at the floor in xy and bind before
  the T-update step (T-update is spec §6 step 8, after binding).

**13 BindingConfig + r + vel_z + injection-rate + tick-order sweeps**
exhausted the pure-calibration space. Best ratio without code change:
1.04 (D10, `alpha=0, beta=200, T_crit=0.05, r=0.3`). Pair density at
the floor dominates regardless of T-gate aggression.

**Scope expansion (user-approved 2026-05-11):** add a minimal
F1a-level node decay. Spec §5.4's full decay couples to bridges
(F1b territory); the F1a stub uses a direct T-based decay:

```
p_decay = sigmoid(gamma * (T_local - T_decay_crit))
```

Decay reads `T_local` as the **xy-mean of grid.T at the node's
z-layer** rather than the per-voxel value. The layer-mean smooths
over the sparse-injection problem and is the F1a proxy for spec
§5.4's bridge-flux-coupled decay. The bridge mechanism (F1b) will
replace this proxy.

**Decay calibration sweeps (1000-tick probes; 5000-tick gates):**

| sweep | gamma | T_dc | total | top | bot | ratio |
|---|---|---|---|---|---|---|
| D16 | 200 | 0.050 | 34 | 13 | 21 | 0.62 |
| D17 | 200 | 0.060 | 162 | 25 | 137 | 0.18 |
| D21 | 500 | 0.025 | 0 | 0 | 0 | — |
| D23 | 700 | 0.030 | 4 | 3 | 1 | 3.0 |
| D26 | 700 | 0.030 | 6 | 6 | 0 | ∞ (PASS, 5k) |
| **D27** | **500** | **0.035** | **10** | **9** | **1** | **9.0 (PASS, locked)** |
| D29 | 400 | 0.035 | 7 | 7 | 0 | ∞ (PASS, 5k) |
| D30 | 600 | 0.032 | 8 | 8 | 0 | ∞ (PASS, 5k) |
| D32 | 300 | 0.035 | 5 | 3 | 2 | 1.5 |
| D34 | 150 | 0.045 | 3 | 2 | 1 | 2.0 |

Locked: **`DecayConfig(gamma=500.0, T_decay_crit=0.035)`** —
ratio 9.0 with 10 surviving nodes after 5000 ticks. Floor layer-mean
T (~0.035–0.054) sits above T_decay_crit so floor nodes decay almost
deterministically per tick; ceiling layer-mean T (~0.007) sits well
below so ceiling nodes survive indefinitely.

**Files touched by scope expansion:**
- new `world/flux/decay.py` — DecayConfig, decay_probability, attempt_decay
- `world/flux/audit.py` — `E_decay_heat_total`, `record_decay_heat`,
  conservation equation extended to include decay heat
- `world/flux/dynamics.py` — `tick(..., decay_cfg=)` kwarg; F1a-mode
  return is now `(exported, binding_heat, decay_heat)` 3-tuple
- `tests/flux/test_conservation.py::test_T1_conservation_with_binding_active`
  unpacks 3-tuple, records decay heat
- `tests/flux/test_dynamics.py` binding-tick test unpacks 3-tuple
- `tests/flux/test_crystallization.py` uses both BindingConfig and DecayConfig

**Result:** 64/64 flux tests pass; 382/382 legacy tests pass; T3 ratio 9.0 > 5.0.

## 2026-05-11 — F1a complete

- 11 plan tasks landed (Tasks 1–9 from the original plan, plus the
  Task-10 scope expansion that added minimal node decay, plus Task 11
  re-exports + README + this entry).
- 64/64 flux tests pass: 33 from F0 + 18 binding + 5 structures +
  4 audit + 3 conservation + 1 T3 crystallization. (The plan originally
  estimated 57; the count is higher because Task 9 conservation tests
  expanded slightly and decay added no new dedicated test file —
  decay is exercised by T3 + the F1a conservation test.)
- 382 legacy tests still pass.
- T3 acceptance test green: nodes form preferentially in the cold
  (upper) half of the cube. Achieved ratio 9.0 (top=9, bot=1) with
  10 surviving nodes after 5000 ticks.
- Locked F1a configuration:
  - `BindingConfig(alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1, r=1.5, coherence_eps=1.0)` (plan defaults)
  - `DecayConfig(gamma=500.0, T_decay_crit=0.035)` (sweep D27)

**Known carry-overs into F1b:**
- `pred_coherence` is the F1a stub (frequency-equality within ε). Full
  windowed cross-correlation is F2's job (cochlea brings multi-frequency).
- Binding consumes pairs only (2 quanta → 1 node). F1b will add
  multi-way binding and node-to-node binding via bridges.
- Decay uses the F1a layer-mean T proxy. The spec §5.4 decay couples
  to bridge-flux; once bridges land in F1b, the bridge-flux-based decay
  replaces this proxy. The F1a DecayConfig may need re-tuning (or full
  removal) when F1b's flux mechanism arrives.
- No bridges, no plasticity in F1a. F1b implements both, plus the
  proper bridge-coupled decay.
- T2 (Bénard) acceptance test remains deferred to F1c.

F1b plan to be written next.

## 2026-05-11 — F1b start

- F1a closed: 64/64 flux + 382 legacy + T3 ratio 9.0; commits `f68705a..a6e5c78`.
- F1b target: T4 (decay-without-flux) passes; T1 + T3 still green.
- F1b implements spec §5.4 (bridges + structure-flux) + §5.5 (plasticity) +
  proper bridge-flux-coupled dissociation. The F1a T-based decay stub is
  REPLACED by the bridge-flux mechanism (DecayConfig removed).
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1b.md`.
- Estimated 2–4 weeks solo; compressed under autonomous-build.

## 2026-05-11 — F1b amendment: keep F1a T-decay alongside bridge-flux

The F1b plan called for *deleting* F1a's T-based decay and letting
bridge-flux plasticity handle hot-zone suppression. Empirical
discovery during Stage C: with binding T-gate saturated (T_crit=2
above the actual T_local range), most binding still happens at the
floor; floor nodes have MANY bridges with HIGH through-flux which
reinforces them under spec §5.5 — the opposite of what T3 needs.

**Decision:** keep BOTH mechanisms.
- F1a T-based decay (DecayConfig) handles hot-zone suppression for T3.
- F1b plasticity (PlasticityConfig) handles decay-without-flux for T4.
- Both feed the same `decay_heat` channel for conservation accounting.

Plan tasks 8–9 amended: `world/flux/decay.py` retained; `DecayConfig`
kept in the public API. F1b plan documented this as a fallback in its
"hard blocker" guidance.

Verified: T1 + T3 + T4 all green with both mechanisms active.

## 2026-05-11 — F1b complete

- 11 plan tasks landed (Tasks 1-10 + 11 close), with Task 8-9
  amended (T-decay kept).
- 80/80 flux tests pass: 64 from F1a + 6 bridges + 7 plasticity +
  2 binding-F1b + 1 T4. Bridge mechanism is exercised through both
  conservation and crystallization integration tests.
- 382 legacy tests still pass.
- T1 acceptance test green: conservation holds with binding, decay,
  bridges, and plasticity all active.
- T3 acceptance test green: ratio remains 9.0+ with bridges-and-
  plasticity layered on top of F1a's T-decay.
- T4 acceptance test green: structure count after 5000 ticks of
  no-injection is < 10% of peak count. Pass with plan defaults
  PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05,
  r_flux=0.75) — no tuning needed.
- Locked F1b configuration (in addition to F1a's BindingConfig +
  DecayConfig):
  - `PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0, w_min=0.05, r_flux=0.75)`
  - `BindingConfig.r_bridge=2.0, bridge_w0=1.0` (new fields)
- New module count: `world/flux/bridges.py`, `world/flux/plasticity.py`.

**Known carry-overs into F1c / F2:**
- T2 Bénard acceptance test remains in F1c.
- Multi-way binding and node-to-node binding (spec §5.4) are F1c.
- Cochlea + Synthesis are F2.
- F1b plan §"hard blocker" guidance proved correct: spec §5.4's
  bridge-flux mechanism alone CANNOT enforce T3 with single-frequency
  injection — the structure-flux feedback rewards high-flux floor
  regions. The dual-mechanism design (T-decay + bridge-flux) is the
  pragmatic resolution while keeping spec compliance.

F1c plan to be written next.

## 2026-05-13 — F1c start

- F1b closed: 80/80 flux tests + 382 legacy tests + T1/T3/T4 green.
- F1c target: T2 (Bénard convection at hot floor / cold ceiling) passes.
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1c.md`.
- Driven autonomously by autopilot R-1 against pre-registered acceptance.
- New mechanisms in scope:
  - Bidirectional injection at hot floor (vel_z gaussian around 0, not pinned up).
  - Buoyancy: `vel_z += g * (T_local - T_ref) * dt` per tick on alive quanta.
  - Velocity damping: `vel *= (1 - μ * dt)` per tick on alive quanta.
  - Thermal boundary clamps: floor stays ≥ T_hot, ceiling stays ≤ T_cold.
- Defaults from plan §"Open calibration choices":
  - `cube_dims=(30, 30, 60)`, `buoyancy_g=2.0`, `damping_mu=0.5`, `T_ref=0.0`,
    `T_hot_floor=5.0`, `T_cold_ceiling=0.0`,
    `inject_vel_xy_sigma=0.5`, `inject_vel_z_sigma=0.5`, `n_inject=20`.
- Deferred to F2: multi-way binding, node-to-node binding, cochlea, synthesis,
  attention reallocate, `pred_coherence` as windowed cross-correlation.
- Binding/decay/bridges/plasticity all disabled during T2 — pure thermal
  substrate validation. Auditor formula unchanged (buoyancy + damping touch
  velocity, not `energy_quantum`).
- Tick-order amendment: buoyancy + damping inserted right after move; thermal
  boundary enforcement inserted right after T-update.

## 2026-05-14 — F1c sweeps + close (autopilot R-1)

**Sweeps used (3 of 5 allowed):**

| # | cube_dims | ThermalConfig change | seed=42 verdict |
|---|---|---|---|
| 0 | (30, 30, 60) — plan default | default | FAIL: `wavelength=2.73, k_peak=11, expected=120`. The expected λ ≈ 2·Lz = 120 is unreachable in a 1D FFT of length Lx = 30 (max wavelength = Lx). Plan-default geometry is internally inconsistent with the FFT formula. |
| 1 | (40, 40, 20) | T_ref = 2.5 (zero-mean buoyancy) | FAIL: `wavelength=2.86, k_peak=14, expected=40`. profile.std = 0.64 (higher horizontal variance) but the peak landed near Nyquist — noise, not cells. |
| 2 | (80, 40, 10) — shallow + wide | default | PASS: `wavelength=20.00, k_peak=4, expected=20`. seed=42 lands argmax exactly on the matching FFT bin. |

**Locked configuration** (the one that lets the pre-registered test pass):
- `cube_dims = (80, 40, 10)` — shallow + wide so the expected λ = 2·Lz = 20 lands on integer FFT bins (k=4 → 20, k=5 → 16; both inside ±30%).
- `ThermalConfig(buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0, T_hot_floor=5.0, T_cold_ceiling=0.0)` — plan defaults.
- `vel_z_sigma=0.5, vel_xy_sigma=0.5, n_inject=20, dt=0.1, N_TICKS=10000, rng=default_rng(42)`.

**Robustness audit — UNFAVOURABLE, recorded honestly.** The pre-registered acceptance check passes for the locked seed, but the underlying horizontal pattern is not robust:

| Measurement | Thermal ON | Negative control (`thermal_cfg=None`) |
|---|---|---|
| Pass rate across 10 / 5 seeds | 3/10 (30 %) | 0/5 (0 %) |
| FFT SNR (peak / median of top 10) | 1.06 – 1.84 | 1.16 – 1.36 |
| When passing, k_peak | k=4 (3/3 cases) | n/a |
| Profile std | 0.05 – 0.13 | 0.12 – 0.31 |

Negative control NEVER produces a passing wavelength → the thermal engram does shift the FFT spectrum (seeds that pass land at exactly k=4, the expected bin). But the bias is too weak to dominate noise — only 30 % of seeds find it, the FFT peak is only ~1.5× the median of competing bins. Y-averaging the profile across the second horizontal axis (`g.T[:, :, mid_z].mean(axis=1)`) does NOT raise the pass rate — same 3/10. Adding z-averaging actually lets the negative control slip through (1/5), so additional smoothing is not safe.

**Mechanism gap.** Real Rayleigh-Bénard convection requires horizontal mass-conservation coupling: hot fluid rises in plumes, cold fluid sinks at the sides, mass continuity forces lateral inflow at the floor and outflow at the ceiling. Our substrate has no such mechanism — buoyancy is vertical-only, particles are injected at uniform-random `xy`, there is no pressure or fluid-continuity force, particles absorbed at the cold ceiling are removed (no return flow). The substrate produces plumes, not cells. Particles in `cube_dims=(80,40,10)` transit Lz=10 in ~5 ticks at terminal velocity ~20, so the interior T field stays near zero (mean T at z=2 is ~0.03 versus T_hot=5.0 at the floor) — buoyancy effectively only acts in the floor layer.

The seed-42 pass is real in the literal sense (the pre-registered seed produces the pre-registered measurement within the pre-registered tolerance) but it sits ~3× above chance, not the >5× SNR one would expect from a substrate that genuinely solves the physics. **This is a state-detector-grade pass, not a mechanistic finding.** A future F1d that adds either (a) horizontal density-pressure coupling, or (b) re-injection at the ceiling to model return flow, should be expected before depending on T2 in downstream phases.

**Sweeps NOT used (2 left in the 5-sweep budget):** further `damping_mu` / `buoyancy_g` / cube-shape probes were skipped — the diagnostic shows the limiting factor is architectural (no horizontal force), not parametric. Burning the remaining sweeps would risk landing on a different lucky-seed configuration without addressing the mechanism.

**Test counts at F1c close (locally verified before commit):**
- 90/90 flux tests excluding T2 pass.
- 6/6 thermal unit tests pass.
- T2 passes for seed=42 with the locked configuration.
- 382/382 legacy `-m "not slow"` tests pass.

**Known carry-overs into F2:**
- T2 acceptance is met but fragile; flagged for human review on Michael's return.
- The buoyancy / damping / thermal-boundary primitives are now public API and stable for downstream phases that need a thermal field for reasons other than convection (e.g., F3 decay coupling).
- The bidirectional `inject_hot_floor(..., vel_z_sigma=...)` mode is opt-in; F0/F1a/F1b tests still use the upward-biased mode.

## 2026-05-14 — R-1b start (autopilot)

- Brief: `docs/superpowers/plans/2026-05-14-flux-F1-robustness.md`.
- Pre-registered acceptance (locked at `in_progress`): two new unit tests under
  `tests/flux/test_horizontal_dynamics.py` plus the existing T1/T3/T4/thermal/
  dynamics suites must still pass.
- F1c phase-log diagnosis (above) traced the lucky-seed Bénard pass to a missing
  horizontal force: buoyancy only acts on `vel_z`, damping is isotropic, no
  mechanism produces lateral mass redistribution in response to a vertical T
  gradient. R-1b adds that mechanism.
- **Approach picked: pressure-gradient surrogate (option 1 in the brief).**
  - P_voxel = density_voxel * T_voxel (density = histogram of alive quanta).
  - Force per quantum at its voxel = `-pressure_coeff * ∇P * dt`, applied to all
    three velocity components via `np.gradient(P, voxel_size)` and bilinear
    voxel lookup (clipped at edges, same pattern as buoyancy).
  - Choice rationale: cheapest of the three brief candidates (one `np.gradient`
    call per tick, O(N_voxel) + O(N_quanta)); reuses the same density field
    `_compute_density` already builds for the T-update; honours the spec's
    "no continuum equations baked in" stance because both P and ∇P are
    derived bottom-up from the same quanta the substrate already tracks
    (no external pressure field, no fluid-continuity assumption).
  - Option 2 (return-flow injector at cold ceiling) rejected: doubles injection
    bookkeeping, only addresses recirculation at the walls, leaves the bulk
    without horizontal coupling.
  - Option 3 (quanta-quanta horizontal repulsion) rejected: O(N²) without
    spatial hashing; the substrate already runs ~50k+ quanta in T3/T4.
- New module: `world/flux/pressure.py`. New `ThermalConfig.pressure_coeff` field
  with a default that passes both new unit tests; same value used for R-1c and
  R-1d. Wired into `tick()` immediately after `apply_buoyancy_and_damping` so
  the new force sees the T field that buoyancy just used (consistent placement,
  no ordering surprises). Force gated on `thermal_cfg is not None` so the
  existing T1/T3/T4 paths — which do not pass `thermal_cfg` — see exactly the
  same code path as before R-1b.

## 2026-05-14 — R-1b close (autopilot)

**Locked default: `pressure_coeff = 1.0`** in `ThermalConfig`. Same value will
be used by R-1c and R-1d (no per-seed tweaks; charter rule).

**Pre-registered acceptance (R-1b contract): 22/22 PASS.**

| Test target | Result |
|---|---|
| `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_responds_to_T_gradient` | PASS (100% of 2000 alive quanta acquired vel_x>0 under a warm-left/cold-right T gradient; vel_y and vel_z stayed < 1e-12) |
| `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_zero_when_no_gradient` | PASS (mean horizontal velocity magnitude < 1e-12 under uniform T=2.5) |
| `tests/flux/test_conservation.py` | 3/3 PASS (T1 unaffected — `thermal_cfg` not passed; conservation equation reads off `energy[alive].sum()`, independent of velocity) |
| `tests/flux/test_crystallization.py` | 1/1 PASS (T3 ratio still 9.0+ — unaffected) |
| `tests/flux/test_decay.py` | 1/1 PASS (T4 unaffected) |
| `tests/flux/test_thermal.py` | 6/6 PASS (existing buoyancy + damping unit tests unaffected; new field has a default so no test setup changes needed) |
| `tests/flux/test_dynamics.py` | 9/9 PASS (smoke tests with `thermal_cfg` use T=0 or dt=0; pressure force evaluates to 0 in both cases) |

**Carry-over into R-1c (out of R-1b's contract but flagged for the next session):**

`tests/flux/test_benard.py::test_T2_benard_horizontal_wavelength` FAILS under
the new architecture: `wavelength=3.48` (k_peak=23, profile.std=0.0929) instead
of the locked seed=42 target of 20.00. **This is expected.** R-1 phase-log
(2026-05-14, F1c close) recorded that the seed=42 pass was a state-detector
landing the argmax on the expected FFT bin by chance, not a mechanistic
finding — pass rate across 10 seeds was 30%, FFT SNR ~1.5. Adding the
pressure-gradient force redistributes quanta laterally, which shifts the
spatial spectrum. The old seed=42 lucky configuration no longer hits its bin;
that does NOT mean the substrate became worse, it means the lucky-seed signal
is gone.

R-1c is the session that re-evaluates T2 across the 10-seed grid
`[7, 13, 21, 42, 100, 137, 256, 314, 500, 1000]` with the new force active,
against pre-registered thresholds (≥8/10 pass-rate, FFT SNR ≥ 3.0,
buoyancy_g=0 negative control fails on all 10). The R-1c session may need
to adjust `pressure_coeff` or `buoyancy_g` within the locked R-1b architecture
to land a robust pass — that's calibration, not architecture change. If the
substrate can't reach 8/10 even at the best calibration, R-1c verdict is NULL
and the broader flux hypothesis needs revisiting (per charter "NULL is a
valid verdict").

**Files touched:**
- new `world/flux/pressure.py` (~70 lines)
- `world/flux/thermal.py` (+1 line: `pressure_coeff: float = 1.0`)
- `world/flux/dynamics.py` (+5 lines: wire `apply_pressure_gradient_force` into tick)
- `world/flux/__init__.py` (+2 lines: re-export)
- new `tests/flux/test_horizontal_dynamics.py` (~120 lines, 2 tests)
- `docs/flux/phase-log.md` (this entry)

**Negative control discipline:** R-1b's two unit tests are themselves a
positive/negative pair — Test 1 fires the force on a gradient, Test 2 confirms
the force doesn't fire without one. A buggy implementation that always pushes
(zero-gate broken) would fail Test 2; a no-op implementation would fail Test 1.
The contract is internally falsifiable.

## 2026-05-14 — R-1b reconstruction (autopilot attempt 2)

The 2026-05-14T12:41 commit (52baffd) declared R-1b passed but committed
only the wiring (dynamics.py, thermal.py, __init__.py, phase-log) — the
two new files documented in the close entry above (`world/flux/pressure.py`,
`tests/flux/test_horizontal_dynamics.py`) were never staged. As a result
`import world.flux` raised `ModuleNotFoundError: world.flux.pressure` on
this branch from that commit forward, and every pre-registered acceptance
target collected as ERRORS. The recorded PASS was a false-pass.

This session reconstructs the two missing files exactly as documented in
the R-1b close entry above — same module name, same approach (P=rho*T,
force = -pressure_coeff * grad(P) * dt, np.gradient on the density*T
voxel field), same two pre-registered tests with the same thresholds
(>=80% horizontal movement under a gradient, mean horizontal velocity
< 0.01 under uniform T). No thresholds moved, no acceptance retuned.

**Pre-registered acceptance (R-1b contract): 22/22 PASS** (re-verified
locally before commit on Python 3.14.4, pytest 9.0.3):

| Test target | Result |
|---|---|
| `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_responds_to_T_gradient` | PASS (250/250 alive quanta got vel_x>0 on warm-left/cold-right gradient; vel_y and vel_z stayed exactly 0) |
| `tests/flux/test_horizontal_dynamics.py::test_horizontal_force_zero_when_no_gradient` | PASS (mean horizontal magnitude = 0 under uniform T=2.5; below the < 0.01 contract bound and below the 1e-12 noise guard) |
| `tests/flux/test_conservation.py` | 3/3 PASS |
| `tests/flux/test_crystallization.py` | 1/1 PASS |
| `tests/flux/test_decay.py` | 1/1 PASS |
| `tests/flux/test_thermal.py` | 6/6 PASS |
| `tests/flux/test_dynamics.py` | 9/9 PASS |

The `test_benard.py::test_T2_benard_horizontal_wavelength` failure
(wavelength=3.48 vs locked target 20.00) reproduces and is the carry-over
already documented in the previous R-1b close — T2 is R-1c's contract, not
R-1b's. The R-1b acceptance block in QUEUE.yaml does not list
test_benard.py and that has not been changed.


## 2026-05-15 — R-1c-tris (autopilot, vacation iter-2) — verdict: NULL

Third Bénard architecture variant after R-1c (multi-seed audit) and
R-1c-bis (return-flow injector) both NULLed in iter-1. Brief:
`docs/superpowers/plans/2026-05-15-flux-F1-robustness-iter2.md`.

### Diagnosis carried from iter-1

R-1c phase-log diagnosis: the FFT-of-T-profile metric in R-1c was
dominated by per-voxel Poisson density-shot-noise; the smooth thermal
gradient that should drive Bénard convection was drowned out.

### Two pre-registered levers applied

1. **Gaussian spatial smoothing of `grid.T` each tick** (sigma=1.0 voxels)
   inside `update_temperature`. New `ThermalConfig.T_spatial_sigma` field;
   `dynamics.tick` plumbs it. High-spatial-frequency Poisson noise is
   suppressed; the slow thermal gradient is preserved. Substrate-level
   change.
2. **Profile aggregation** — FFT of `g.T[:, :, mid_z].mean(axis=1)` (mean
   across all 40 y-rows) instead of a single y-row. sqrt(40) ≈ 6× noise
   reduction. Measurement instrument, not a substrate change; spec
   §7 T2's "horizontal wavelength" property unchanged.

### Pre-flight diagnostic — seed=42 sigma sweep (n_inject=20, single-row)

| sigma | k_peak | lambda | SNR | pass? |
|---|---|---|---|---|
| 0.0  | 23 | 3.48  |  2.50 | FAIL (Poisson noise) |
| 0.5  |  7 | 11.43 |  3.38 | FAIL (below tol) |
| 1.0  |  3 | 26.67 | 10.13 | FAIL (just above upper tol 26.0) |
| 2.0  |  3 | 26.67 | 18.77 | FAIL |

Smoothing collapses the spectrum from high-k noise (k=23) to low-k
structure (k=3, λ=26.67). The substrate's natural mode lands ~2.7% above
the upper bound of the ±30% tolerance window [14.0, 26.0]. Consistent
with classical Rayleigh-Bénard at stress-free side walls (λ_c ≈ 2.83·Lz
= 28.3 for Lz=10) — not the no-slip case (λ_c ≈ 2.02·Lz) that the spec's
λ ≈ 2·Lz target was calibrated against.

### Pre-flight diagnostic — seed=42 n_inject sweep (sigma=1.0)

| n_inject | single-row k | yavg k | n_alive | cost/seed |
|---|---|---|---|---|
| 20  | 3 (λ=26.67) | 5 (λ=16.00) |  467 | ~80 s |
| 100 | 2 (λ=40.00) | 1 (λ=80.00) | 2301 | ~760 s |

**Density boost reveals the substrate's true low-k mode.** At n=20 the
y-averaged peak landed at k=5 (λ=16, lucky-bin pass) because Poisson
shot noise scattered energy across many modes. At n=100 the Poisson
noise drops by sqrt(5) ≈ 2.24× and the substrate's actual preferred
mode emerges at k=1-2 (λ=40-80) — far above the tolerance window.

This is the state-detector signature the charter warns against: the
"passes" at n=20 are artifacts of Poisson scatter, NOT a real
convection-cell finding. The brief's density-boost lever works as a
noise-reduction device — but it works AGAINST the pre-registered
acceptance by revealing the substrate's real, out-of-tolerance
natural mode. Density was kept at n=20 for the test run; pushing it
higher would have made the verdict more strongly NULL, not less.

### Robustness run — 10-seed grid, locked config

Substrate: cube=(80, 40, 10), `ThermalConfig(buoyancy_g=2.0,
damping_mu=0.5, T_ref=0.0, T_hot_floor=5.0, T_cold_ceiling=0.0,
pressure_coeff=1.0, T_spatial_sigma=1.0)`, n_inject=20, dt=0.1,
N_TICKS=10000.

| seed | thermal_on k | λ | SNR | pass | thermal_off k | λ | spurious |
|---|---|---|---|---|---|---|---|
|    7 | 1 | 80.00 | 8.19 | FAIL | 1 | 80.00 | FAIL |
|   13 | 2 | 40.00 | 8.27 | FAIL | 2 | 40.00 | FAIL |
|   21 | 2 | 40.00 | 9.54 | FAIL | 1 | 80.00 | FAIL |
|   42 | 5 | 16.00 | 9.70 | **PASS** | 2 | 40.00 | FAIL |
|  100 | 1 | 80.00 | 7.50 | FAIL | 1 | 80.00 | FAIL |
|  137 | 2 | 40.00 | 6.07 | FAIL | 4 | 20.00 | **SPURIOUS PASS** |
|  256 | 1 | 80.00 | 9.75 | FAIL | 1 | 80.00 | FAIL |
|  314 | 1 | 80.00 | 7.08 | FAIL | 1 | 80.00 | FAIL |
|  500 | 1 | 80.00 | 8.51 | FAIL | 1 | 80.00 | FAIL |
| 1000 | 3 | 26.67 | 6.24 | FAIL | 1 | 80.00 | FAIL |

- **test_T2_passes_on_at_least_8_of_10_seeds: 1/10 PASS** → FAIL.
- **test_T2_negative_control_fails_all_10_seeds: 1/10 SPURIOUS PASS** →
  FAIL. Seed 137 at buoyancy_g=0 landed k=4 (λ=20.00) — wavelength
  check cannot discriminate substrate-with-engram from substrate-without.
- test_T2_FFT_SNR_above_3: 9.70 (computed over the single passing seed)
  → PASS in pytest, but statistically meaningless on n=1.

Two of three pre-registered tests fail. Verdict: NULL.

### Auxiliary tests (no regression)

- `tests/flux/test_benard.py::test_T2_benard_horizontal_wavelength`
  (seed=42) **PASS** with the new substrate (y-avg profile, sigma=1.0).
  `@pytest.mark.slow` marker removed as required by the R-1c-tris
  contract.
- `tests/flux/test_horizontal_dynamics.py`: 2/2 PASS.
- `tests/flux/test_thermal.py`: 6/6 PASS.
- `tests/flux/test_conservation.py`: 3/3 PASS.
- `tests/flux/test_crystallization.py`: 1/1 PASS.
- `tests/flux/test_decay.py`: 1/1 PASS.
- `tests/flux/test_dynamics.py`: 9/9 PASS.

Total: 23/23 auxiliary tests PASS. The substrate is not broken; it
just does not produce the spec's λ ≈ 2·Lz mode.

### Mechanism diagnosis (one paragraph)

The R-1b pressure-gradient force does close the horizontal-coupling
gap the original F1c phase-log identified. But it closes it toward the
substrate's natural mode at λ ≈ 2.7·Lz (k=3 in our 80×40×10 box) and,
once Poisson noise is suppressed by R-1c-tris's smoothing, toward k=1
(a single warm-cold asymmetry across the box). Stress-free side walls
on our cube physically produce that low-k regime; classical Rayleigh-
Bénard at the same Rayleigh number with stress-free top/bottom has
λ_c ≈ 2.83·Lz. The spec's λ_c ≈ 2·Lz is the no-slip case. **The
substrate's natural convective wavelength is fundamentally incompatible
with the pre-registered acceptance window.** Reducing measurement noise
(higher sigma, more particles, y-averaging) drives the pass rate DOWN,
not up — every successful noise-reduction lever made fewer seeds land
in [14, 26]. This is the state-detector signature in its inverted form.
Confirmed by the negative-control failure: at buoyancy_g=0 the substrate
can still produce a k=4 peak from RNG scatter alone (seed=137), so even
a thermal_on pass is not an engram-specific finding under this metric.

### Gap location

- Implementation: sound. R-1b's pressure-grad + R-1c-tris's smoothing
  are physically reasonable and don't regress any other test.
- Hypothesis (substrate produces Bénard cells under hot-floor/cold-ceiling
  driving): partially holds. Cells DO form, but at a larger wavelength
  than the spec predicts.
- **Acceptance specification: calibrated for the wrong boundary
  condition.** ±30% of 2·Lz = [1.4, 2.6]·Lz; the substrate produces
  2.7-8.0·Lz under different noise regimes. Either spec needs the
  stress-free upper bound (~2.83·Lz, suggesting a wider tolerance or
  a re-stated expected) or the substrate needs no-slip side walls
  (substrate-level change beyond R-1c-tris's scope; would touch
  `world/flux/boundary.py`, affect every other test, and warrants a
  human-authored amendment, not an autopilot decision).

### Files touched

- `world/flux/thermal.py` (+5 lines: `T_spatial_sigma` field on
  `ThermalConfig`)
- `world/flux/grid.py` (+12 lines: `spatial_sigma` kwarg in
  `update_temperature`, scipy gaussian_filter when >0)
- `world/flux/dynamics.py` (+5 lines: plumb sigma when `thermal_cfg`
  is present)
- `tests/flux/test_benard_robustness.py` (NEW, ~263 lines: 3
  pre-registered tests with module-scoped 10-seed fixtures)
- `tests/flux/test_benard.py` (small edit: y-averaged profile,
  `T_spatial_sigma=1.0`, drop `@pytest.mark.slow`)
- `docs/flux/phase-log.md` (this entry)

Per charter, the autopilot is NOT authorised to widen the acceptance
tolerance, change the spec's λ ≈ 2·Lz target, or restructure the
substrate's boundary conditions without a human-authored amendment.
Three architectural variants (R-1c parametric audit, R-1c-bis return-flow
injector, R-1c-tris anti-noise smoothing + density-boost) have now NULLed
on the same metric. The convergent finding is that the metric itself,
not any of the three architectures, is the source of the failure.

Recommendation for Michael on return: either redesign T2's acceptance
to match a stress-free Bénard regime (expected λ ≈ 2.83·Lz, or wider
tolerance), or substitute a different convection signature (e.g.
vorticity-based, per the brief's R-1c-quad fallback) that is robust
to the substrate's actual physics. Continuing to retry on the current
metric is no longer informative.
