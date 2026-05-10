# Flux Substrate F0 — Skeleton + Energy Conservation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the skeleton of `world/flux/` and `agent/flux/`, plus the per-tick energy-conservation audit, sufficient to make Phase-1 test T1 pass. No binding, no plasticity, no audio — pure motion + boundary + conservation accounting.

**Architecture:** Struct-of-arrays vibration entities (matches legacy EQMOD pattern). Plain numpy, no Numba yet (small scale; performance is not the F0 bottleneck). Energy is `float64` for clean conservation arithmetic. Per-tick conservation is enforced as an `assert`, not a soft check — a failed audit halts the run.

**Tech Stack:** Python 3.13, numpy ≥ 1.26, pytest ≥ 8.0. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — read sections §3, §5.1–§5.3, §6, §7 (T1 only) before starting.

**Estimated wallclock:** 1 week solo developer.

**Acceptance contract:** `pytest tests/flux/test_conservation.py -v` passes. The test runs 1000 ticks under constant injection on a 10×10×10 voxel cube; final assertion `|E_initial + E_injected - (E_free + E_exported)| < 1e-9 * max(E_injected, 1.0)` must hold.

---

## File structure (locked decisions)

New files this plan creates:

| Path | Responsibility |
|---|---|
| `world/flux/__init__.py` | Module marker, exposes `Quanta`, `Grid`, `EnergyAuditor`, `tick` |
| `world/flux/quantum.py` | `Quanta` SoA container — pre-allocated arrays for up to `MAX_QUANTA` vibrations |
| `world/flux/grid.py` | `Grid` class — voxel dimensions, temperature field, position→voxel mapping |
| `world/flux/boundary.py` | `inject_hot_floor` + `absorb_cold_faces` functions |
| `world/flux/dynamics.py` | `tick(quanta, grid, audit, dt)` — orchestrates motion + boundary + temperature update |
| `world/flux/audit.py` | `EnergyAuditor` — tracks `E_injected_total`, `E_exported_total`, asserts conservation |
| `agent/flux/__init__.py` | Empty stub (filled in F2) |
| `tests/flux/__init__.py` | Test package marker |
| `tests/flux/test_quantum.py` | Quanta unit tests |
| `tests/flux/test_grid.py` | Grid unit tests |
| `tests/flux/test_boundary.py` | Injection + absorption unit tests |
| `tests/flux/test_dynamics.py` | Single-tick motion tests |
| `tests/flux/test_audit.py` | Auditor unit tests |
| `tests/flux/test_conservation.py` | T1 integration test (the acceptance test) |
| `docs/flux/principle.md` | Skeleton — full content added in F1 |
| `docs/flux/phase-log.md` | Append-only build log — first entry: F0 start |

Modified files:

| Path | What changes |
|---|---|
| `README.md` | Add a paragraph after the existing "What runs today" section naming the two substrates side by side |

---

## Task 1: Project skeleton — directories and stubs

**Files:**
- Create: `world/flux/__init__.py`
- Create: `agent/flux/__init__.py`
- Create: `tests/flux/__init__.py`
- Create: `docs/flux/principle.md`
- Create: `docs/flux/phase-log.md`

- [ ] **Step 1: Create `world/flux/__init__.py`**

```python
"""Flux Substrate — thermodynamically grounded learning substrate.

See docs/superpowers/specs/2026-05-10-flux-substrate-design.md for the
design rationale and falsifier contract.

This module is under active development. Public API stabilises after F1.
"""
from __future__ import annotations
```

- [ ] **Step 2: Create `agent/flux/__init__.py`**

```python
"""Flux Substrate — agent layer (cochlea, synthesis, attention, loop).

Empty in F0. Filled in F2+. See spec §5.6-§5.8.
"""
from __future__ import annotations
```

- [ ] **Step 3: Create `tests/flux/__init__.py`**

```python
```

(Empty file — pytest package marker.)

- [ ] **Step 4: Create `docs/flux/principle.md`**

```markdown
# The Flux Substrate Principle

> *Filled in F1.*

Placeholder. The principle is documented in
[`../superpowers/specs/2026-05-10-flux-substrate-design.md`](../superpowers/specs/2026-05-10-flux-substrate-design.md)
section §3. This file expands it into prose for reading.
```

- [ ] **Step 5: Create `docs/flux/phase-log.md`**

```markdown
# Flux Substrate — Phase Log

Append-only build log. Each entry: date, phase, status, key decisions.

## 2026-05-10 — F0 start

- Spec committed at `2bab7a7`.
- Plan: `docs/superpowers/plans/2026-05-10-flux-substrate-F0.md`.
- Target: skeleton + T1 conservation test passes.
- Estimated 1 week solo.
```

- [ ] **Step 6: Commit**

