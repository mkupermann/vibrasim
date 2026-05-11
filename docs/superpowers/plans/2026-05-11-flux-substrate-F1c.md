# Flux Substrate F1c — Thermal Dynamics → T2 Bénard

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the thermal-physics layer the substrate has been missing — bidirectional vibration motion + buoyancy coupling to T_local — so that Phase-1 test T2 (Bénard convection) passes. T1 + T3 + T4 stay green.

**Why this is a separate phase:** T2 needs *physics* the F0–F1b substrate doesn't have. Today a quantum is born at the floor with a fixed upward velocity (`vel_z = 2 ± 20%`), absorbed at any cold face, and never sees a force tied to local temperature. Bénard convection requires (a) free motion in all directions, (b) a buoyancy force that biases vel_z upward where T_local is high, (c) a damping mechanism so quanta equilibrate rather than fly out instantly. None of that exists yet. Binding/decay/bridges/plasticity are all *off* during T2 — it's pure thermal substrate validation.

**Architecture sketch (per spec §3, §5.1, §5.3, §7 T2):**

- **Bidirectional injection.** Hot floor injection initializes velocity with a random gaussian around 0 in all three axes, not a fixed upward bias. The upward drift emerges from buoyancy, not from initialization.
- **Buoyancy force.** Each tick, each free quantum gets a velocity nudge proportional to `(T_local - T_ref)` along the +z axis. Warm voxels push quanta up; cool voxels don't. T_ref is the cube-wide mean T (so the buoyancy is zero-mean — energy comes from the floor/ceiling boundary contrast, not the bulk).
- **Velocity damping.** Each tick, each quantum's velocity is multiplied by `(1 - μ * dt)`. This is the "mean free path" hinted at in spec §10 open question. Without damping, quanta accumulate kinetic energy indefinitely and convection never settles.
- **Cold ceiling, hot floor as T boundary conditions.** In addition to the existing inject/absorb mechanism, the grid's T field gets two boundary terms each tick:
  - `T[:,:,0] = max(T[:,:,0], T_hot_floor)` (floor stays at least T_hot)
  - `T[:,:,Lz-1] = min(T[:,:,Lz-1], T_cold_ceiling)` (ceiling stays at most T_cold)
  This is what spec §7 T2 means by "hot floor T_hot, cold ceiling T_cold". For Phase-1 T2 the floor is a *thermal* boundary, not just an *injection* boundary.

**Tech stack:** Python 3.13, numpy (already a dep), pytest. No new dependencies — FFT via `numpy.fft`.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §5.1 (substrate + grid), §5.3 (boundary), §6 (tick order: move comes before binding, so the buoyancy nudge goes in step 4-ish), §7 T2 (acceptance), §10 (open questions — cube dimensions + damping coefficient).

**Estimated wallclock:** 2–3 weeks solo; compressed under autonomous-build.

**Acceptance contract:**
- `uv run pytest tests/flux/test_benard.py -v` passes (T2)
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1 with buoyancy + damping)
- `uv run pytest tests/flux/test_crystallization.py -v` still passes (T3)
- `uv run pytest tests/flux/test_decay.py -v` still passes (T4)
- All 80 F1b flux tests still pass (or rewritten counterparts)
- All 382 legacy tests still pass

---

## What F1c deliberately defers

| Concept | Status in F1c | Where it lands |
|---|---|---|
| Multi-way binding (3+ quanta → 1 node) | NOT in scope | F2 or "Phase-1 polish" |
| Node-to-node binding via bridges | NOT in scope | F2 |
| Cochlea (resonator-bank input) | NOT in scope | F2 |
| Synthesis (output) | NOT in scope | F2 |
| Attention reallocate (PE-driven compute budget) | NOT in scope | F2 |
| `pred_coherence` as windowed cross-correlation | still F1a stub | F2 (when cochlea brings multi-frequency) |

The reason multi-way + node-to-node binding live outside F1c despite being spec §5.4 features: none of T1-T4 need them. They become useful once cochlea is in (F2), so it's cheaper to specify them alongside the multi-frequency regime.

---

## Open calibration choices (call these out in phase-log)

These are §10 open questions. Default values below; tune during T2 sweeps and record in phase-log per the F1a/F1b pattern.

