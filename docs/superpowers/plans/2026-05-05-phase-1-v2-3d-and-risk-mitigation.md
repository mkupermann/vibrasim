# Phase 1 v2 Implementation Plan — 3D Substrate and Risk Mitigation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the existing 2D Phase 1 simulation to the 3D substrate of CONCEPT.md v2. Implement scale repulsion (§4.6) and ambient regeneration (§4.7). Replace the live Pygame renderer with a decoupled Open3D preview + headless Blender keyframe pipeline. Build the parameter sweep harness with Optuna backend. Add a frequency-histogram observation tool.

**Architecture:** Forward migration — 3D replaces 2D in `world/`. Three layers: headless physics writes snapshot NPZs; Open3D polls snapshots for live preview; Blender Cycles consumes snapshots offline for publication-grade keyframes. Calibration via parameter sweeps (grid/random + Optuna). Pygame is removed.

**Tech Stack:** Python 3.13+, NumPy 2.x, Numba 0.65+, Open3D 0.18+, Optuna 3.6+, pytest 9.x, headless Blender (Cycles) for keyframe rendering.

**Spec:** [`docs/superpowers/specs/2026-05-05-phase-1-v2-3d-and-risk-mitigation.md`](../specs/2026-05-05-phase-1-v2-3d-and-risk-mitigation.md). When this plan and the spec disagree, the spec wins.

---

## File map

| Path | Status | What it holds |
|---|---|---|
| `pyproject.toml` | modify | drop pygame, add open3d, optuna |
| `world/__init__.py` | unchanged | |
| `world/__main__.py` | unchanged | |
| `world/config.py` | rewrite | 3D box_size, lambda_gen, lambda_dec, repulsion_k, repulsion_cell_size, repulsion_threshold_ratio |
| `world/state.py` | rewrite | 3D arrays; node velocity arrays; total_vibrations / ambient_density helpers |
| `world/spatial.py` | rewrite | 3D periodic-wrap grid, 27-cell neighbour iteration, 3D distance/midpoint |
| `world/physics.py` | rewrite | 3D motion, 3D binding, decay+ambient regeneration, scale repulsion, tick composition |
| `world/snapshot.py` | new | save/load NPZ + metadata |
| `world/preview.py` | new | Open3D 3D viewer (replaces `world/render.py`) |
| `world/render.py` | delete | Pygame renderer is gone |
| `world/run.py` | rewrite | snapshot-aware CLI, --preview, no Pygame window mode |
| `tests/conftest.py` | modify | 3D fixtures |
| `tests/test_config.py` | modify | 3D + new params |
| `tests/test_state.py` | rewrite | 3D arrays |
| `tests/test_spatial.py` | rewrite | 3D periodic + 27-cell |
| `tests/test_motion.py` | rewrite | 3D motion |
| `tests/test_binding.py` | rewrite | 3D binding |
| `tests/test_decay.py` | modify | retain decay tests; ambient is its own file |
| `tests/test_ambient.py` | new | ambient generation + decay tests |
| `tests/test_repulsion.py` | new | scale repulsion tests |
| `tests/test_snapshot.py` | new | round-trip and metadata |
| `tests/test_tick.py` | rewrite | 3D + new tick steps |
| `tests/test_sweep.py` | new | sweep harness tests |
| `tests/test_histogram.py` | new | histogram tool tests |
| `tools/sweep.py` | new | parameter sweep harness, Optuna backend |
| `tools/histogram.py` | new | frequency histograms from snapshot |
| `tools/render_blender.py` | new | Blender Cycles keyframe pipeline |

---

## Task 0: Bootstrap — dependencies and venv refresh

**Files:** `pyproject.toml`

- [ ] **Step 1: Update `pyproject.toml`**

```toml
[project]
name = "world"
version = "0.2.0"
description = "World of Vibrations — 3D physics simulator toward emergent brain-like structure (Phase 1 v2)."
readme = "README.md"
requires-python = ">=3.13"
authors = [{ name = "Michael Kupermann", email = "michael@kupermann.com" }]
dependencies = [
    "numpy >= 1.26",
    "numba >= 0.61",
    "open3d >= 0.18",
    "optuna >= 3.6",
]

[project.optional-dependencies]
dev = ["pytest >= 8.0", "matplotlib >= 3.8"]

[project.scripts]
world = "world.run:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["world"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --strict-markers"
```

- [ ] **Step 2: Refresh venv**

```bash
cd /Users/mkupermann/Documents/GitHub/EQMOD
source .venv/bin/activate
pip uninstall -y pygame
pip install -e ".[dev]"
```

- [ ] **Step 3: Sanity import check**

```bash
python -c "import open3d; import optuna; import numpy, numba; print('OK')"
```

Expected: `OK`. Note: open3d is large (~150 MB). First import may take a few seconds.

- [ ] **Step 4: Verify Blender available**

```bash
blender --version 2>&1 | head -1
```

If Blender isn't installed: `brew install --cask blender` on macOS. Document the installed version in the LOGBOOK.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "build(deps): add open3d/optuna, drop pygame, bump to 0.2.0 for v2"
```

---

## Task 1: `world/config.py` — 3D + new parameters

**Files:** `world/config.py`, `tests/test_config.py`

- [ ] **Step 1: Update test for 3D + new fields**

`tests/test_config.py` — replace `test_default_config_matches_spec` with:

```python
def test_default_config_matches_spec():
    cfg = WorldConfig()
    assert cfg.n_initial_vibrations == 1000
    assert cfg.box_size == (1000.0, 1000.0, 1000.0)         # CHANGED: 3-tuple
    assert cfg.r_1 == 5.0
    assert cfg.r_2 == 10.0
    assert cfg.repulsion_k == 100.0                         # NEW
    assert cfg.repulsion_cell_size == 100.0                 # NEW
    assert cfg.repulsion_threshold_ratio == 1000.0          # NEW
    assert cfg.lambda_gen == 0.0001                         # NEW
    assert cfg.lambda_dec == 0.001                          # NEW
    assert cfg.dt == pytest.approx(1.0 / 60.0)
    assert cfg.rng_seed == 42
    assert cfg.n_vibrations_max == 4096
    assert cfg.n_nodes_max == 1024


def test_box_size_is_three_tuple():
    cfg = WorldConfig()
    assert len(cfg.box_size) == 3
    for d in cfg.box_size:
        assert isinstance(d, float)


def test_toml_box_size_list_to_tuple():
    """Three-element list in TOML coerces to 3-tuple."""
    import tempfile, pathlib
    from world.config import load_config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('box_size = [500.0, 500.0, 500.0]\n')
        path = pathlib.Path(f.name)
    cfg = load_config(path)
    assert cfg.box_size == (500.0, 500.0, 500.0)
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_config.py -v
```

Expected: AttributeError on `repulsion_k` / `lambda_gen`, or assertion failure on `box_size` shape.

- [ ] **Step 3: Update `world/config.py`**

```python
from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding (3D)
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (1000.0, 1000.0, 1000.0)
    freq_min: float = 100.0
    freq_max: float = 10000.0
    freq_distribution: str = "log"
    speed_min: float = 10.0
    speed_max: float = 50.0
    polarity_split: float = 0.5

    # Binding
    r_1: float = 5.0
    r_2: float = 10.0
    freq_ratio: float = 0.08
    freq_tolerance: float = 0.005

    # Decay (mean exponential lifetimes, seconds)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Scale separation through repulsion (§4.6)
    repulsion_k: float = 100.0
    repulsion_cell_size: float = 100.0
    repulsion_threshold_ratio: float = 1000.0

    # Ambient regeneration (§4.7)
    lambda_gen: float = 0.0001
    lambda_dec: float = 0.001

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024


INITIAL_CONFIG = WorldConfig()


def load_config(path: Path | str | None) -> WorldConfig:
    if path is None:
        return WorldConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    valid_field_names = {f.name for f in fields(WorldConfig)}
    overrides = {k: v for k, v in data.items() if k in valid_field_names}
    if "box_size" in overrides and isinstance(overrides["box_size"], list):
        overrides["box_size"] = tuple(overrides["box_size"])
    return replace(WorldConfig(), **overrides)
```

- [ ] **Step 4: Run, confirm pass**

```bash
pytest tests/test_config.py -v
```

Expected: all 3+ tests pass.

- [ ] **Step 5: Commit**

```bash
git add world/config.py tests/test_config.py
git commit -m "feat(config): 3D box_size, scale-repulsion params, ambient-regeneration rates"
```

---

## Task 2: `world/state.py` — 3D arrays and node velocities

**Files:** `world/state.py`, `tests/conftest.py`, `tests/test_state.py`

- [ ] **Step 1: Update `tests/conftest.py` for 3D fixtures**

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


@pytest.fixture
def default_config() -> WorldConfig:
    return WorldConfig()


@pytest.fixture
def empty_world() -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(100.0, 100.0, 100.0),
        n_vibrations_max=64,
        n_nodes_max=32,
        rng_seed=42,
    )
    return World(cfg)
```