```bash
git add world/flux/ agent/flux/ tests/flux/ docs/flux/
git commit -m "flux F0 task 1: project skeleton + phase log

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Vibration entity (`world/flux/quantum.py`)

**Files:**
- Create: `world/flux/quantum.py`
- Create: `tests/flux/test_quantum.py`

- [ ] **Step 1: Write failing test `tests/flux/test_quantum.py`**

```python
"""Tests for Quanta SoA container."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta


def test_quanta_empty_on_init():
    q = Quanta(max_quanta=100)
    assert q.max_quanta == 100
    assert q.n_alive() == 0
    assert q.alive.shape == (100,)
    assert q.alive.dtype == np.bool_
    assert q.pos.shape == (100, 3)
    assert q.pos.dtype == np.float64
    assert q.vel.shape == (100, 3)
    assert q.energy.shape == (100,)
    assert q.freq.shape == (100,)
    assert q.polarity.dtype == np.int8


def test_quanta_add_returns_slot_and_writes_fields():
    q = Quanta(max_quanta=10)
    slot = q.add(pos=(1.5, 2.5, 3.5), vel=(0.1, 0.2, 0.3),
                 freq=440.0, polarity=1, energy=1.0)
    assert 0 <= slot < 10
    assert q.alive[slot]
    assert q.pos[slot, 0] == 1.5
    assert q.pos[slot, 1] == 2.5
    assert q.pos[slot, 2] == 3.5
    assert q.vel[slot, 0] == 0.1
    assert q.freq[slot] == 440.0
    assert q.polarity[slot] == 1
    assert q.energy[slot] == 1.0
    assert q.n_alive() == 1


def test_quanta_add_uses_free_slots_in_order():
    q = Quanta(max_quanta=5)
    s0 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s1 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s2 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    assert {s0, s1, s2} == {0, 1, 2}
    assert q.n_alive() == 3


def test_quanta_remove_marks_slot_free_and_reusable():
    q = Quanta(max_quanta=5)
    s0 = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    s1 = q.add((1, 1, 1), (0, 0, 0), 100.0, 1, 1.0)
    q.remove(s0)
    assert not q.alive[s0]
    assert q.alive[s1]
    assert q.n_alive() == 1
    # Re-adding should reuse slot s0
    s2 = q.add((2, 2, 2), (0, 0, 0), 100.0, 1, 1.0)
    assert s2 == s0
    assert q.alive[s0]
    assert q.n_alive() == 2


def test_quanta_add_returns_minus_one_when_full():
    q = Quanta(max_quanta=2)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    full = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.0)
    assert full == -1


def test_quanta_total_energy_sums_alive_only():
    q = Quanta(max_quanta=5)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 1.5)
    q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 2.5)
    s = q.add((0, 0, 0), (0, 0, 0), 100.0, 1, 99.0)
    q.remove(s)
    assert q.total_energy() == 4.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_quantum.py -v`
Expected: `ModuleNotFoundError: No module named 'world.flux.quantum'` (or similar import error)

- [ ] **Step 3: Implement `world/flux/quantum.py`**

```python
"""Quanta — struct-of-arrays container for energy-carrying vibrations.

Each vibration carries a discrete energy quantum. Bound vibrations live
in the Structures graph (added in F1); free vibrations live here.
"""
from __future__ import annotations
import numpy as np


class Quanta:
    """Pre-allocated SoA container for free vibrations.

    Slots are reused on remove: `add` finds the lowest-index free slot.
    Energy is float64 for clean conservation arithmetic; positions and
    velocities are float64 to match legacy EQMOD's `world/state.py`.
    """

    def __init__(self, max_quanta: int):
        self.max_quanta = int(max_quanta)
        N = self.max_quanta
        self.pos = np.zeros((N, 3), dtype=np.float64)
        self.vel = np.zeros((N, 3), dtype=np.float64)
        self.freq = np.zeros(N, dtype=np.float64)
        self.polarity = np.zeros(N, dtype=np.int8)
        self.energy = np.zeros(N, dtype=np.float64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0  # cursor for free-slot search

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def total_energy(self) -> float:
        return float(self.energy[self.alive].sum())

    def add(self, pos, vel, freq: float, polarity: int,
            energy: float) -> int:
        """Add a vibration, returning its slot index or -1 if full."""
        N = self.max_quanta
        # Search from _next_search forward, wrap around once
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.pos[j] = pos
                self.vel[j] = vel
                self.freq[j] = freq
                self.polarity[j] = polarity
                self.energy[j] = energy
                self.alive[j] = True
                self._next_search = j  # next add can try here first
                return j
        return -1

    def remove(self, slot: int) -> float:
        """Mark slot dead; return the released energy quantum."""
        if not self.alive[slot]:
            return 0.0
        e = float(self.energy[slot])
        self.alive[slot] = False
        self.energy[slot] = 0.0
        # Reset search cursor so this slot is reused first
        self._next_search = min(self._next_search, slot)
        return e
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_quantum.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/quantum.py tests/flux/test_quantum.py
git commit -m "flux F0 task 2: Quanta SoA container

Pre-allocated arrays for up to MAX_QUANTA free vibrations. Slot reuse
via lowest-index free search. Total-energy accessor for audit hook.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Voxel grid (`world/flux/grid.py`)

**Files:**
- Create: `world/flux/grid.py`
- Create: `tests/flux/test_grid.py`

- [ ] **Step 1: Write failing test `tests/flux/test_grid.py`**

```python
"""Tests for Grid — voxelisation + temperature field."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.grid import Grid