| Param | Default | Purpose |
|---|---|---|
| `cube_dims` | `(30, 30, 60)` | Lx × Ly × Lz. Tall enough for one Bénard wavelength; wide enough to see 1–2 cells. Spec §10 suggests 20×60×20 but FFT-along-horizontal needs Lx ≥ 2λ ≈ 4×Lz, so trade-off: tall + wide gets expensive. Start at 30×30×60 and revisit. |
| `buoyancy_g` | `2.0` | Strength of (T_local - T_ref) → vel_z coupling, per unit T per unit time. |
| `damping_mu` | `0.5` | Velocity decay coefficient per unit time; vel *= (1 - μ*dt). |
| `T_hot_floor` | `5.0` | Floor T boundary condition. |
| `T_cold_ceiling` | `0.0` | Ceiling T boundary condition. |
| `inject_vel_xy_sigma` | `0.5` | Initial gaussian velocity stddev in xy at injection (replaces the F0 default 0.1 + upward-vz bias). |
| `inject_vel_z_sigma` | `0.5` | Initial gaussian velocity stddev in z at injection. |
| `n_inject` | `20` per tick | Higher than F1a's 5 — Bénard needs density to develop a clean field. |

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `world/flux/thermal.py` | `ThermalConfig` dataclass + `apply_buoyancy_and_damping(quanta, grid, cfg, dt)` + `enforce_thermal_boundaries(grid, cfg)`. Pure-function module; no new state. |
| `tests/flux/test_thermal.py` | Unit tests for buoyancy, damping, T-boundary enforcement. |
| `tests/flux/test_benard.py` | T2 integration test with FFT analysis. |

Modified files:

| Path | What changes |
|---|---|
| `world/flux/boundary.py` | `inject_hot_floor` gains `vel_z_sigma` kwarg (or new signature with bidirectional initial velocity); defaults preserve F0-F1b behavior so existing tests don't break. |
| `world/flux/dynamics.py` | New tick steps: buoyancy+damping right after move; T-boundary enforcement right before T-update. New kwarg `thermal_cfg`. F1c-mode return shape unchanged: `(exported, binding_heat, decay_heat)`. |
| `world/flux/__init__.py` | Re-export `ThermalConfig`, `apply_buoyancy_and_damping`, `enforce_thermal_boundaries`. |
| `docs/flux/phase-log.md` | F1c start + close entries + per-sweep notes. |
| `README.md` | One-line status update on F1c. |

**Conservation accounting note:** buoyancy and damping change vibration *velocity* but not energy in the current substrate model (energy = a fixed scalar per quantum, see spec §5.2: "energy_quantum (scalar, default 1.0)"). If F1c later couples kinetic energy back to `energy_quantum`, the auditor needs new fields. For F1c-as-specced, no auditor changes.

---

## Task 1: F1c start — phase-log entry

**Files:** Modify `docs/flux/phase-log.md`.

- [ ] Append the F1c-start block describing scope, open calibration choices, deferred items.
- [ ] Commit: `flux F1c start: phase-log entry`.

---

## Task 2: ThermalConfig + buoyancy + damping (pure function)

**Files:**
- Create: `world/flux/thermal.py`
- Create: `tests/flux/test_thermal.py`

- [ ] **Step 1: Tests first.**