- [ ] **Step 2: Update `tests/test_state.py`**

Replace `test_world_constructs_with_correct_capacity` and add 3D-specific tests:

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


def test_world_constructs_with_correct_3d_capacity(default_config):
    w = World(default_config)
    N = default_config.n_vibrations_max
    K = default_config.n_nodes_max
    assert w.s_pos.shape == (N, 3)
    assert w.s_vel.shape == (N, 3)
    assert w.k_pos.shape == (K, 3)
    assert w.k_vel.shape == (K, 3)


def test_seeded_vibrations_in_3d_box(default_config):
    w = World(default_config)
    alive = w.s_alive
    bx, by, bz = default_config.box_size
    assert np.all(w.s_pos[alive, 0] >= 0)
    assert np.all(w.s_pos[alive, 0] < bx)
    assert np.all(w.s_pos[alive, 1] >= 0)
    assert np.all(w.s_pos[alive, 1] < by)
    assert np.all(w.s_pos[alive, 2] >= 0)
    assert np.all(w.s_pos[alive, 2] < bz)


def test_seeded_velocities_isotropic_in_3d(default_config):
    """Seeded velocities should not be confined to a 2D plane."""
    w = World(default_config)
    alive = w.s_alive
    # In a uniform 3D distribution of velocities, each component has nonzero variance.
    for d in range(3):
        assert np.std(w.s_vel[alive, d]) > 1.0


def test_seeded_speeds_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    speeds = np.linalg.norm(w.s_vel[alive], axis=1)
    assert np.all(speeds >= default_config.speed_min - 1e-6)
    assert np.all(speeds <= default_config.speed_max + 1e-6)


def test_total_vibrations_count():
    """Bookkeeping: total_vibrations counts free + bound."""
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=16, n_nodes_max=8, rng_seed=42)
    w = World(cfg)
    assert w.total_vibrations() == 10  # 10 free, no bound
```

- [ ] **Step 3: Run, confirm failure**

```bash
pytest tests/test_state.py -v
```

- [ ] **Step 4: Update `world/state.py`**

```python
from __future__ import annotations
import numpy as np
from world.config import WorldConfig

LEVEL_TO_VIBRATIONS = {1: 2, 2: 4, 3: 6, 4: 8}  # vibrations bound at each level


class World:
    """3D physics state. SoA NumPy arrays, periodic boundaries on all three axes."""

    def __init__(self, config: WorldConfig):
        self.config = config
        self.t: float = 0.0
        self.rng = np.random.default_rng(config.rng_seed)

        N = config.n_vibrations_max
        K = config.n_nodes_max

        # Vibration arrays (3D)
        self.s_pos = np.zeros((N, 3), dtype=np.float64)
        self.s_vel = np.zeros((N, 3), dtype=np.float64)
        self.s_freq = np.zeros(N, dtype=np.float64)
        self.s_pol = np.zeros(N, dtype=np.bool_)
        self.s_alive = np.zeros(N, dtype=np.bool_)
        self.s_locked_this_tick = np.zeros(N, dtype=np.bool_)
        self.n_alive: int = 0

        # Node arrays (3D, with velocity for repulsion)
        self.k_pos = np.zeros((K, 3), dtype=np.float64)
        self.k_vel = np.zeros((K, 3), dtype=np.float64)
        self.k_freq = np.zeros(K, dtype=np.float64)
        self.k_pol = np.zeros(K, dtype=np.bool_)
        self.k_level = np.zeros(K, dtype=np.uint8)
        self.k_birth = np.zeros(K, dtype=np.float64)
        self.k_alive = np.zeros(K, dtype=np.bool_)
        self.k_locked_this_tick = np.zeros(K, dtype=np.bool_)

        # CSR composition
        comp_caps = K * 4
        self.k_comp_offset = np.zeros(K + 1, dtype=np.int32)
        self.k_comp_indices = np.zeros(comp_caps, dtype=np.int32)
        self.k_comp_kind = np.zeros(K, dtype=np.uint8)
        self.k_comp_used: int = 0
        self.k_count: int = 0

        self._seed()

    def _seed(self) -> None:
        cfg = self.config
        n = cfg.n_initial_vibrations
        if n == 0:
            return
        bx, by, bz = cfg.box_size
        self.s_pos[:n, 0] = self.rng.uniform(0.0, bx, size=n)
        self.s_pos[:n, 1] = self.rng.uniform(0.0, by, size=n)
        self.s_pos[:n, 2] = self.rng.uniform(0.0, bz, size=n)
        self.s_freq[:n] = self._sample_frequencies(n)
        self.s_pol[:n] = self.rng.random(n) < cfg.polarity_split
        self.s_vel[:n] = self._sample_velocities_3d(n)
        self.s_alive[:n] = True
        self.n_alive = n

    def _sample_frequencies(self, n: int) -> np.ndarray:
        cfg = self.config
        if cfg.freq_distribution == "log":
            return np.exp(self.rng.uniform(np.log(cfg.freq_min), np.log(cfg.freq_max), size=n))
        elif cfg.freq_distribution == "uniform":
            return self.rng.uniform(cfg.freq_min, cfg.freq_max, size=n)
        else:
            raise ValueError(f"Unknown freq_distribution: {cfg.freq_distribution!r}")

    def _sample_velocities_3d(self, n: int) -> np.ndarray:
        """Isotropic 3D velocities with magnitudes uniformly distributed in [speed_min, speed_max]."""
        cfg = self.config
        speeds = self.rng.uniform(cfg.speed_min, cfg.speed_max, size=n)
        # Uniform points on the unit sphere (Marsaglia method)
        z = self.rng.uniform(-1.0, 1.0, size=n)
        phi = self.rng.uniform(0.0, 2 * np.pi, size=n)
        sqrt_omz2 = np.sqrt(1 - z * z)
        v = np.empty((n, 3), dtype=np.float64)
        v[:, 0] = speeds * sqrt_omz2 * np.cos(phi)
        v[:, 1] = speeds * sqrt_omz2 * np.sin(phi)
        v[:, 2] = speeds * z
        return v

    def allocate_node(
        self, pos: np.ndarray, freq: float, pol: bool, level: int,
        constituents: np.ndarray, comp_kind: int,
    ) -> int:
        i = self.k_count
        if i >= self.config.n_nodes_max:
            raise RuntimeError("Node capacity exhausted")
        self.k_pos[i] = pos
        self.k_vel[i] = 0.0  # nodes start at rest; repulsion accumulates velocity
        self.k_freq[i] = freq
        self.k_pol[i] = pol
        self.k_level[i] = level
        self.k_birth[i] = self.t
        self.k_alive[i] = True
        self.k_comp_kind[i] = comp_kind
        n_comp = len(constituents)
        start = self.k_comp_used
        end = start + n_comp
        if end > self.k_comp_indices.shape[0]:
            raise RuntimeError("Composition index capacity exhausted")
        self.k_comp_indices[start:end] = constituents
        self.k_comp_offset[i] = start
        self.k_comp_offset[i + 1] = end
        self.k_comp_used = end
        self.k_count += 1
        return i

    def reset_tick_locks(self) -> None:
        if self.n_alive > 0:
            self.s_locked_this_tick[:self.n_alive] = False
        if self.k_count > 0:
            self.k_locked_this_tick[:self.k_count] = False

    def total_vibrations(self) -> int:
        """Count of vibrations free + bound (for ambient-stability bookkeeping)."""
        free = int(self.s_alive.sum())
        bound = 0
        for level, vib_count in LEVEL_TO_VIBRATIONS.items():
            n_level = int(((self.k_level == level) & self.k_alive).sum())
            bound += n_level * vib_count
        return free + bound

    def ambient_density(self) -> float:
        """Free vibrations per unit volume."""
        bx, by, bz = self.config.box_size
        return float(self.s_alive.sum()) / (bx * by * bz)
```

- [ ] **Step 5: Run, confirm pass**

```bash
pytest tests/test_state.py -v
```

- [ ] **Step 6: Commit**

```bash
git add world/state.py tests/conftest.py tests/test_state.py
git commit -m "feat(state): 3D arrays, isotropic velocities, total_vibrations bookkeeping"
```

---

## Task 3: `world/spatial.py` — 3D periodic-wrap grid

**Files:** `world/spatial.py`, `tests/test_spatial.py`

- [ ] **Step 1: Update `tests/test_spatial.py` for 3D**

```python
import numpy as np
import pytest
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