def test_grid_creates_zeroed_temperature_field():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    assert g.dims == (10, 10, 10)
    assert g.voxel_size == 1.0
    assert g.T.shape == (10, 10, 10)
    assert g.T.dtype == np.float64
    np.testing.assert_array_equal(g.T, np.zeros((10, 10, 10)))


def test_position_to_voxel_within_bounds():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    assert g.pos_to_voxel((0.0, 0.0, 0.0)) == (0, 0, 0)
    assert g.pos_to_voxel((5.5, 7.2, 3.1)) == (5, 7, 3)
    assert g.pos_to_voxel((9.99, 9.99, 9.99)) == (9, 9, 9)


def test_position_to_voxel_clips_at_boundaries():
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Out-of-bounds should clip to valid voxel
    assert g.pos_to_voxel((10.5, 5.0, 5.0)) == (9, 5, 5)
    assert g.pos_to_voxel((-0.5, 5.0, 5.0)) == (0, 5, 5)


def test_position_to_voxel_respects_voxel_size():
    g = Grid(dims=(5, 5, 5), voxel_size=2.0)
    assert g.pos_to_voxel((0.0, 0.0, 0.0)) == (0, 0, 0)
    assert g.pos_to_voxel((2.0, 2.0, 2.0)) == (1, 1, 1)
    assert g.pos_to_voxel((3.9, 5.5, 9.99)) == (1, 2, 4)


def test_update_temperature_from_density():
    g = Grid(dims=(4, 4, 4), voxel_size=1.0, T_smoothing=1.0)
    # Density field of size dims: voxel (2,2,2) has 5 quanta, rest zero
    density = np.zeros((4, 4, 4), dtype=np.float64)
    density[2, 2, 2] = 5.0
    g.update_temperature(density)
    assert g.T[2, 2, 2] == 5.0
    assert g.T[0, 0, 0] == 0.0


def test_temperature_smoothing_is_exponential():
    g = Grid(dims=(2, 2, 2), voxel_size=1.0, T_smoothing=0.5)
    density = np.full((2, 2, 2), 10.0)
    g.update_temperature(density)
    # First update: 0.5 * 10 + 0.5 * 0 = 5
    np.testing.assert_allclose(g.T, np.full((2, 2, 2), 5.0))
    g.update_temperature(density)
    # Second update: 0.5 * 10 + 0.5 * 5 = 7.5
    np.testing.assert_allclose(g.T, np.full((2, 2, 2), 7.5))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_grid.py -v`
Expected: `ModuleNotFoundError: No module named 'world.flux.grid'`

- [ ] **Step 3: Implement `world/flux/grid.py`**

```python
"""Grid — voxel dimensions + temperature field.

The temperature is exponentially-smoothed local free-quanta density,
updated each tick from the Quanta positions. In F0 the temperature is
computed and stored but does not gate any binding (no binding rule
exists yet). It will gate binding from F1 onward.
"""
from __future__ import annotations
import numpy as np


class Grid:
    """3D voxel grid with an exponentially-smoothed temperature field.

    `dims` is (Lx, Ly, Lz) in voxel counts.
    `voxel_size` is the physical extent of one voxel.
    `T_smoothing` is α in T(t+1) = α * density + (1-α) * T(t).
    Default α = 0.1 gives a ~10-tick effective memory.
    """

    def __init__(self, dims: tuple[int, int, int],
                 voxel_size: float = 1.0,
                 T_smoothing: float = 0.1):
        self.dims = tuple(int(d) for d in dims)
        self.voxel_size = float(voxel_size)
        self.T_smoothing = float(T_smoothing)
        self.T = np.zeros(self.dims, dtype=np.float64)

    def pos_to_voxel(self, pos) -> tuple[int, int, int]:
        """Map a continuous position to a clipped voxel index."""
        x, y, z = pos
        ix = int(np.clip(x / self.voxel_size, 0, self.dims[0] - 1))
        iy = int(np.clip(y / self.voxel_size, 0, self.dims[1] - 1))
        iz = int(np.clip(z / self.voxel_size, 0, self.dims[2] - 1))
        return ix, iy, iz

    def update_temperature(self, density: np.ndarray) -> None:
        """Exponential smoothing: T(t+1) = α * density + (1-α) * T(t)."""
        if density.shape != self.dims:
            raise ValueError(
                f"density shape {density.shape} != grid dims {self.dims}"
            )
        a = self.T_smoothing
        self.T = a * density + (1.0 - a) * self.T
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_grid.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/grid.py tests/flux/test_grid.py
git commit -m "flux F0 task 3: Grid + temperature field

Voxel dims, voxel size, exponentially smoothed temperature field
updated from local quantum density. Field is computed but doesn't
gate anything in F0 — F1 binding rule will read it.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Hot floor injection (`world/flux/boundary.py` — part 1)

**Files:**
- Create: `world/flux/boundary.py`
- Create: `tests/flux/test_boundary.py`

- [ ] **Step 1: Write failing test `tests/flux/test_boundary.py`**