```python
"""Tests for thermal layer — F1c."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.thermal import (
    ThermalConfig,
    apply_buoyancy_and_damping,
    enforce_thermal_boundaries,
)


def test_buoyancy_pushes_quanta_up_in_hot_voxel():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[2, 2, 0] = 10.0  # hot floor voxel
    slot = q.add(pos=(2.5, 2.5, 0.5), vel=(0, 0, 0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=2.0, damping_mu=0.0, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    # Δvz = buoyancy_g * (T_local - T_ref) * dt = 2.0 * 10.0 * 0.1 = 2.0
    assert q.vel[slot, 2] == pytest.approx(2.0)
    # No buoyancy in x/y
    assert q.vel[slot, 0] == pytest.approx(0.0)
    assert q.vel[slot, 1] == pytest.approx(0.0)


def test_buoyancy_does_not_push_in_cold_voxel():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:] = 0.0  # uniform cold
    slot = q.add(pos=(2.5, 2.5, 4.5), vel=(0, 0, 0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=2.0, damping_mu=0.0, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    assert q.vel[slot, 2] == pytest.approx(0.0)


def test_damping_shrinks_velocity():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    slot = q.add(pos=(2.5, 2.5, 2.5), vel=(1.0, -1.0, 2.0),
                 freq=1.0, polarity=1, energy=1.0)
    cfg = ThermalConfig(buoyancy_g=0.0, damping_mu=0.5, T_ref=0.0)
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    # vel *= (1 - μ*dt) = (1 - 0.05) = 0.95
    np.testing.assert_allclose(q.vel[slot], [0.95, -0.95, 1.9])


def test_damping_only_affects_alive_quanta():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    s = q.add(pos=(2.5, 2.5, 2.5), vel=(1.0, 0.0, 0.0),
              freq=1.0, polarity=1, energy=1.0)
    q.remove(s)
    cfg = ThermalConfig(buoyancy_g=0.0, damping_mu=0.5, T_ref=0.0)
    # Should be a no-op since nothing alive
    apply_buoyancy_and_damping(q, g, cfg, dt=0.1)
    assert q.vel[s, 0] == 0.0  # remove() zeros velocity


def test_thermal_boundaries_clamp_floor_and_ceiling():
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:, :, 0] = 1.0
    g.T[:, :, 4] = 3.0
    cfg = ThermalConfig(T_hot_floor=5.0, T_cold_ceiling=0.5)
    enforce_thermal_boundaries(g, cfg)
    assert (g.T[:, :, 0] == 5.0).all()  # raised to T_hot
    assert (g.T[:, :, 4] == 0.5).all()  # lowered to T_cold


def test_thermal_boundaries_dont_disturb_middle():
    g = Grid(dims=(5, 5, 5), voxel_size=1.0)
    g.T[:, :, 2] = 1.5
    cfg = ThermalConfig(T_hot_floor=5.0, T_cold_ceiling=0.0)
    enforce_thermal_boundaries(g, cfg)
    assert (g.T[:, :, 2] == 1.5).all()
```

- [ ] **Step 2: Implement `world/flux/thermal.py`.**