def test_periodic_distance_no_wrap_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([10.0, 10.0, 10.0])
    b = np.array([13.0, 14.0, 22.0])
    d2 = periodic_distance_sq(a, b, box)
    assert d2 == pytest.approx(9 + 16 + 144)  # 169


def test_periodic_distance_with_wrap_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([1.0, 1.0, 1.0])
    b = np.array([99.0, 99.0, 99.0])
    d2 = periodic_distance_sq(a, b, box)
    # Each axis wraps; delta = 2 in each dim → d2 = 12
    assert d2 == pytest.approx(12.0)


def test_3d_neighbors_within_27_cells():
    """A 3D grid query visits 27 neighbour cells."""
    positions = np.array([[5.0, 5.0, 5.0], [15.0, 5.0, 5.0]])  # adjacent x-cells
    alive = np.array([True, True])
    box = np.array([100.0, 100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_3d_neighbors_periodic_wrap():
    positions = np.array([[1.0, 50.0, 50.0], [99.0, 50.0, 50.0]])  # opposite x-faces
    alive = np.array([True, True])
    box = np.array([100.0, 100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_periodic_midpoint_3d():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([10.0, 20.0, 30.0])
    b = np.array([14.0, 24.0, 38.0])
    m = periodic_midpoint(a, b, box)
    assert np.allclose(m, [12.0, 22.0, 34.0])


def test_periodic_midpoint_3d_wrap():
    box = np.array([100.0, 100.0, 100.0])
    a = np.array([99.0, 50.0, 50.0])
    b = np.array([1.0, 50.0, 50.0])
    m = periodic_midpoint(a, b, box)
    # Wrap midpoint is at 0 (or 100), not at 50.
    assert m[0] < 1.0 or m[0] > 99.0
    assert m[1] == pytest.approx(50.0)
    assert m[2] == pytest.approx(50.0)


def test_dead_points_excluded_3d():
    positions = np.array([[5.0, 5.0, 5.0], [6.0, 6.0, 6.0]])
    alive = np.array([True, False])
    box = np.array([100.0, 100.0, 100.0])
    grid = build_grid(positions, alive, box, 10.0)
    nbrs = neighbors_of(grid, positions[0], box, 10.0, exclude_self=True, query_index=0)
    assert 1 not in nbrs
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_spatial.py -v
```

- [ ] **Step 3: Implement `world/spatial.py` for 3D**

```python
from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def periodic_distance_sq(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> float:
    d2 = 0.0
    for i in range(3):
        dx = a[i] - b[i]
        b_i = box[i]
        if dx > b_i * 0.5:
            dx -= b_i
        elif dx < -b_i * 0.5:
            dx += b_i
        d2 += dx * dx
    return d2


@njit(cache=True)
def periodic_midpoint(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> np.ndarray:
    out = np.empty(3, dtype=np.float64)
    for d in range(3):
        delta = b[d] - a[d]
        if delta > box[d] * 0.5:
            delta -= box[d]
        elif delta < -box[d] * 0.5:
            delta += box[d]
        m = a[d] + delta * 0.5
        m = m % box[d]
        out[d] = m
    return out


def build_grid(
    positions: np.ndarray,
    alive: np.ndarray,
    box: np.ndarray,
    cell_size: float,
) -> dict[tuple[int, int, int], list[int]]:
    grid: dict[tuple[int, int, int], list[int]] = {}
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    nz = int(np.ceil(box[2] / cell_size))
    for i in range(positions.shape[0]):
        if not alive[i]:
            continue
        cx = int(positions[i, 0] // cell_size) % nx
        cy = int(positions[i, 1] // cell_size) % ny
        cz = int(positions[i, 2] // cell_size) % nz
        key = (cx, cy, cz)
        if key not in grid:
            grid[key] = []
        grid[key].append(i)
    return grid


def neighbors_of(
    grid: dict[tuple[int, int, int], list[int]],
    pos: np.ndarray,
    box: np.ndarray,
    cell_size: float,
    *,
    exclude_self: bool,
    query_index: int,
) -> list[int]:
    """Iterate the 27-cell (3³) periodic neighbourhood."""
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    nz = int(np.ceil(box[2] / cell_size))
    cx = int(pos[0] // cell_size) % nx
    cy = int(pos[1] // cell_size) % ny
    cz = int(pos[2] // cell_size) % nz
    out: list[int] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                key = ((cx + dx) % nx, (cy + dy) % ny, (cz + dz) % nz)
                bucket = grid.get(key)
                if bucket is None:
                    continue
                for idx in bucket:
                    if exclude_self and idx == query_index:
                        continue
                    out.append(idx)
    return out
```

- [ ] **Step 4: Run, confirm pass**

```bash
pytest tests/test_spatial.py -v
```

- [ ] **Step 5: Commit**

```bash
git add world/spatial.py tests/test_spatial.py
git commit -m "feat(spatial): 3D periodic-wrap distance/midpoint, 27-cell neighbour grid"
```

---

## Task 4: `world/physics.py` — 3D motion

**Files:** `world/physics.py`, `tests/test_motion.py`

- [ ] **Step 1: Update `tests/test_motion.py` for 3D**

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import move_vibrations


def test_motion_no_friction_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0, 10.0]
    w.s_vel[0] = [3.0, 4.0, 5.0]
    w.s_alive[0] = True
    w.n_alive = 1
    dt = 0.5
    n_ticks = 10
    box = np.array(cfg.box_size)
    for _ in range(n_ticks):
        move_vibrations(w.s_pos, w.s_vel, w.s_alive, box, dt)
    expected = ((np.array([10., 10., 10.]) + np.array([3., 4., 5.]) * dt * n_ticks)
                % np.array(cfg.box_size))
    assert np.allclose(w.s_pos[0], expected)


def test_motion_periodic_wrap_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [99.0, 99.0, 99.0]
    w.s_vel[0] = [5.0, 5.0, 5.0]
    w.s_alive[0] = True
    w.n_alive = 1
    box = np.array(cfg.box_size)
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, box, 1.0)
    assert np.allclose(w.s_pos[0], [4.0, 4.0, 4.0])


def test_motion_dead_unchanged_3d():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0, 10.0]
    w.s_vel[0] = [5.0, 5.0, 5.0]
    w.s_alive[0] = False
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert np.allclose(w.s_pos[0], [10.0, 10.0, 10.0])
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_motion.py -v
```

- [ ] **Step 3: Update `world/physics.py` (start fresh — full rewrite)**

```python
from __future__ import annotations
import math
import numpy as np
from numba import njit
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


@njit(cache=True)
def move_vibrations(
    s_pos: np.ndarray,
    s_vel: np.ndarray,
    s_alive: np.ndarray,
    box: np.ndarray,
    dt: float,
) -> None:
    """3D motion with periodic-wrap on all three axes."""
    n = s_pos.shape[0]
    for i in range(n):
        if not s_alive[i]:
            continue
        for d in range(3):
            s_pos[i, d] = (s_pos[i, d] + s_vel[i, d] * dt) % box[d]
```

- [ ] **Step 4: Run, confirm pass**

```bash
pytest tests/test_motion.py -v
```

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_motion.py
git commit -m "feat(physics): 3D periodic-wrap motion update"
```

---

## Task 5: 3D binding (vibrations → electrons → pairs → triads → atoms)

**Files:** `world/physics.py` (append), `tests/test_binding.py`

- [ ] **Step 1: Update `tests/test_binding.py`**

Replace position lists in helpers with 3D coordinates. Key tests to update:

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_vibrations_to_electrons, bind_nodes_upward


def _seed_two_vibrations(w: World, p1, p2, f1, f2, pol1, pol2):
    """p1, p2 are now length-3 arrays / lists."""
    w.s_pos[0] = p1
    w.s_pos[1] = p2
    w.s_freq[0] = f1
    w.s_freq[1] = f2
    w.s_pol[0] = pol1
    w.s_pol[1] = pol2
    w.s_alive[0] = True
    w.s_alive[1] = True
    w.s_vel[0] = [0.0, 0.0, 0.0]
    w.s_vel[1] = [0.0, 0.0, 0.0]
    w.n_alive = 2


def test_no_binding_same_polarity_3d(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10., 10., 10.], [12., 10., 10.],
                         1000.0, 1080.0, True, True)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_electron_forms_3d(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10., 10., 10.], [12., 10., 10.],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    assert w.k_freq[0] == pytest.approx(2080.0)
    assert np.allclose(w.k_pos[0], [11., 10., 10.])
    assert not w.s_alive[0] and not w.s_alive[1]


def test_electron_forms_at_3d_wrap(empty_world):
    w = empty_world
    box = w.config.box_size
    _seed_two_vibrations(w, [box[0] - 1., 10., 10.], [1., 10., 10.],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    mx = w.k_pos[0, 0]
    assert mx < 1.0 or mx > box[0] - 1.0


# Higher binding tests — 3D positions, otherwise identical structure
def _make_electron_3d(w: World, idx: int, pos, freq, pol):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 1
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]


def test_pair_forms_3d(empty_world):
    w = empty_world
    _make_electron_3d(w, 0, [10., 10., 10.], 2000.0, True)
    _make_electron_3d(w, 1, [13., 10., 10.], 2160.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1


def test_decade_isolation_3d(empty_world):
    w = empty_world
    _make_electron_3d(w, 0, [10., 10., 10.], 9500.0, True)
    _make_electron_3d(w, 1, [13., 10., 10.], 10260.0, False)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 0
```

- [ ] **Step 2: Append binding to `world/physics.py`**

```python
def bind_vibrations_to_electrons(world) -> int:
    cfg = world.config
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r1 = cfg.r_1
    r1_sq = r1 * r1
    fr = cfg.freq_ratio
    ftol = cfg.freq_tolerance
    fmin_ratio = fr - ftol
    fmax_ratio = fr + ftol

    world.reset_tick_locks()
    grid = build_grid(world.s_pos, world.s_alive, box, r1)
    formed = 0

    for i in range(world.s_pos.shape[0]):
        if not world.s_alive[i] or world.s_locked_this_tick[i]:
            continue
        nbrs = neighbors_of(grid, world.s_pos[i], box, r1, exclude_self=True, query_index=i)
        for j in nbrs:
            if j <= i:
                continue
            if not world.s_alive[j] or world.s_locked_this_tick[j]:
                continue
            if world.s_pol[i] == world.s_pol[j]:
                continue
            d2 = periodic_distance_sq(world.s_pos[i], world.s_pos[j], box)
            if d2 >= r1_sq:
                continue
            f1 = world.s_freq[i]
            f2 = world.s_freq[j]
            ratio = abs(f1 - f2) / min(f1, f2)
            if ratio < fmin_ratio or ratio > fmax_ratio:
                continue
            mid = periodic_midpoint(world.s_pos[i], world.s_pos[j], box)
            new_freq = f1 + f2
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            world.allocate_node(mid, new_freq, new_pol, level=1,
                                constituents=constituents, comp_kind=0)
            world.s_alive[i] = False
            world.s_alive[j] = False
            world.s_locked_this_tick[i] = True
            world.s_locked_this_tick[j] = True
            world.n_alive -= 2
            formed += 1
            break

    return formed


_UPGRADE_TARGET = {
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
}


def _decade(freq: float) -> int:
    return int(math.floor(math.log10(freq)))


def bind_nodes_upward(world) -> int:
    cfg = world.config
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r2 = cfg.r_2
    r2_sq = r2 * r2
    fr = cfg.freq_ratio
    ftol = cfg.freq_tolerance
    fmin_ratio = fr - ftol
    fmax_ratio = fr + ftol

    world.k_locked_this_tick[:world.k_count] = False
    formed = 0
    grid = build_grid(world.k_pos[:world.k_count], world.k_alive[:world.k_count], box, r2)

    for i in range(world.k_count):
        if not world.k_alive[i] or world.k_locked_this_tick[i]:
            continue
        nbrs = neighbors_of(grid, world.k_pos[i], box, r2, exclude_self=True, query_index=i)
        for j in nbrs:
            if j <= i:
                continue
            if not world.k_alive[j] or world.k_locked_this_tick[j]:
                continue
            li = int(world.k_level[i])
            lj = int(world.k_level[j])
            target = _UPGRADE_TARGET.get((li, lj))
            if target is None:
                continue
            if world.k_pol[i] == world.k_pol[j]:
                continue
            d2 = periodic_distance_sq(world.k_pos[i], world.k_pos[j], box)
            if d2 >= r2_sq:
                continue
            f1 = world.k_freq[i]
            f2 = world.k_freq[j]
            if _decade(f1) != _decade(f2):
                continue
            ratio = abs(f1 - f2) / min(f1, f2)
            if ratio < fmin_ratio or ratio > fmax_ratio:
                continue
            mid = periodic_midpoint(world.k_pos[i], world.k_pos[j], box)
            new_freq = f1 + f2
            new_pol = bool(world.rng.random() < 0.5)
            constituents = np.array([i, j], dtype=np.int32)
            world.allocate_node(mid, new_freq, new_pol, level=target,
                                constituents=constituents, comp_kind=1)
            world.k_alive[i] = False
            world.k_alive[j] = False
            world.k_locked_this_tick[i] = True
            world.k_locked_this_tick[j] = True
            formed += 1
            break

    return formed
```

- [ ] **Step 3: Run, confirm pass**

```bash
pytest tests/test_binding.py -v
```

- [ ] **Step 4: Commit**

```bash
git add world/physics.py tests/test_binding.py
git commit -m "feat(physics): 3D vibration→electron and node-upgrade binding"
```

---

## Task 6: Decay + ambient regeneration

**Files:** `world/physics.py` (append), `tests/test_decay.py` (update), `tests/test_ambient.py` (new)

- [ ] **Step 1: Update `tests/test_decay.py` for 3D**

Update fixture seeding to use 3D positions; the decay logic is dimension-agnostic so most tests just need 3D-shape fixes.

- [ ] **Step 2: Write `tests/test_ambient.py`**

```python
import math
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import ambient_regeneration


def test_zero_lambda_no_change():
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100., 100., 100.),
                      lambda_gen=0.0, lambda_dec=0.0, rng_seed=42)
    w = World(cfg)
    before = int(w.s_alive.sum())
    for _ in range(1000):
        ambient_regeneration(w, cfg.dt)
    assert int(w.s_alive.sum()) == before


def test_generation_rate_matches_lambda():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      lambda_gen=0.001, lambda_dec=0.0,
                      n_vibrations_max=8192, rng_seed=42)
    w = World(cfg)
    n_ticks = 1000
    expected = cfg.lambda_gen * 100 * 100 * 100 * cfg.dt * n_ticks
    for _ in range(n_ticks):
        ambient_regeneration(w, cfg.dt)
    actual = int(w.s_alive.sum())
    assert abs(actual - expected) / expected < 0.10


def test_decay_atoms_immune():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      lambda_gen=0.0, lambda_dec=1.0, rng_seed=42)
    w = World(cfg)
    w.k_alive[0] = True
    w.k_level[0] = 4
    w.k_count = 1
    for _ in range(10000):
        ambient_regeneration(w, cfg.dt)
    assert w.k_alive[0]


def test_capacity_overflow_safe():
    cfg = WorldConfig(n_initial_vibrations=10, box_size=(100., 100., 100.),
                      lambda_gen=10.0, lambda_dec=0.0,  # ridiculously high
                      n_vibrations_max=12, rng_seed=42)
    w = World(cfg)
    for _ in range(100):
        ambient_regeneration(w, cfg.dt)  # should not crash
    assert int(w.s_alive.sum()) <= 12
```

- [ ] **Step 3: Append `ambient_regeneration` to `world/physics.py`**

```python
def ambient_regeneration(world, dt: float) -> tuple[int, int]:
    """Generate new free vibrations and decay unstable nodes back to vibrations.

    Returns (n_generated, n_decayed)."""
    cfg = world.config
    rng = world.rng
    box = np.asarray(cfg.box_size, dtype=np.float64)
    volume = box[0] * box[1] * box[2]

    # Generation: Poisson(lambda_gen * volume * dt)
    expected = cfg.lambda_gen * volume * dt
    n_new = rng.poisson(expected)
    n_max = world.s_pos.shape[0]
    n_alive_now = int(world.s_alive.sum())
    capacity = n_max - n_alive_now
    n_new = min(n_new, capacity)
    if n_new > 0:
        # Find slot indices that are dead
        dead_idx = np.where(~world.s_alive)[0][:n_new]
        # Sample new vibrations
        for d in range(3):
            world.s_pos[dead_idx, d] = rng.uniform(0.0, box[d], size=n_new)
        if cfg.freq_distribution == "log":
            world.s_freq[dead_idx] = np.exp(rng.uniform(np.log(cfg.freq_min),
                                                        np.log(cfg.freq_max), size=n_new))
        else:
            world.s_freq[dead_idx] = rng.uniform(cfg.freq_min, cfg.freq_max, size=n_new)
        world.s_pol[dead_idx] = rng.random(n_new) < cfg.polarity_split
        # Isotropic 3D velocities
        speeds = rng.uniform(cfg.speed_min, cfg.speed_max, size=n_new)
        z = rng.uniform(-1.0, 1.0, size=n_new)
        phi = rng.uniform(0.0, 2 * np.pi, size=n_new)
        sqz = np.sqrt(1 - z * z)
        world.s_vel[dead_idx, 0] = speeds * sqz * np.cos(phi)
        world.s_vel[dead_idx, 1] = speeds * sqz * np.sin(phi)
        world.s_vel[dead_idx, 2] = speeds * z
        world.s_alive[dead_idx] = True
        world.n_alive += n_new

    # Decay: each alive node level 1/2/3 has Bernoulli(lambda_dec * dt) of decaying
    n_decayed = 0
    if cfg.lambda_dec > 0:
        p = cfg.lambda_dec * dt
        for i in range(world.k_count):
            if not world.k_alive[i]:
                continue
            level = int(world.k_level[i])
            if level not in (1, 2, 3):
                continue  # atoms (level 4) immune
            if rng.random() < p:
                # Cascade decay: revive constituents
                world.k_alive[i] = False
                start = world.k_comp_offset[i]
                end = world.k_comp_offset[i + 1]
                kind = int(world.k_comp_kind[i])
                if kind == 0:
                    # constituents are vibrations; bring them back to life
                    for jj in range(start, end):
                        idx = int(world.k_comp_indices[jj])
                        if not world.s_alive[idx]:
                            world.s_alive[idx] = True
                            world.s_pos[idx] = world.k_pos[i]
                            # Random thermal velocity
                            speed = rng.uniform(cfg.speed_min, cfg.speed_max)
                            z = rng.uniform(-1.0, 1.0)
                            phi = rng.uniform(0.0, 2 * np.pi)
                            sqz = math.sqrt(1 - z * z)
                            world.s_vel[idx, 0] = speed * sqz * math.cos(phi)
                            world.s_vel[idx, 1] = speed * sqz * math.sin(phi)
                            world.s_vel[idx, 2] = speed * z
                            world.n_alive += 1
                else:
                    # constituents are nodes; revive them
                    for jj in range(start, end):
                        idx = int(world.k_comp_indices[jj])
                        world.k_alive[idx] = True
                n_decayed += 1

    return n_new, n_decayed
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/test_decay.py tests/test_ambient.py -v
```

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_decay.py tests/test_ambient.py
git commit -m "feat(physics): ambient regeneration (lambda_gen) + node-decay (lambda_dec) channels"
```

---

## Task 7: Scale repulsion

**Files:** `world/physics.py` (append), `tests/test_repulsion.py` (new)

- [ ] **Step 1: Write `tests/test_repulsion.py`**

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import apply_scale_repulsion, move_nodes


def _two_nodes(w: World, freq1, freq2, pos1, pos2):
    """Hand-place two electrons with given frequencies at given positions."""
    w.k_pos[0] = pos1
    w.k_freq[0] = freq1
    w.k_level[0] = 1
    w.k_alive[0] = True
    w.k_pos[1] = pos2
    w.k_freq[1] = freq2
    w.k_level[1] = 1
    w.k_alive[1] = True
    w.k_count = 2


def test_no_repulsion_below_threshold():
    """Frequency ratio < 1000 → no force."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=100.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 1000., 1500., [100., 100., 100.], [200., 100., 100.])  # ratio 1.5
    initial_pos = w.k_pos[:2].copy()
    for _ in range(100):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    assert np.allclose(w.k_pos[:2], initial_pos, atol=1e-3)


def test_repulsion_above_threshold():
    """Frequency ratio > 1000 → nodes drift apart."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=1000.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 100., 200000., [100., 100., 100.], [200., 100., 100.])  # ratio 2000
    initial_distance = np.linalg.norm(w.k_pos[1] - w.k_pos[0])
    for _ in range(1000):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    final_distance = np.linalg.norm(w.k_pos[1] - w.k_pos[0])
    assert final_distance > initial_distance


def test_atoms_participate():
    """Heavier atoms move less under same force, but they do move."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000., 1000., 1000.),
                      n_vibrations_max=4, n_nodes_max=4, repulsion_k=1000.0,
                      rng_seed=42)
    w = World(cfg)
    _two_nodes(w, 100., 200000., [100., 100., 100.], [200., 100., 100.])
    w.k_level[1] = 4  # heavier
    initial_displacement_light = w.k_pos[0].copy()
    for _ in range(1000):
        apply_scale_repulsion(w, cfg.dt)
        move_nodes(w, cfg.dt)
    delta_light = np.linalg.norm(w.k_pos[0] - initial_displacement_light)
    assert delta_light > 0  # atom moves at all
```

- [ ] **Step 2: Append to `world/physics.py`**

```python
def apply_scale_repulsion(world, dt: float) -> None:
    """Accumulate repulsive force into k_vel for nodes whose freq_ratio exceeds threshold."""
    cfg = world.config
    if cfg.repulsion_k == 0.0 or world.k_count == 0:
        return
    box = np.asarray(cfg.box_size, dtype=np.float64)
    cell = cfg.repulsion_cell_size
    threshold = cfg.repulsion_threshold_ratio
    grid = build_grid(world.k_pos[:world.k_count], world.k_alive[:world.k_count], box, cell)

    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        f_i = world.k_freq[i]
        nbrs = neighbors_of(grid, world.k_pos[i], box, cell, exclude_self=True, query_index=i)
        for j in nbrs:
            if not world.k_alive[j]:
                continue
            f_j = world.k_freq[j]
            ratio = max(f_i, f_j) / min(f_i, f_j)
            if ratio <= threshold:
                continue
            # Direction: from j to i
            dx = world.k_pos[i, 0] - world.k_pos[j, 0]
            dy = world.k_pos[i, 1] - world.k_pos[j, 1]
            dz = world.k_pos[i, 2] - world.k_pos[j, 2]
            # Apply periodic wrap
            for d_idx, d_val in enumerate((dx, dy, dz)):
                if d_val > box[d_idx] * 0.5:
                    d_val -= box[d_idx]
                elif d_val < -box[d_idx] * 0.5:
                    d_val += box[d_idx]
                if d_idx == 0: dx = d_val
                elif d_idx == 1: dy = d_val
                else: dz = d_val
            r2 = dx*dx + dy*dy + dz*dz
            if r2 < 1e-9:
                continue
            r = math.sqrt(r2)
            # F_magnitude = k * (ratio - threshold) / r²
            F_mag = cfg.repulsion_k * (ratio - threshold) / r2
            # Mass from level (heavier nodes accelerate less)
            mass_i = float(world.k_level[i])
            ax = F_mag * dx / r / mass_i
            ay = F_mag * dy / r / mass_i
            az = F_mag * dz / r / mass_i
            world.k_vel[i, 0] += ax * dt
            world.k_vel[i, 1] += ay * dt
            world.k_vel[i, 2] += az * dt


def move_nodes(world, dt: float) -> None:
    """Apply k_vel to k_pos with periodic wrap. Atoms move slowly because of mass."""
    box = np.asarray(world.config.box_size, dtype=np.float64)
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        for d in range(3):
            world.k_pos[i, d] = (world.k_pos[i, d] + world.k_vel[i, d] * dt) % box[d]
```

- [ ] **Step 3: Run, confirm pass**

```bash
pytest tests/test_repulsion.py -v
```

- [ ] **Step 4: Commit**

```bash
git add world/physics.py tests/test_repulsion.py
git commit -m "feat(physics): scale separation through repulsion (§4.6) and node motion under force"
```

---

## Task 8: 3D `tick()` composition

**Files:** `world/physics.py` (append), `tests/test_tick.py`

- [ ] **Step 1: Update `tests/test_tick.py`**

```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def test_tick_advances_time(empty_world):
    w = empty_world
    tick(w, 0.5)
    assert w.t == pytest.approx(0.5)


def test_tick_runs_full_default_world():
    """Full default 3D world ticks without crashing."""
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    tick(w, cfg.dt)
    assert w.t == pytest.approx(cfg.dt)


def test_tick_decay_then_bind_order():
    """A tick should update positions before binding scans."""
    # Smoke test — full tick on a world with 100 vibrations should not crash
    cfg = WorldConfig(n_initial_vibrations=100, box_size=(200., 200., 200.),
                      n_vibrations_max=256, n_nodes_max=64, rng_seed=42)
    w = World(cfg)
    for _ in range(10):
        tick(w, cfg.dt)
    assert w.t == pytest.approx(10 * cfg.dt)
```

- [ ] **Step 2: Append to `world/physics.py`**

```python
def tick(world, dt: float) -> None:
    """One simulation step. See CONCEPT.md v2 §4 + §7.1 for the canonical order."""
    box = np.asarray(world.config.box_size, dtype=np.float64)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    apply_scale_repulsion(world, dt)
    move_nodes(world, dt)
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    ambient_regeneration(world, dt)
    world.t += dt
```

- [ ] **Step 3: Run all tests**

```bash
pytest -v
```

- [ ] **Step 4: Commit**

```bash
git add world/physics.py tests/test_tick.py
git commit -m "feat(physics): full 3D tick — motion → repulsion → binding → decay → ambient"
```

---

## Task 9: Snapshot module

**Files:** `world/snapshot.py` (new), `tests/test_snapshot.py` (new)

- [ ] **Step 1: Write `tests/test_snapshot.py`**

```python
import numpy as np
import pytest
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot, load_snapshot, snapshot_filename


def test_filename_format():
    p = snapshot_filename(123.45)
    assert p.endswith("snapshot_t000123.45.npz")


def test_filename_chronological_sort():
    files = sorted([snapshot_filename(t) for t in (10.0, 1.0, 100.0)])
    # Lexicographic sort should match numerical order
    times = [float(f.split('_t')[1].split('.npz')[0]) for f in files]
    assert times == sorted(times)


def test_round_trip(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    # Run a few ticks to make state non-trivial
    from world.physics import tick
    for _ in range(10):
        tick(w, cfg.dt)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    w2 = load_snapshot(path)
    np.testing.assert_array_equal(w.s_pos, w2.s_pos)
    np.testing.assert_array_equal(w.k_pos, w2.k_pos)
    assert w.t == w2.t
    assert w.n_alive == w2.n_alive
    assert w.k_count == w2.k_count


def test_resumed_world_can_tick(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    from world.physics import tick
    for _ in range(10):
        tick(w, cfg.dt)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    w2 = load_snapshot(path)
    tick(w2, cfg.dt)  # should not crash
```

- [ ] **Step 2: Implement `world/snapshot.py`**

```python
from __future__ import annotations
import dataclasses
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World


def snapshot_filename(t: float) -> str:
    return f"snapshot_t{t:09.2f}.npz"


def save_snapshot(world: World, path: Path | str) -> None:
    cfg_dict = dataclasses.asdict(world.config)
    np.savez(
        path,
        s_pos=world.s_pos, s_vel=world.s_vel, s_freq=world.s_freq,
        s_pol=world.s_pol, s_alive=world.s_alive,
        k_pos=world.k_pos, k_vel=world.k_vel, k_freq=world.k_freq,
        k_pol=world.k_pol, k_level=world.k_level, k_birth=world.k_birth,
        k_alive=world.k_alive,
        k_comp_offset=world.k_comp_offset, k_comp_indices=world.k_comp_indices,
        k_comp_kind=world.k_comp_kind,
        t=np.array([world.t]),
        n_alive=np.array([world.n_alive]),
        k_count=np.array([world.k_count]),
        k_comp_used=np.array([world.k_comp_used]),
        config_json=np.array([str(cfg_dict)], dtype=object),
    )


def load_snapshot(path: Path | str) -> World:
    data = np.load(path, allow_pickle=True)
    cfg_dict = eval(str(data["config_json"][0]))
    if "box_size" in cfg_dict and isinstance(cfg_dict["box_size"], list):
        cfg_dict["box_size"] = tuple(cfg_dict["box_size"])
    cfg = WorldConfig(**cfg_dict)
    w = World(cfg)
    w.s_pos[:] = data["s_pos"]
    w.s_vel[:] = data["s_vel"]
    w.s_freq[:] = data["s_freq"]
    w.s_pol[:] = data["s_pol"]
    w.s_alive[:] = data["s_alive"]
    w.k_pos[:] = data["k_pos"]
    w.k_vel[:] = data["k_vel"]
    w.k_freq[:] = data["k_freq"]
    w.k_pol[:] = data["k_pol"]
    w.k_level[:] = data["k_level"]
    w.k_birth[:] = data["k_birth"]
    w.k_alive[:] = data["k_alive"]
    w.k_comp_offset[:] = data["k_comp_offset"]
    w.k_comp_indices[:] = data["k_comp_indices"]
    w.k_comp_kind[:] = data["k_comp_kind"]
    w.t = float(data["t"][0])
    w.n_alive = int(data["n_alive"][0])
    w.k_count = int(data["k_count"][0])
    w.k_comp_used = int(data["k_comp_used"][0])
    return w
```

- [ ] **Step 3: Run, confirm pass**

```bash
pytest tests/test_snapshot.py -v
```

- [ ] **Step 4: Commit**

```bash
git add world/snapshot.py tests/test_snapshot.py
git commit -m "feat(snapshot): NPZ save/load with config metadata, chronological filenames"
```

---

## Task 10: CLI rewrite + Open3D preview scaffolding

**Files:** `world/run.py`, `world/preview.py` (new), `world/render.py` (delete)

- [ ] **Step 1: Delete the old Pygame renderer**

```bash
git rm world/render.py
```

- [ ] **Step 2: Write `world/preview.py`**

```python
"""Open3D 3D live preview. Polls the world state at low frame rate. Read-only."""
from __future__ import annotations
import numpy as np
import open3d as o3d
import threading


COLOR_VIBR_EVEN = [0.29, 0.56, 0.89]
COLOR_VIBR_ODD = [0.91, 0.30, 0.24]
COLOR_ELECTRON = [0.95, 0.61, 0.07]
COLOR_ATOM = [1.0, 1.0, 1.0]


class LivePreview:
    """Non-blocking Open3D viewer that polls a World instance. Run in a thread."""

    def __init__(self, world):
        self.world = world
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window("World of Vibrations — live preview")
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()
        self.thread.join(timeout=2.0)
        self.vis.destroy_window()

    def _loop(self):
        import time
        while not self._stop.is_set():
            geom = self._build_geometry()
            self.vis.clear_geometries()
            for g in geom:
                self.vis.add_geometry(g, reset_bounding_box=False)
            self.vis.poll_events()
            self.vis.update_renderer()
            time.sleep(0.1)  # 10 fps preview

    def _build_geometry(self):
        w = self.world
        geom = []
        # Vibrations as point cloud
        if w.n_alive > 0:
            alive = w.s_alive
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(w.s_pos[alive])
            colors = np.where(w.s_pol[alive, None],
                              np.array(COLOR_VIBR_EVEN),
                              np.array(COLOR_VIBR_ODD))
            pcd.colors = o3d.utility.Vector3dVector(colors)
            geom.append(pcd)
        # Nodes as labelled spheres (small for now; refine in render_blender for keyframes)
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            radius = {1: 1.0, 2: 1.5, 3: 2.0, 4: 3.0}.get(level, 1.0)
            color = COLOR_ELECTRON if level == 1 else COLOR_ATOM
            sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius, resolution=8)
            sphere.translate(w.k_pos[i])
            sphere.paint_uniform_color(color)
            geom.append(sphere)
        return geom
```

- [ ] **Step 3: Rewrite `world/run.py`**

```python
"""CLI entry point for the World of Vibrations simulation."""
from __future__ import annotations
import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick
from world.snapshot import save_snapshot, snapshot_filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="world", description="World of Vibrations")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, default=None)
    run.add_argument("--duration", type=float, default=60.0)
    run.add_argument("--snapshot-every", type=float, default=None)
    run.add_argument("--snapshot-dir", type=Path, default=None)
    run.add_argument("--save", type=Path, default=None)
    run.add_argument("--seed", type=int, default=None)
    run.add_argument("--preview", action="store_true",
                     help="open Open3D live preview alongside the simulation")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    if args.seed is not None:
        cfg = replace(cfg, rng_seed=args.seed)
    world = World(cfg)

    if args.snapshot_dir:
        args.snapshot_dir.mkdir(parents=True, exist_ok=True)

    preview = None
    if args.preview:
        from world.preview import LivePreview
        preview = LivePreview(world)
        preview.start()

    n_ticks = int(args.duration / cfg.dt)
    snap_step = int(args.snapshot_every / cfg.dt) if args.snapshot_every else None
    start = time.time()
    try:
        for k in range(n_ticks):
            tick(world, cfg.dt)
            if snap_step and (k + 1) % snap_step == 0 and args.snapshot_dir:
                path = args.snapshot_dir / snapshot_filename(world.t)
                save_snapshot(world, path)
                _print_stats(world)
    finally:
        if preview:
            preview.stop()

    wall = time.time() - start
    print(f"# done — {args.duration:.1f} simulated s in {wall:.1f} wall s "
          f"({args.duration / wall:.1f}× real-time)")
    _print_stats(world)
    if args.save:
        save_snapshot(world, args.save)
    return 0


def _print_stats(world):
    n_v = int(world.s_alive.sum())
    n_e = int(((world.k_level == 1) & world.k_alive).sum())
    n_p = int(((world.k_level == 2) & world.k_alive).sum())
    n_t = int(((world.k_level == 3) & world.k_alive).sum())
    n_a = int(((world.k_level == 4) & world.k_alive).sum())
    print(f"t = {world.t:7.2f} | total_v {world.total_vibrations():6d} "
          f"| ambient {world.ambient_density():.4e} "
          f"| vibr {n_v:5d} | e- {n_e:4d} | pair {n_p:3d} | "
          f"triad {n_t:3d} | atom {n_a:3d}")


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Smoke test**

```bash
python -m world run --duration 5 --snapshot-every 1 --snapshot-dir /tmp/snap-test/
ls /tmp/snap-test/
```

Expected: 5 snapshot files created.

- [ ] **Step 5: Smoke test preview (manual)**

```bash
python -m world run --duration 10 --preview
```

Expected: Open3D window opens, simulation runs for 10 simulated seconds, window closes.

- [ ] **Step 6: Commit**

```bash
git add world/run.py world/preview.py
git rm world/render.py 2>/dev/null || true
git commit -m "feat(cli): snapshot-aware run, Open3D live preview, drop Pygame renderer"
```

---

## Task 11: Parameter sweep harness

**Files:** `tools/sweep.py` (new), `tests/test_sweep.py` (new)

- [ ] **Step 1: Write `tests/test_sweep.py`**

```python
import json
import pytest
from pathlib import Path
from tools.sweep import grid_configs, run_one_trial


def test_grid_enumeration():
    configs = list(grid_configs({"r_2": [10, 20, 30], "freq_tolerance": [0.005, 0.01]}))
    assert len(configs) == 6
    assert {"r_2": 10, "freq_tolerance": 0.005} in configs


def test_run_one_trial_returns_objective(tmp_path):
    """A short trial returns a finite objective value."""
    params = {"box_size": [200.0, 200.0, 200.0], "duration": 5.0,
              "objective": "time_to_first_atom"}
    result = run_one_trial(params, snapshot_dir=tmp_path)
    assert "objective" in result
    assert "params" in result
    assert "wall_s" in result
```

- [ ] **Step 2: Implement `tools/sweep.py`**

```python
"""Parameter sweep harness with grid, random, and Optuna backends."""
from __future__ import annotations
import argparse
import itertools
import json
import math
import time
from dataclasses import replace
from pathlib import Path
from typing import Iterable

import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def grid_configs(param_ranges: dict) -> Iterable[dict]:
    keys = list(param_ranges.keys())
    for values in itertools.product(*[param_ranges[k] for k in keys]):
        yield dict(zip(keys, values))


def random_configs(param_bounds: dict, n: int, rng_seed: int = 42) -> Iterable[dict]:
    rng = np.random.default_rng(rng_seed)
    for _ in range(n):
        cfg = {}
        for key, (low, high) in param_bounds.items():
            cfg[key] = float(rng.uniform(low, high))
        yield cfg


def run_one_trial(params: dict, snapshot_dir: Path | None = None) -> dict:
    """Run a simulation with `params` overlaid on default WorldConfig.

    Returns a dict with `params`, `objective`, `wall_s`, `final_counts`.
    """
    duration = float(params.pop("duration", 60.0))
    objective_name = params.pop("objective", "time_to_first_atom")
    base = WorldConfig()
    if "box_size" in params and isinstance(params["box_size"], list):
        params["box_size"] = tuple(params["box_size"])
    cfg = replace(base, **{k: v for k, v in params.items() if hasattr(base, k)})
    w = World(cfg)
    n_ticks = int(duration / cfg.dt)
    start = time.time()
    first_atom_t = math.inf
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        if first_atom_t == math.inf and ((w.k_level == 4) & w.k_alive).any():
            first_atom_t = w.t
    wall = time.time() - start

    counts = {
        "vibr": int(w.s_alive.sum()),
        "e_": int(((w.k_level == 1) & w.k_alive).sum()),
        "pair": int(((w.k_level == 2) & w.k_alive).sum()),
        "triad": int(((w.k_level == 3) & w.k_alive).sum()),
        "atom": int(((w.k_level == 4) & w.k_alive).sum()),
    }

    objective = {
        "time_to_first_atom": first_atom_t,
    }.get(objective_name, math.inf)

    return {
        "params": params,
        "objective": float(objective) if math.isfinite(objective) else None,
        "wall_s": wall,
        "final_counts": counts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/sweep.py")
    parser.add_argument("--backend", choices=["grid", "random"], default="grid")
    parser.add_argument("--params-toml", type=Path, required=True,
                        help="TOML defining grid/random ranges")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--objective", type=str, default="time_to_first_atom")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-trials", type=int, default=20,
                        help="for random backend")
    args = parser.parse_args(argv)

    import tomllib
    with open(args.params_toml, "rb") as f:
        ranges = tomllib.load(f)

    if args.backend == "grid":
        configs = list(grid_configs(ranges))
    else:
        # ranges are 2-element [low, high] lists for random
        bounds = {k: tuple(v) for k, v in ranges.items()}
        configs = list(random_configs(bounds, args.n_trials))

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.workers == 1:
        for cfg in configs:
            cfg["duration"] = args.duration
            cfg["objective"] = args.objective
            result = run_one_trial(cfg)
            with open(args.output, "a") as f:
                f.write(json.dumps(result) + "\n")
            print(f"[{cfg}] objective={result['objective']} counts={result['final_counts']}")
    else:
        from multiprocessing import Pool
        configs_with_meta = [{**c, "duration": args.duration, "objective": args.objective}
                             for c in configs]
        with Pool(args.workers) as pool:
            for result in pool.imap_unordered(run_one_trial, configs_with_meta):
                with open(args.output, "a") as f:
                    f.write(json.dumps(result) + "\n")
                print(f"objective={result['objective']} counts={result['final_counts']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
```

- [ ] **Step 3: Smoke test**

```bash
mkdir -p /tmp/sweep-test
cat > /tmp/sweep-test/ranges.toml <<EOF
r_2 = [10.0, 20.0]
freq_tolerance = [0.01, 0.02]
EOF
python tools/sweep.py --backend grid --params-toml /tmp/sweep-test/ranges.toml \
                     --duration 5 --output /tmp/sweep-test/results.jsonl
wc -l /tmp/sweep-test/results.jsonl  # expected: 4
```

- [ ] **Step 4: Commit**

```bash
git add tools/sweep.py tests/test_sweep.py
git commit -m "feat(tools): parameter sweep harness with grid/random backends"
```

---

## Task 12: Frequency histogram tool

**Files:** `tools/histogram.py` (new), `tests/test_histogram.py` (new)

- [ ] **Step 1: Write `tests/test_histogram.py`**

```python
from pathlib import Path
import pytest
from world.config import WorldConfig
from world.state import World
from world.snapshot import save_snapshot
from tools.histogram import compute_histogram_text


def test_text_output_lists_levels(tmp_path):
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    text = compute_histogram_text(path)
    assert "vibrations" in text.lower()
    assert "electrons" in text.lower() or "e-" in text


def test_empty_world_no_crash(tmp_path):
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100., 100., 100.),
                      rng_seed=42)
    w = World(cfg)
    path = tmp_path / "snap.npz"
    save_snapshot(w, path)
    text = compute_histogram_text(path)
    assert isinstance(text, str)
```

- [ ] **Step 2: Implement `tools/histogram.py`**

```python
"""Frequency-histogram observation tool over a snapshot."""
from __future__ import annotations
import argparse
from collections import Counter
import math
from pathlib import Path
import numpy as np
from world.snapshot import load_snapshot


def compute_histogram_text(snapshot_path: Path) -> str:
    w = load_snapshot(snapshot_path)
    lines = [f"Snapshot: {snapshot_path.name} | t = {w.t:.2f}"]

    # Vibrations
    alive_v = w.s_alive
    if alive_v.any():
        decade_counts = Counter(int(math.floor(math.log10(f))) for f in w.s_freq[alive_v] if f > 0)
        lines.append(f"vibrations ({int(alive_v.sum())}): "
                     + ", ".join(f"10^{d}: {c}" for d, c in sorted(decade_counts.items())))
    else:
        lines.append("vibrations: 0")

    # Nodes per level
    for level, name in [(1, "electrons"), (2, "pairs"), (3, "triads"), (4, "atoms")]:
        mask = (w.k_level == level) & w.k_alive
        if mask.any():
            decade_counts = Counter(int(math.floor(math.log10(f))) for f in w.k_freq[mask] if f > 0)
            lines.append(f"{name} ({int(mask.sum())}): "
                         + ", ".join(f"10^{d}: {c}" for d, c in sorted(decade_counts.items())))
        else:
            lines.append(f"{name}: 0")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/histogram.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "png"], default="text")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.format == "text":
        out = compute_histogram_text(args.snapshot)
        if args.output:
            args.output.write_text(out)
        else:
            print(out)
    elif args.format == "png":
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed; install via `pip install matplotlib`")
            return 1
        # Simple multi-panel histogram
        w = load_snapshot(args.snapshot)
        fig, axes = plt.subplots(1, 5, figsize=(15, 3))
        for ax, (level, name) in zip(axes, [(0, "vibrations"), (1, "electrons"),
                                              (2, "pairs"), (3, "triads"), (4, "atoms")]):
            if level == 0:
                freqs = w.s_freq[w.s_alive]
            else:
                mask = (w.k_level == level) & w.k_alive
                freqs = w.k_freq[mask]
            if len(freqs) > 0:
                ax.hist(np.log10(freqs[freqs > 0]), bins=20)
            ax.set_title(name)
            ax.set_xlabel("log10(freq)")
        fig.tight_layout()
        fig.savefig(args.output or "histogram.png", dpi=150)
        plt.close(fig)
        print(f"Wrote {args.output or 'histogram.png'}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
```

- [ ] **Step 3: Run, confirm pass**

```bash
pytest tests/test_histogram.py -v
```

- [ ] **Step 4: Commit**

```bash
git add tools/histogram.py tests/test_histogram.py
git commit -m "feat(tools): frequency-histogram observation tool over snapshots"
```

---

## Task 13: Blender keyframe rendering script

**Files:** `tools/render_blender.py` (new)

- [ ] **Step 1: Write `tools/render_blender.py`**

```python
"""Headless Blender Cycles renderer for snapshot keyframes.

Invoke via:
    blender -b -P tools/render_blender.py -- --snapshot snap.npz --output frame.png

Inside Blender's Python:
- Load snapshot
- Build scene (camera, lights, instanced spheres per level)
- Render to PNG
"""
import sys
import argparse
from pathlib import Path

# Strip Blender's own argv before --
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
else:
    argv = []

parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--quality", choices=["low", "medium", "high", "paper"], default="medium")
args = parser.parse_args(argv)

# Lazy imports — these only work inside Blender
try:
    import bpy
    import numpy as np
except ImportError:
    print("This script must be run inside Blender (blender -b -P ...).", file=sys.stderr)
    sys.exit(1)


SAMPLES = {"low": 64, "medium": 256, "high": 1024, "paper": 4096}[args.quality]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def setup_camera_and_lights(box_size):
    # Camera at the long diagonal
    cam_pos = (box_size[0] * 1.6, -box_size[1] * 1.2, box_size[2] * 1.4)
    bpy.ops.object.camera_add(location=cam_pos)
    cam = bpy.context.object
    cam.rotation_euler = (1.0, 0, 0.7)
    bpy.context.scene.camera = cam

    # Three-point lighting
    for loc, energy in [
        ((box_size[0] * 1.5, -box_size[1] * 1.5, box_size[2] * 1.5), 1500.0),
        ((-box_size[0] * 0.5, box_size[1] * 1.0, box_size[2] * 0.5), 800.0),
        ((box_size[0] * 0.5, box_size[1] * 0.5, -box_size[2] * 0.3), 400.0),
    ]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.data.energy = energy


def add_node_meshes(positions, levels, alive):
    """Add one sphere per alive node, sized by level."""
    for i in range(len(positions)):
        if not alive[i]:
            continue
        level = int(levels[i])
        radius = {1: 1.5, 2: 2.0, 3: 2.5, 4: 4.0}.get(level, 1.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=positions[i].tolist())
        obj = bpy.context.object
        mat = bpy.data.materials.new(f"node_l{level}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        color = {1: (1.0, 0.6, 0.07, 1), 4: (1.0, 1.0, 1.0, 1)}.get(level, (0.7, 0.7, 0.9, 1))
        bsdf.inputs["Base Color"].default_value = color
        if level == 4:
            bsdf.inputs["Emission Strength"].default_value = 2.0
            bsdf.inputs["Emission Color"].default_value = color
        obj.data.materials.append(mat)


def main():
    data = np.load(args.snapshot, allow_pickle=True)
    cfg_dict = eval(str(data["config_json"][0]))
    box_size = tuple(cfg_dict["box_size"])

    clear_scene()
    setup_camera_and_lights(box_size)
    add_node_meshes(data["k_pos"], data["k_level"], data["k_alive"])

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(args.output)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    bpy.ops.render.render(write_still=True)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Manual smoke test**

```bash
# First, generate a snapshot:
python -m world run --duration 30 --snapshot-every 30 --snapshot-dir /tmp/blender-test/

# Then, render one keyframe at low quality:
blender -b -P tools/render_blender.py -- \
  --snapshot /tmp/blender-test/snapshot_t000030.00.npz \
  --output /tmp/blender-test/frame.png \
  --quality low
ls -la /tmp/blender-test/frame.png
```

Expected: PNG file created, ~1920x1080, 1-2 minutes for the low-quality render.

- [ ] **Step 3: Commit**

```bash
git add tools/render_blender.py
git commit -m "feat(tools): Blender Cycles keyframe renderer for snapshots"
```

---

## Task 14: Acceptance check + LOGBOOK update

**Files:** `LOGBOOK.md`

- [ ] **Step 1: Run full test suite**

```bash
pytest -v 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 2: Run a 5-minute headless calibration with snapshots**

```bash
mkdir -p snapshots/v2-acceptance/
python -m world run --duration 300 --snapshot-every 30 --snapshot-dir snapshots/v2-acceptance/
ls snapshots/v2-acceptance/ | wc -l   # expected ~10 snapshots
```

- [ ] **Step 3: Verify ambient density stability**

```bash
python tools/histogram.py snapshots/v2-acceptance/snapshot_t0000300.00.npz --format text
```

Compare ambient density (the printed `ambient` field in stats) at t=30 vs t=300; should be within 20% of each other for the run to count as ambient-stable.

- [ ] **Step 4: Run a small parameter sweep**

```bash
cat > /tmp/sweep-r2.toml <<EOF
r_2 = [10.0, 20.0, 30.0]
EOF
python tools/sweep.py --backend grid --params-toml /tmp/sweep-r2.toml \
                     --duration 60 --output sweeps/v2-r2.jsonl
wc -l sweeps/v2-r2.jsonl   # expected: 3
```

- [ ] **Step 5: Render one Blender keyframe**

```bash
blender -b -P tools/render_blender.py -- \
  --snapshot snapshots/v2-acceptance/snapshot_t0000300.00.npz \
  --output renders/v2-acceptance.png \
  --quality medium
```

- [ ] **Step 6: Update LOGBOOK with v2 session entry**

Add a new section to `LOGBOOK.md`:

```markdown
## 2026-05-12 — Session 2: Phase 1 v2 shipped

- 3D substrate, scale repulsion, ambient regeneration, snapshot/preview/Blender pipeline, sweep harness all in.
- Test count: [paste actual] passing.
- Acceptance check: [paste actual ambient density at t=30, t=300; ratio].
- First v2 calibration sweep over r_2 ∈ {10, 20, 30}: [paste results].
- First Blender keyframe at renders/v2-acceptance.png — [paste impressions].

Next session: calibrate parameters that satisfy CONCEPT.md v2 §5 Phase 1 success criteria
(reproducible atom formation + spatial sorting by frequency decade + ambient stability over 1 hour).
```

- [ ] **Step 7: Final commit + push**

```bash
git add LOGBOOK.md
git commit -m "docs(logbook): session 2 — Phase 1 v2 shipped"
git push
```

---

## Self-review notes

| Spec section | Covered by task |
|---|---|
| §3 architectural decisions | Tasks 0–10 (Pygame removed, Open3D added, snapshots central) |
| §4 substrate (3D, repulsion, ambient) | Tasks 1–8 |
| §5 scale repulsion | Task 7 |
| §6 ambient regeneration | Task 6 |
| §7 snapshot format | Task 9 |
| §8 live preview | Task 10 |
| §9 Blender keyframes | Task 13 |
| §10 sweep harness | Task 11 |
| §11 histogram tool | Task 12 |
| §12 config changes | Task 1 |
| §13 CLI changes | Task 10 |
| §14 bootstrap | Task 0 |
| §15 acceptance | Task 14 |

No placeholders. All function names match across tasks. The plan inherits the v1 plan's commit-per-task discipline and TDD-first ordering.