```python
"""Tests for boundary injection + absorption."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.boundary import inject_hot_floor


def test_inject_hot_floor_adds_correct_count():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    injected = inject_hot_floor(
        q, g, n=5, energy_per=1.0,
        freq_mean=200.0, vel_z_mean=1.0,
        rng=np.random.default_rng(0),
    )
    assert injected == 5
    assert q.n_alive() == 5


def test_inject_hot_floor_places_at_z_near_zero():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    inject_hot_floor(q, g, n=20, energy_per=1.0,
                     freq_mean=200.0, vel_z_mean=1.0,
                     rng=np.random.default_rng(0))
    alive_z = q.pos[q.alive, 2]
    # All injected vibrations should start in the lowest voxel layer
    assert alive_z.min() >= 0.0
    assert alive_z.max() < 1.0  # voxel_size


def test_inject_hot_floor_gives_upward_velocity():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    inject_hot_floor(q, g, n=20, energy_per=1.0,
                     freq_mean=200.0, vel_z_mean=2.0,
                     rng=np.random.default_rng(0))
    alive_vz = q.vel[q.alive, 2]
    # All upward (positive z velocity)
    assert (alive_vz > 0).all()
    # Mean roughly matches vel_z_mean (with sampling noise tolerance)
    assert abs(alive_vz.mean() - 2.0) < 1.0


def test_inject_hot_floor_assigns_constant_energy():
    q = Quanta(max_quanta=100)
    g = Grid(dims=(10, 10, 10))
    inject_hot_floor(q, g, n=10, energy_per=1.5,
                     freq_mean=200.0, vel_z_mean=1.0,
                     rng=np.random.default_rng(0))
    assert q.total_energy() == 15.0


def test_inject_hot_floor_returns_actual_count_when_buffer_full():
    q = Quanta(max_quanta=3)
    g = Grid(dims=(10, 10, 10))
    injected = inject_hot_floor(q, g, n=10, energy_per=1.0,
                                freq_mean=200.0, vel_z_mean=1.0,
                                rng=np.random.default_rng(0))
    assert injected == 3
    assert q.n_alive() == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_boundary.py -v`
Expected: `ImportError: cannot import name 'inject_hot_floor'`

- [ ] **Step 3: Implement `world/flux/boundary.py`**

```python
"""Boundary handling — hot floor injection + cold face absorption.

Hot floor is the z=0 face: source of new energy quanta.
Cold faces are z=Lz (ceiling) and the four side walls: energy sinks.
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid


def inject_hot_floor(quanta: Quanta, grid: Grid,
                     n: int,
                     energy_per: float,
                     freq_mean: float,
                     vel_z_mean: float,
                     freq_sigma: float = 0.0,
                     vel_xy_sigma: float = 0.1,
                     rng: np.random.Generator | None = None) -> int:
    """Inject up to `n` vibrations at the hot floor.

    Positions are uniform random in the z=0 voxel layer
    (x, y ∈ [0, Lx*size), z ∈ [0, voxel_size)).
    Velocities: upward (z>0) with sampled magnitude vel_z_mean,
    small random xy component (sigma=vel_xy_sigma).
    Frequencies: Gaussian around freq_mean.

    Returns: number actually injected (= n unless buffer fills first).
    """
    if rng is None:
        rng = np.random.default_rng()
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    injected = 0
    for _ in range(n):
        x = rng.uniform(0.0, Lx * s)
        y = rng.uniform(0.0, Ly * s)
        z = rng.uniform(0.0, s)  # Z within first voxel layer
        vx = rng.normal(0.0, vel_xy_sigma)
        vy = rng.normal(0.0, vel_xy_sigma)
        vz = rng.normal(vel_z_mean, vel_z_mean * 0.2)  # 20% scatter
        if vz <= 0.0:
            vz = vel_z_mean  # Floor at mean — keep upward
        freq = rng.normal(freq_mean, freq_sigma) if freq_sigma > 0 \
            else freq_mean
        slot = quanta.add(
            pos=(x, y, z), vel=(vx, vy, vz),
            freq=freq, polarity=1, energy=energy_per,
        )
        if slot < 0:
            break  # Buffer full
        injected += 1
    return injected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_boundary.py::test_inject_hot_floor_adds_correct_count tests/flux/test_boundary.py::test_inject_hot_floor_places_at_z_near_zero tests/flux/test_boundary.py::test_inject_hot_floor_gives_upward_velocity tests/flux/test_boundary.py::test_inject_hot_floor_assigns_constant_energy tests/flux/test_boundary.py::test_inject_hot_floor_returns_actual_count_when_buffer_full -v`
Expected: all 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/boundary.py tests/flux/test_boundary.py
git commit -m "flux F0 task 4: inject_hot_floor

Energy injection at z=0 voxel layer. Upward velocity with scatter,
configurable frequency, fixed energy per quantum. Returns actual
injection count when buffer fills.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Cold face absorption (`world/flux/boundary.py` — part 2)

**Files:**
- Modify: `world/flux/boundary.py`
- Modify: `tests/flux/test_boundary.py`

- [ ] **Step 1: Add failing tests for absorption to `tests/flux/test_boundary.py`**

Append at the bottom of the existing test file:

```python
from world.flux.boundary import absorb_cold_faces


def test_absorb_cold_faces_returns_zero_when_no_quanta_at_boundary():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quantum well inside the cube
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0),
          freq=100.0, polarity=1, energy=1.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 0.0
    assert q.n_alive() == 1


def test_absorb_cold_faces_removes_quanta_at_ceiling():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quanta at the ceiling face (z > Lz - delta)
    q.add(pos=(5.0, 5.0, 9.8), vel=(0, 0, 1), freq=100.0, polarity=1,
          energy=1.0)
    q.add(pos=(3.0, 3.0, 5.0), vel=(0, 0, 1), freq=100.0, polarity=1,
          energy=1.0)  # interior — not absorbed
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 1.0
    assert q.n_alive() == 1


def test_absorb_cold_faces_removes_quanta_at_side_walls():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # x near 0
    q.add(pos=(0.1, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # x near Lx
    q.add(pos=(9.9, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # y near 0
    q.add(pos=(5.0, 0.05, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # y near Ly
    q.add(pos=(5.0, 9.95, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    # interior
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=2.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 8.0  # 4 absorbed × 2.0
    assert q.n_alive() == 1


def test_absorb_cold_faces_does_not_absorb_at_hot_floor():
    """Hot floor (z near 0) must NOT be a cold face."""
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    q.add(pos=(5.0, 5.0, 0.05), vel=(0, 0, 1), freq=100, polarity=1,
          energy=1.0)
    exported = absorb_cold_faces(q, g, delta=0.5)
    assert exported == 0.0
    assert q.n_alive() == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_boundary.py -v -k absorb`
Expected: 4 tests FAIL with `ImportError: cannot import name 'absorb_cold_faces'`.

- [ ] **Step 3: Add `absorb_cold_faces` to `world/flux/boundary.py`**

Append at the bottom of `world/flux/boundary.py`:

```python
def absorb_cold_faces(quanta: Quanta, grid: Grid,
                      delta: float = 0.5) -> float:
    """Remove vibrations within delta of cold faces; return total
    absorbed energy.

    Cold faces: z = Lz*size (ceiling), x = 0, x = Lx*size,
    y = 0, y = Ly*size. The z = 0 face is the HOT FLOOR and is
    NOT absorbing.
    """
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    x_min, x_max = 0.0 + delta, Lx * s - delta
    y_min, y_max = 0.0 + delta, Ly * s - delta
    z_max = Lz * s - delta

    pos = quanta.pos
    alive = quanta.alive

    # Mask of alive quanta within delta of any cold face
    at_ceiling = (pos[:, 2] > z_max)
    at_x_low   = (pos[:, 0] < x_min)
    at_x_high  = (pos[:, 0] > x_max)
    at_y_low   = (pos[:, 1] < y_min)
    at_y_high  = (pos[:, 1] > y_max)

    to_absorb = alive & (at_ceiling | at_x_low | at_x_high |
                         at_y_low | at_y_high)

    exported = float(quanta.energy[to_absorb].sum())

    if exported > 0.0:
        # Mark all absorbed slots dead
        idx = np.where(to_absorb)[0]
        for i in idx:
            quanta.alive[i] = False
            quanta.energy[i] = 0.0
        # Reset search cursor
        quanta._next_search = int(idx.min())

    return exported
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_boundary.py -v`
Expected: all 9 boundary tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/boundary.py tests/flux/test_boundary.py
git commit -m "flux F0 task 5: absorb_cold_faces

Vibrations within delta of ceiling or side walls are removed; their
energy is returned for the audit. Hot floor (z=0) is explicitly NOT
absorbing.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Dynamics tick — motion + boundary (`world/flux/dynamics.py`)

**Files:**
- Create: `world/flux/dynamics.py`
- Create: `tests/flux/test_dynamics.py`

- [ ] **Step 1: Write failing test `tests/flux/test_dynamics.py`**

```python
"""Tests for the single-tick orchestration."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.dynamics import tick


def test_tick_moves_quanta_by_velocity_times_dt():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(1.0, 0.0, 0.5),
          freq=100, polarity=1, energy=1.0)
    tick(q, g, dt=0.1, injector=None)
    # Position should be (5.1, 5.0, 5.05)
    np.testing.assert_allclose(q.pos[0], [5.1, 5.0, 5.05])


def test_tick_absorbs_quanta_that_cross_cold_face():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    # Quantum that will cross the ceiling in 1 tick
    q.add(pos=(5.0, 5.0, 9.0), vel=(0, 0, 5.0), freq=100, polarity=1,
          energy=1.0)
    exported = tick(q, g, dt=1.0, injector=None)
    assert exported == 1.0
    assert q.n_alive() == 0


def test_tick_updates_temperature_from_quanta_density():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(4, 4, 4), voxel_size=1.0, T_smoothing=1.0)
    # 3 quanta all inside voxel (1, 1, 1)
    for _ in range(3):
        q.add(pos=(1.5, 1.5, 1.5), vel=(0, 0, 0),
              freq=100, polarity=1, energy=1.0)
    tick(q, g, dt=0.0, injector=None)  # dt=0: no motion
    # With T_smoothing=1.0 the new T is just the density
    assert g.T[1, 1, 1] == 3.0
    assert g.T[0, 0, 0] == 0.0


def test_tick_calls_injector_when_provided():
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    calls = {"count": 0, "injected": 0}
    def fake_injector(quanta, grid):
        quanta.add(pos=(5, 5, 0.1), vel=(0, 0, 1),
                   freq=100, polarity=1, energy=1.0)
        quanta.add(pos=(5, 5, 0.2), vel=(0, 0, 1),
                   freq=100, polarity=1, energy=1.0)
        calls["count"] += 1
        calls["injected"] += 2
        return 2.0
    # tick returns exported energy only; injector return value is
    # ignored by tick (the auditor tracks injection separately).
    exported = tick(q, g, dt=0.1, injector=fake_injector)
    assert calls["count"] == 1
    assert calls["injected"] == 2
    assert q.n_alive() == 2
    # At dt=0.1 and vel_z=1.0, neither quantum reaches the ceiling
    # (z=10) — nothing absorbed yet.
    assert exported == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_dynamics.py -v`