```python
"""Thermal layer — F1c.

Buoyancy: vel_z gets nudged by (T_local - T_ref) × buoyancy_g × dt.
Damping: vel *= (1 - damping_mu × dt). Both applied per tick to all
alive quanta.

Thermal boundaries clamp grid.T at floor and ceiling layers to keep
the convection driver constant.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

from world.flux.quantum import Quanta
from world.flux.grid import Grid


@dataclass
class ThermalConfig:
    buoyancy_g: float = 2.0
    damping_mu: float = 0.5
    T_ref: float = 0.0           # if 0, buoyancy is one-sided (T>0 pushes up)
    T_hot_floor: float = 5.0
    T_cold_ceiling: float = 0.0


def apply_buoyancy_and_damping(quanta: Quanta, grid: Grid,
                                cfg: ThermalConfig, dt: float) -> None:
    """In-place update of quanta.vel.

    Buoyancy: vel_z += g * (T_local - T_ref) * dt
    Damping:  vel    *= (1 - μ * dt)
    """
    if quanta.n_alive() == 0:
        return
    alive = quanta.alive
    pos = quanta.pos[alive]
    s = grid.voxel_size
    Lx, Ly, Lz = grid.dims
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    T_local = grid.T[ix, iy, iz]
    dvz = cfg.buoyancy_g * (T_local - cfg.T_ref) * dt
    quanta.vel[alive, 2] += dvz
    factor = 1.0 - cfg.damping_mu * dt
    quanta.vel[alive] *= factor


def enforce_thermal_boundaries(grid: Grid, cfg: ThermalConfig) -> None:
    """Clamp the floor layer at T_hot, ceiling layer at T_cold.

    Use max/min so the boundary conditions are a *floor*/*ceiling* on
    T at those layers, not an overwrite. This lets density-driven T
    updates only affect interior voxels.
    """
    grid.T[:, :, 0] = np.maximum(grid.T[:, :, 0], cfg.T_hot_floor)
    grid.T[:, :, -1] = np.minimum(grid.T[:, :, -1], cfg.T_cold_ceiling)
```

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_thermal.py -v`. Expect 6/6 pass.

- [ ] **Step 4: Commit** `flux F1c task 2: ThermalConfig + buoyancy + damping`.

---

## Task 3: Wire thermal into the tick

**Files:** Modify `world/flux/dynamics.py`.

New tick order:

1. Inject
2. Move (pos += vel * dt) — unchanged
3. **Buoyancy + damping** (NEW: nudges vel based on T_local; damps overall) — placed *after* move so this tick's move uses the previous tick's velocity (consistent with the move/T-update ordering)
4. Absorb at cold faces
5. Binding (if configured)
6. Structure-flux + plasticity + pruning (if configured)
7. Update T from density
8. **Thermal-boundary enforcement** (NEW: clamps floor/ceiling T) — placed *after* T-update so it overrides the density-based T at the boundary layers

- [ ] **Step 1: Add `thermal_cfg` kwarg to `tick`.** When given, run buoyancy+damping after move and enforce_thermal_boundaries after T-update.

- [ ] **Step 2: Update test_dynamics.** Add a smoke test that thermal_cfg with damping_mu=0.5 actually shrinks velocity over a tick.

- [ ] **Step 3: Run** all existing flux tests. They should still pass since thermal_cfg=None preserves F0/F1a/F1b behavior.

- [ ] **Step 4: Commit** `flux F1c task 3: wire thermal into tick`.

---

## Task 4: Bidirectional injection

**Files:** Modify `world/flux/boundary.py`.

`inject_hot_floor` gains optional `vel_z_sigma` kwarg. When given, vel_z is gaussian around 0 with the given sigma (not pinned upward). Default behavior preserved.

- [ ] **Step 1: Add `vel_z_sigma: float | None = None` kwarg.** If given, replaces the existing "vel_z >= 0" clamping logic with `vz = rng.normal(0.0, vel_z_sigma)`.

- [ ] **Step 2: Unit test:** with vel_z_sigma=0.5 and rng(seed=0), confirm the empirical mean velocity over 1000 injections is ≈ 0 ± 0.05.

- [ ] **Step 3: Commit** `flux F1c task 4: bidirectional injection at hot floor`.

---

## Task 5: T2 Bénard integration test

**Files:** Create `tests/flux/test_benard.py`.

Spec §7 T2: hot floor + cold ceiling (no audio), 10000 ticks, FFT of T field along horizontal axis shows peak at wavelength λ ≈ 2 × cube_height ±30%.

- [ ] **Step 1: Write the test.**

```python
"""T2 — Bénard convection acceptance test.

Spec §7 T2: hot floor T_hot, cold ceiling T_cold (no audio).
10000 ticks. At steady state, FFT of the temperature field along
the horizontal axis shows a peak at wavelength λ ≈ 2 × cube_height
within ±30%.

This is the F1c acceptance test. Binding/decay/plasticity all
disabled — pure thermal substrate validation.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.thermal import ThermalConfig


def test_T2_benard_horizontal_wavelength():
    rng_inject = np.random.default_rng(42)
    LX, LY, LZ = 30, 30, 60
    q = Quanta(max_quanta=200_000)
    g = Grid(dims=(LX, LY, LZ), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    tcfg = ThermalConfig(
        buoyancy_g=2.0, damping_mu=0.5, T_ref=0.0,
        T_hot_floor=5.0, T_cold_ceiling=0.0,
    )

    N_PER_TICK = 20
    DT = 0.1
    N_TICKS = 10000

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid, n=N_PER_TICK, energy_per=1.0,
            freq_mean=200.0, vel_z_sigma=0.5, vel_xy_sigma=0.5,
            rng=rng_inject,
        )
        audit.record_injection(count * 1.0)
        return count * 1.0

    for t in range(N_TICKS):
        exported = tick(
            q, g, dt=DT, injector=injector, thermal_cfg=tcfg,
        )
        audit.record_export(exported)
        audit.check()
        audit.step()

    # FFT of horizontal T profile at mid-height
    mid_z = LZ // 2
    profile = g.T[:, LY // 2, mid_z]   # 1D slice along x
    fft = np.abs(np.fft.rfft(profile - profile.mean()))
    if fft.sum() == 0:
        pytest.fail("Flat horizontal T profile — no convection cells formed")
    k_peak = int(np.argmax(fft))
    if k_peak == 0:
        pytest.fail(f"FFT peak at DC (k=0) — no spatial modulation")
    wavelength = LX / k_peak
    expected = 2.0 * LZ
    tol = 0.30 * expected
    assert abs(wavelength - expected) <= tol, (
        f"T2 wavelength {wavelength:.2f} not within ±30% of {expected:.2f}. "
        f"k_peak={k_peak}, profile.std={profile.std():.4f}. "
        f"Tune ThermalConfig or cube dims in docs/flux/phase-log.md."
    )
```

- [ ] **Step 2: Run** `uv run pytest tests/flux/test_benard.py -v`. Likely fails first try.

- [ ] **Step 3: Up to 5 ThermalConfig + cube-shape sweeps** if T2 fails. Suggested order (cheapest to most expensive):
  1. `damping_mu` — too high = no convection, too low = chaos. Sweep 0.1, 0.3, 0.5, 1.0, 2.0.
  2. `buoyancy_g` — drives the instability. Sweep 1.0, 2.0, 5.0, 10.0.
  3. `cube_dims` — change Lx (wider = more visible cells) or Lz (taller = larger λ).
  4. `n_inject` — more density = stronger T gradient.
  5. `T_hot_floor` / `T_cold_ceiling` — bigger contrast = stronger convection.

  Document each in phase-log per the F1a/F1b pattern.

- [ ] **Step 4: Commit** `flux F1c task 5: T2 Bénard test passes`.

- [ ] **Step 5: BLOCKER** — if T2 fails after 5 sweeps, escalate. The buoyancy/damping model may need rethinking (e.g., adding return-flow injection at the ceiling, or a different T-coupling functional form).

---

## Task 6: Verify T3 + T4 + T1 still pass

The thermal layer adds buoyancy and damping. T3 and T4's test_crystallization / test_decay don't pass `thermal_cfg`, so they should be unaffected — but verify anyway since dynamics.py was touched.

- [ ] **Step 1: Run** `uv run pytest tests/flux/ -v`. All previous 80 tests + new 6 thermal tests + 1 T2 test = expect ~87 pass.

- [ ] **Step 2: Run legacy suite.** Expect 382 pass.

- [ ] **Step 3: If T3 or T4 regressed**, the most likely cause is an accidental side effect in the tick orchestration. Bisect.

---

## Task 7: __init__ re-exports + README + F1c close

**Files:**
- Modify: `world/flux/__init__.py` (add `ThermalConfig`, `apply_buoyancy_and_damping`, `enforce_thermal_boundaries`)
- Modify: `README.md`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Update `__init__.py`** with the 3 thermal symbols and rebuilt `__all__`.

- [ ] **Step 2: README "Two substrates" status line**:

```
Status as of <date>: F0 + F1a + F1b + F1c complete (all of Phase 1: T1 conservation + T3 crystallization + T4 decay + T2 Bénard convection). F2 (cochlea + synthesis + first audio input) is next.
```

- [ ] **Step 3: Phase-log F1c-close entry**: task summary, final ThermalConfig + cube dims, T2 measured wavelength, test counts.

- [ ] **Step 4: Run** `uv run pytest tests/flux/ -v` (expect all green) and the legacy suite (expect 382).

- [ ] **Step 5: Commit** `flux F1c complete: re-exports + README status + phase-log`.

---

## Notes for autonomous execution

- **T2 is unlike T1/T3/T4** in that it doesn't involve binding or decay at all. Pure substrate. So binding-side regression risk is low; the risk is T2 itself simply failing because the buoyancy+damping model isn't enough.
- **The 5-sweep cap from the F1a/F1b plan still applies.** If T2 won't pass with 5 sweeps' worth of tuning, escalate — the spec deliberately leaves the buoyancy and damping mechanisms vague, so an architectural rethink (e.g., adding a small return-flow injector at the ceiling, or coupling T to *vibration kinetic energy* rather than density) is on the table.
- **Cube dimensions are expensive.** A 30×30×60 cube with 20 quanta/tick × 10000 ticks ≈ 6M quanta-ticks. Memory budget: `max_quanta=200_000` slots should hold the live population if damping keeps it bounded. Watch for `add returns -1` warnings.
- **FFT interpretation pitfall.** If the profile is mostly DC (a uniform vertical gradient with no horizontal variation), the FFT peak is at k=0 and `wavelength = LX / 0` is undefined. The test must reject that case. Spec §7 T2 implicitly assumes you have a nonzero-k peak; if you only see k=0, no Bénard cells formed.
- **Energy conservation under thermal.** Buoyancy and damping change *velocity*, not energy_quantum. The auditor formula doesn't change. But if a future spec refinement says "damping dissipates energy as heat," that becomes a new exported-heat channel and the auditor needs `record_thermal_heat`. Out of F1c scope.