Expected: `ModuleNotFoundError: No module named 'world.flux.dynamics'`

- [ ] **Step 3: Implement `world/flux/dynamics.py`**

```python
"""Per-tick orchestration.

Order of operations in one tick (matches spec §6 for F0):
1. Inject at hot floor (if injector provided) → returns E_injected
2. Move free vibrations: pos += vel * dt
3. Absorb at cold faces → returns E_exported
4. Update temperature field from new density

Returns the tuple (E_injected, E_exported) for use by the auditor.
F1 will add structure-flux and binding-attempt steps. F0 is motion +
boundary + temperature only — no plasticity, no binding.
"""
from __future__ import annotations
from typing import Callable, Optional
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.boundary import absorb_cold_faces


Injector = Callable[[Quanta, Grid], float]
"""Function (quanta, grid) -> energy_injected_this_tick."""


def _compute_density(quanta: Quanta, grid: Grid) -> np.ndarray:
    """Histogram alive quanta into voxel bins → counts per voxel."""
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    density = np.zeros(grid.dims, dtype=np.float64)
    if quanta.n_alive() == 0:
        return density
    alive = quanta.alive
    pos = quanta.pos[alive]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    np.add.at(density, (ix, iy, iz), 1.0)
    return density


def tick(quanta: Quanta, grid: Grid, dt: float,
         injector: Optional[Injector],
         cold_face_delta: float = 0.5) -> float:
    """Run one tick. Returns E_exported (energy that left through cold
    faces).

    The caller is responsible for summing injected vs. exported and
    checking conservation — see audit.py.
    """
    # 1. Inject
    if injector is not None:
        # injector mutates `quanta`; we don't use its return here
        # since the auditor tracks injected separately via the
        # boundary helper return value. For F0 this is informational.
        injector(quanta, grid)

    # 2. Move
    alive = quanta.alive
    if alive.any():
        quanta.pos[alive] += quanta.vel[alive] * dt

    # 3. Absorb
    exported = absorb_cold_faces(quanta, grid, delta=cold_face_delta)

    # 4. Temperature
    density = _compute_density(quanta, grid)
    grid.update_temperature(density)

    return exported
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_dynamics.py -v`
Expected: all 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/dynamics.py tests/flux/test_dynamics.py
git commit -m "flux F0 task 6: dynamics tick (motion + boundary + temp)

Single tick orchestrates injection, motion, absorption, and
temperature-field update. No binding yet — F1 adds it.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Energy auditor (`world/flux/audit.py`)

**Files:**
- Create: `world/flux/audit.py`
- Create: `tests/flux/test_audit.py`

- [ ] **Step 1: Write failing test `tests/flux/test_audit.py`**

```python
"""Tests for the EnergyAuditor."""
from __future__ import annotations
import pytest

from world.flux.quantum import Quanta
from world.flux.audit import EnergyAuditor, ConservationViolation


def test_auditor_starts_balanced():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    assert a.E_initial == 0.0
    assert a.E_injected_total == 0.0
    assert a.E_exported_total == 0.0


def test_auditor_record_injection_accumulates():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    a.record_injection(2.5)
    a.record_injection(1.5)
    assert a.E_injected_total == 4.0


def test_auditor_record_export_accumulates():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    a.record_export(0.5)
    a.record_export(0.5)
    assert a.E_exported_total == 1.0


def test_auditor_balance_holds_after_injection_and_persistence():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=3.0)
    a.record_injection(3.0)
    a.check()  # Should not raise


def test_auditor_balance_holds_after_export():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=5.0)
    a.record_injection(5.0)
    # Simulate boundary absorbing the quantum
    q.remove(0)
    a.record_export(5.0)
    a.check()  # Should not raise


def test_auditor_raises_on_violation():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    # Inject 5 but only 4 actually appears in quanta -> imbalance
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=4.0)
    a.record_injection(5.0)
    with pytest.raises(ConservationViolation):
        a.check()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_audit.py -v`
Expected: `ModuleNotFoundError: No module named 'world.flux.audit'`

- [ ] **Step 3: Implement `world/flux/audit.py`**

```python
"""Energy conservation audit.

Conservation law:
    E_initial + E_injected_total == E_in_quanta + E_exported_total
within tolerance `tol` × max(|E_initial + E_injected_total|, 1.0).

A failed audit halts the run (raises ConservationViolation). This is
non-negotiable per the spec §3: a failed audit means the code is broken,
not the physics. Production mode can disable the assertion via the
caller passing audit=None to tick(); default is enabled.
"""
from __future__ import annotations

from world.flux.quantum import Quanta


class ConservationViolation(AssertionError):
    """Raised when energy conservation is violated beyond tolerance."""


class EnergyAuditor:
    def __init__(self, quanta: Quanta, tol: float = 1e-9):
        self.quanta = quanta
        self.tol = float(tol)
        self.E_initial: float = 0.0
        self.E_injected_total: float = 0.0
        self.E_exported_total: float = 0.0
        self.tick_count: int = 0

    def record_initial(self) -> None:
        self.E_initial = self.quanta.total_energy()

    def record_injection(self, e: float) -> None:
        self.E_injected_total += float(e)

    def record_export(self, e: float) -> None:
        self.E_exported_total += float(e)

    def check(self) -> None:
        """Assert conservation. Raises ConservationViolation on
        imbalance."""
        E_in = self.quanta.total_energy()
        lhs = self.E_initial + self.E_injected_total
        rhs = E_in + self.E_exported_total
        scale = max(abs(lhs), 1.0)
        err = abs(lhs - rhs)
        if err > self.tol * scale:
            raise ConservationViolation(
                f"Energy conservation violated at tick {self.tick_count}: "
                f"E_initial({self.E_initial}) + E_injected({self.E_injected_total}) "
                f"= {lhs}; E_in_quanta({E_in}) + E_exported({self.E_exported_total}) "
                f"= {rhs}; diff={err}, tol={self.tol * scale}"
            )

    def step(self) -> None:
        self.tick_count += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_audit.py -v`
Expected: all 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/audit.py tests/flux/test_audit.py
git commit -m "flux F0 task 7: EnergyAuditor

Tracks E_initial, E_injected_total, E_exported_total. .check()
asserts conservation, raises ConservationViolation on imbalance
beyond tol*scale. Per spec §3: failed audit halts the run.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: T1 Conservation integration test

**Files:**
- Create: `tests/flux/test_conservation.py`

This is the Phase-1 T1 acceptance test from the spec §7.

- [ ] **Step 1: Write failing test `tests/flux/test_conservation.py`**

```python
"""T1 — Energy conservation under 1000 ticks of constant injection.

Spec §7 T1: |E_initial + E_injected - (E_free + E_exported)| <
  1e-9 * max(|E_injected|, 1.0)

This is the F0 acceptance test. When this passes, F0 is done.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick


def test_T1_conservation_over_1000_ticks():
    """Run 1000 ticks of constant injection on a 10×10×10 cube.

    Each tick injects 5 quanta of energy 1.0 each at the hot floor.
    Absorbing cold ceiling + side walls take the rest.
    Conservation must hold within tolerance for every tick AND at end.
    """
    rng = np.random.default_rng(42)
    q = Quanta(max_quanta=20_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 1000
    DT = 0.1

    def injector(quanta, grid):
        injected_count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=200.0,
            vel_z_mean=2.0,
            rng=rng,
        )
        audit.record_injection(injected_count * ENERGY_PER)
        return injected_count * ENERGY_PER

    for _ in range(N_TICKS):
        exported = tick(q, g, dt=DT, injector=injector)
        audit.record_export(exported)
        audit.check()  # Per-tick assertion
        audit.step()

    # Final check (already covered by per-tick, but explicit here)
    audit.check()

    # Sanity: some energy was injected, some exported, some still in
    # the buffer (or all exported if cube is very leaky)
    E_in = q.total_energy()
    assert audit.E_injected_total > 0
    assert audit.E_injected_total <= N_TICKS * QUANTA_PER_TICK * ENERGY_PER
    assert E_in >= 0
    assert audit.E_exported_total >= 0
    # The accounting equation
    np.testing.assert_allclose(
        audit.E_initial + audit.E_injected_total,
        E_in + audit.E_exported_total,
        rtol=0, atol=1e-9 * max(audit.E_injected_total, 1.0),
    )


def test_T1_conservation_zero_injection_zero_export():
    """Empty cube + no injection → nothing changes."""
    q = Quanta(max_quanta=100)
    g = Grid(dims=(5, 5, 5))
    audit = EnergyAuditor(quanta=q, tol=1e-9)
    audit.record_initial()
    for _ in range(100):
        exported = tick(q, g, dt=0.1, injector=None)
        audit.record_export(exported)
        audit.check()
        audit.step()
    assert audit.E_injected_total == 0.0
    assert audit.E_exported_total == 0.0
    assert q.total_energy() == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_conservation.py -v`
Expected: fails or errors only if any module is missing. Once tasks 1–7 are done, this test should pass without any new implementation. If it fails for a logic reason (e.g., conservation violation), debug the contributing module — do not modify the test thresholds.

- [ ] **Step 3: Make it pass without modifying the test**

If the test fails, the failure indicates a bug in one of: `quantum.py`, `boundary.py`, `dynamics.py`, or `audit.py`. Common suspects:
- `absorb_cold_faces` removing a vibration but not adding its energy to `exported`
- `tick` injector returning wrong injected count
- Re-using a slot that still had non-zero energy (Quanta.add)

Trace energy from injection through motion to export. The bug is wherever the running sum diverges.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_conservation.py -v`
Expected: both tests PASS.

Run all flux tests to confirm no regression:
Run: `uv run pytest tests/flux/ -v`
Expected: all flux tests PASS (no count assertion — depends on how many test cases got added). Should be roughly 25–30 passing.

- [ ] **Step 5: Commit**

```bash
git add tests/flux/test_conservation.py
git commit -m "flux F0 task 8: T1 conservation integration test

Runs 1000 ticks under constant injection on a 10x10x10 cube,
asserts conservation per tick and at end. This is the F0 acceptance
test — F0 is done when this passes.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: README update — name the two substrates

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Locate the insertion point in `README.md`**

Find the line that ends the "What runs today" section (after the test count + verification line, around line 98 in the current file). The insertion is a new paragraph block between "What runs today" and "## The four research-grounded amendments of May 2026".

- [ ] **Step 2: Add the "Two substrates" paragraph to `README.md`**

After this existing block:

```markdown
Total suite: **313 non-slow tests + 22 slow tests passing**. Verified on macOS-arm64 (Python 3.13.12) and Linux-x86_64 CI.

---
```

Insert (preserving the trailing `---`):

```markdown
## Two substrates: legacy engineered + flux (in development)

Since 2026-05-10 the repo carries two substrates side by side.

- **Legacy** (`world/`, `agent/`) — the engineered six-level binding rule set documented throughout this README. Honest scope as of 2026-05-10: single-pattern recall works (M4 contract A+B); G19 predictive-babble falsifier returned FAIL on the first real-corpus run with z-scores statistically indistinguishable from white noise; the README has been corrected (commit `d83b82c`) to remove overclaims and document the FAIL.
- **Flux** (`world/flux/`, `agent/flux/`) — the project's actual scientific bet. A substrate where the six engineered levels are replaced by one principle: energy quanta flow through an open boundary, structures kondensieren wo sie diesen Fluss effizienter kanalisieren, learning is reconfiguration toward more efficient flux channelling. Spec: [`docs/superpowers/specs/2026-05-10-flux-substrate-design.md`](docs/superpowers/specs/2026-05-10-flux-substrate-design.md). Status as of 2026-05-10: F0 in progress (skeleton + energy-conservation audit); F1–F6 roadmap pre-registered with Tier 2 falsifier as obligation and Tier 3 as stretch.

The two substrates do not share state. The legacy substrate remains runnable as the comparison baseline; the flux substrate carries the unprejudiced learning hypothesis.

---
```

- [ ] **Step 3: Verify the README still renders sensibly**

Run: `uv run python -c "import markdown; markdown.markdown(open('README.md').read())"` (or just open in a markdown viewer)
Expected: no exceptions, no obvious formatting breakage.

Then visually scan the README from the changed section: the new block should sit between "Total suite: ..." and "## The four research-grounded amendments of May 2026". The amendments section title and content must still appear correctly after.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "flux F0 task 9: README names the two substrates

Adds a section after 'What runs today' that points at both world/
(legacy, engineered, G19 FAIL) and world/flux/ (in development,
flux-driven, F0 underway). Spec linked.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## F0 Done-criterion

F0 is closed when **all** of the following hold:

- `uv run pytest tests/flux/ -v` passes with zero failures
- `uv run pytest tests/flux/test_conservation.py -v` (the explicit T1 acceptance test) passes
- `git log --oneline | head -10` shows 9 commits with `flux F0 task N:` prefix
- README mentions both substrates
- `docs/flux/phase-log.md` exists and notes F0 start

Next plan: `docs/superpowers/plans/2026-MM-DD-flux-substrate-F1.md` covering binding rule + structures + T2 + T3 + T4.

---

## Notes for the engineer implementing this

- **No Numba in F0.** The motion loop is simple and the scale is small. Premature JIT compilation slows down iteration without measurable gain at 10×10×10 with 1000 vibrations.
- **No structures yet.** No Node, no Bridge, no graph. Just free vibrations + boundary + audit. F1 introduces structures.
- **Conservation is mandatory.** If T1 fails, the bug is in *your* code — do not loosen the tolerance, do not modify the test. The test enforces the spec contract; if you weaken the test, you weaken the contract.
- **Style matches legacy EQMOD.** Struct-of-arrays, `np.float64` for position/velocity/energy, `np.bool_` for alive flags. See `world/state.py` for the legacy `World` class — note the `s_pos`, `s_vel`, `s_alive` naming convention. The flux substrate uses `pos`, `vel`, `alive` (no prefix) because there's no namespace collision in `world/flux/`.
- **No new dependencies.** numpy + pytest only.
- **Commit after every task.** Nine commits total for F0. If a step fails, fix it before committing — do not commit a broken intermediate state.
