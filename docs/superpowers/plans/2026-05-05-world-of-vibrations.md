# World of Vibrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real-time 2D simulation in which vibrations bind through fixed natural laws into electrons, pairs, triads, and indestructible atoms — observable in a Pygame window and runnable headless for multi-hour calibration.

**Architecture:** Decoupled physics and rendering. Physics is a pure data model (Struct-of-Arrays NumPy + Numba `@njit` hot loops) in `world/state.py` and `world/physics.py`. Renderer in `world/render.py` reads the state but never mutates. CLI in `world/run.py` dispatches both window and headless modes. Tests exercise physics functions directly, bypassing the renderer.

**Tech Stack:** Python 3.11+, NumPy, Numba (`@njit`), Pygame, pytest, TOML (stdlib `tomllib`), `hatchling` build backend.

**Spec reference:** `docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md`. The spec is the source of truth — when this plan and the spec disagree, the spec wins.

**One spec deviation noted up front:** spec §9.1 lists translation of a repo-root `README.md`. No such file currently exists in `EQMOD/`. The plan creates a new English root `README.md` from scratch instead; no German original to preserve.

---

## File structure

Files this plan creates or modifies, with single-responsibility scope:

| Path | Responsibility |
|---|---|
| `.gitignore` | Standard Python ignores |
| `pyproject.toml` | Package definition, deps, build backend, CLI entry point |
| `README.md` | New English root README — project intro and quickstart |
| `LOGBOOK.md` | Research diary template + first session entry |
| `files/README.de.md` | German original of `files/README.md`, preserved |
| `files/README.md` | English translation (overwrites the German file) |
| `files/SKILL.de.md` | German original of `files/SKILL.md`, preserved |
| `files/SKILL.md` | English translation |
| `files/SPEZIFIKATION.de.md` | German original of `files/SPEZIFIKATION.md`, preserved |
| `files/SPECIFICATION.md` | English translation, renamed |
| `world/__init__.py` | Package marker, re-exports |
| `world/config.py` | `WorldConfig` frozen dataclass + `INITIAL_CONFIG` + TOML loader |
| `world/state.py` | `World` class — pure data; SoA NumPy arrays; capacity, seeding, compaction |
| `world/spatial.py` | `@njit` spatial hash, periodic-wrapping cell grid, neighbor iteration |
| `world/physics.py` | `@njit` motion, binding (vibration→electron, electron→pair→triad→atom), decay; the `tick(world, dt)` driver |
| `world/render.py` | Pygame renderer; reads state only; visual rules from spec §7.1 |
| `world/run.py` | CLI entry — `python -m world run [...]`; wires headless and window modes |
| `tests/__init__.py` | Package marker |
| `tests/conftest.py` | pytest fixtures — `tiny_world` factory, deterministic RNG |
| `tests/test_config.py` | `WorldConfig` defaults and TOML override |
| `tests/test_state.py` | World seeding, array shapes, compaction |
| `tests/test_spatial.py` | Spatial hash correctness, periodic wrap, neighbor iteration |
| `tests/test_motion.py` | Linear motion, periodic boundaries |
| `tests/test_binding.py` | Vibration→electron, all node-upgrade levels, parity randomization |
| `tests/test_decay.py` | Pair and triad exponential decay, atom indestructibility, decade isolation |
| `tests/test_tick.py` | End-to-end tick composition |
| `tests/calibration_smoke.py` | Standalone 60-second headless smoke run (not in default `pytest`) |

**Decomposition rationale.** `world/state.py` holds *only* arrays and lifecycle (alloc, seed, compact). `physics.py` holds *only* `@njit` rules. `spatial.py` is split out because the hash is reused by both `bind_vibrations_to_electrons` and `bind_nodes_upward`, and its periodic-wrap math is delicate enough to deserve its own test file. `render.py` is a strict reader; importing it from headless mode is forbidden. Tests are split by responsibility, not per-function, so each file holds one full subject and its edge cases.

---

## Task 0: Repo init and skeleton

**Files:**
- Create: `.gitignore`
- Create: `world/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)

- [ ] **Step 1: Initialize git repository**

```bash
cd /Users/mkupermann/Documents/GitHub/EQMOD
git init
git config user.name "$(git config --global user.name || echo 'Michael Kupermann')"
git config user.email "$(git config --global user.email || echo 'michael@kupermann.com')"
```

Expected: `Initialized empty Git repository in .../EQMOD/.git/`

- [ ] **Step 2: Create `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
env/
ENV/

# pytest
.pytest_cache/
.coverage
htmlcov/

# Editor / OS
.vscode/
.idea/
.DS_Store
*.swp

# Numba
__pycache__/
.numba_cache/

# Simulation artifacts
*.npz
docs/logbook/*.png
!docs/logbook/.gitkeep
```

- [ ] **Step 3: Create empty package and test markers**

`world/__init__.py`:
```python
"""World of Vibrations — physical substrate built from vibrations alone."""
```

`tests/__init__.py`:
```python
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore world/__init__.py tests/__init__.py docs/
git commit -m "chore: initialize repo, package skeleton, and brainstorming spec"
```

Expected: commit succeeds, includes spec under `docs/superpowers/specs/` and this plan under `docs/superpowers/plans/`.

---

## Task 1: Bootstrap — translate German source files

**Files:**
- Move: `files/README.md` → `files/README.de.md`
- Move: `files/SKILL.md` → `files/SKILL.de.md`
- Move: `files/SPEZIFIKATION.md` → `files/SPEZIFIKATION.de.md`
- Create: `files/README.md` (English)
- Create: `files/SKILL.md` (English)
- Create: `files/SPECIFICATION.md` (English)

- [ ] **Step 1: Preserve German originals as `*.de.md`**

```bash
cd /Users/mkupermann/Documents/GitHub/EQMOD
git mv files/README.md files/README.de.md
git mv files/SKILL.md files/SKILL.de.md
git mv files/SPEZIFIKATION.md files/SPEZIFIKATION.de.md
```

- [ ] **Step 2: Translate `files/README.de.md` → `files/README.md`**

Faithful English translation of the German `files/README.de.md`, preserving structure, headings, and tone. No content rewrites. Save as `files/README.md` (UTF-8). The German is research-honest and slightly informal — keep that register in English.

The translation must cover all sections present in the German original: project intro ("World of Vibrations"), directory contents, "How to begin" with steps 1–4, logbook guidance, honest expectations, and the two closing notes ("Let the world work", "Trust the world more than your expectations").

- [ ] **Step 3: Translate `files/SKILL.de.md` → `files/SKILL.md`**

Faithful translation. Keep the YAML frontmatter (`name`, `description`) but translate the description to English. All 8 phases preserved with the same structure (Goal, Components, Success criterion). Preserve the closing "Ethics and reflection" section.

- [ ] **Step 4: Translate `files/SPEZIFIKATION.de.md` → `files/SPECIFICATION.md`**

Faithful translation. Note: the filename changes from German `SPEZIFIKATION` to English `SPECIFICATION`. All 6 parts plus the appendix "Implementation checklist" preserved. The data structure code blocks stay in Python — only the comments and identifier-doc translates. Class names like `Schwingung`, `Knoten`, `Welt` stay in the example code as-is, since they're showing the source spec's example design (the actual code in `world/` will use English names per the design spec we wrote).

- [ ] **Step 5: Verify translations are complete and well-formed**

```bash
wc -l files/*.md
ls -la files/
```

Expected output: six files (README.md, README.de.md, SKILL.md, SKILL.de.md, SPECIFICATION.md, SPEZIFIKATION.de.md). Line counts should be similar between German and English versions (within 30%).

- [ ] **Step 6: Commit**

```bash
git add files/
git commit -m "docs: translate source files to English, preserve German originals"
```

---

## Task 2: Create `pyproject.toml`

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "world"
version = "0.1.0"
description = "World of Vibrations — a simulated physical substrate built from vibrations alone."
readme = "README.md"
requires-python = ">=3.11"
authors = [{ name = "Michael Kupermann", email = "michael@kupermann.com" }]
dependencies = [
    "numpy >= 1.26",
    "numba >= 0.59",
    "pygame >= 2.5",
]

[project.optional-dependencies]
dev = ["pytest >= 8.0"]

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

- [ ] **Step 2: Create virtual environment and install**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

Expected: install succeeds, no errors. Numba may take 30–60 s.

- [ ] **Step 3: Sanity import check**

```bash
python -c "import world; import numpy, numba, pygame; print('OK')"
```

Expected output: `OK`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: add pyproject.toml with numpy, numba, pygame, pytest"
```

---

## Task 3: Create root `README.md` (English, new file)

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write English root README**

```markdown
# World of Vibrations

A simulated 2D world whose only primitive substance is **vibrations**. Through a small set of natural laws, vibrations bind into electrons, then into pairs, triads, and indestructible atoms. The long-term research goal is to grow brain-like structures from this physical substrate.

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run with default config in a Pygame window
python -m world run

# Headless calibration run, 60 simulated seconds
python -m world run --headless --duration 60 --snapshot-every 5
```

Press `Esc` to quit, `Space` to pause, `R` to reset.

## Project layout

- `world/` — Python package (state, physics, spatial hash, renderer, CLI)
- `tests/` — pytest suite for natural laws + calibration smoke test
- `files/` — source spec documents (English + preserved German originals)
- `docs/superpowers/specs/` — design specifications
- `docs/superpowers/plans/` — implementation plans
- `LOGBOOK.md` — research diary

## Documentation

- `files/SPECIFICATION.md` — original world spec (English)
- `files/SKILL.md` — long-term phase plan toward brain-like structures
- `docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md` — design spec for Phase 1 (this build)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add English root README"
```

---

## Task 4: `WorldConfig` dataclass

**Files:**
- Create: `world/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

`tests/test_config.py`:
```python
import pytest
import tomllib
from pathlib import Path
from world.config import WorldConfig, INITIAL_CONFIG, load_config


def test_default_config_matches_spec():
    cfg = WorldConfig()
    assert cfg.n_initial_vibrations == 1000
    assert cfg.box_size == (1000.0, 1000.0)
    assert cfg.freq_min == 100.0
    assert cfg.freq_max == 10000.0
    assert cfg.freq_distribution == "log"
    assert cfg.r_1 == 5.0
    assert cfg.r_2 == 10.0
    assert cfg.freq_ratio == 0.08
    assert cfg.freq_tolerance == 0.005
    assert cfg.pair_decay_time == 5.0
    assert cfg.triad_decay_time == 30.0
    assert cfg.dt == pytest.approx(1.0 / 60.0)
    assert cfg.rng_seed == 42
    assert cfg.n_vibrations_max == 4096
    assert cfg.n_nodes_max == 1024


def test_initial_config_singleton():
    assert INITIAL_CONFIG == WorldConfig()


def test_config_is_frozen():
    cfg = WorldConfig()
    with pytest.raises(Exception):
        cfg.r_1 = 99.0  # type: ignore[misc]


def test_toml_override(tmp_path: Path):
    toml = tmp_path / "override.toml"
    toml.write_text('r_1 = 7.5\nrng_seed = 123\n')
    cfg = load_config(toml)
    assert cfg.r_1 == 7.5
    assert cfg.rng_seed == 123
    # Untouched fields keep defaults
    assert cfg.r_2 == 10.0
    assert cfg.n_initial_vibrations == 1000


def test_load_config_with_no_path_returns_defaults():
    assert load_config(None) == WorldConfig()
```

- [ ] **Step 2: Run the test, confirm it fails**

```bash
pytest tests/test_config.py -v
```

Expected: ImportError or `ModuleNotFoundError: No module named 'world.config'`.

- [ ] **Step 3: Implement `world/config.py`**

```python
from __future__ import annotations
import tomllib
from dataclasses import dataclass, replace, fields
from pathlib import Path


@dataclass(frozen=True)
class WorldConfig:
    # Seeding
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float] = (1000.0, 1000.0)
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

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_config.py -v
```

Expected: all 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add world/config.py tests/test_config.py
git commit -m "feat(config): WorldConfig dataclass with TOML override loader"
```

---

## Task 5: `World` data model and seeding

**Files:**
- Create: `world/state.py`
- Create: `tests/conftest.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write conftest fixtures**

`tests/conftest.py`:
```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


@pytest.fixture
def default_config() -> WorldConfig:
    return WorldConfig()


@pytest.fixture
def tiny_config() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=4,
        box_size=(100.0, 100.0),
        n_vibrations_max=64,
        n_nodes_max=32,
        rng_seed=42,
    )


@pytest.fixture
def empty_world() -> World:
    """A world with capacity but zero seeded vibrations — for hand-placing test scenarios."""
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(100.0, 100.0),
        n_vibrations_max=64,
        n_nodes_max=32,
        rng_seed=42,
    )
    return World(cfg)
```

- [ ] **Step 2: Write the failing test**

`tests/test_state.py`:
```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World


def test_world_constructs_with_correct_capacity(default_config):
    w = World(default_config)
    assert w.s_pos.shape == (default_config.n_vibrations_max, 2)
    assert w.s_vel.shape == (default_config.n_vibrations_max, 2)
    assert w.s_freq.shape == (default_config.n_vibrations_max,)
    assert w.s_pol.shape == (default_config.n_vibrations_max,)
    assert w.s_alive.shape == (default_config.n_vibrations_max,)
    assert w.k_pos.shape == (default_config.n_nodes_max, 2)
    assert w.k_freq.shape == (default_config.n_nodes_max,)
    assert w.k_pol.shape == (default_config.n_nodes_max,)
    assert w.k_level.shape == (default_config.n_nodes_max,)
    assert w.k_alive.shape == (default_config.n_nodes_max,)


def test_world_seeds_initial_vibrations(default_config):
    w = World(default_config)
    assert w.n_alive == default_config.n_initial_vibrations
    alive_idx = np.where(w.s_alive)[0]
    assert len(alive_idx) == default_config.n_initial_vibrations


def test_seeded_vibrations_within_box(default_config):
    w = World(default_config)
    alive = w.s_alive
    assert np.all(w.s_pos[alive, 0] >= 0)
    assert np.all(w.s_pos[alive, 0] < default_config.box_size[0])
    assert np.all(w.s_pos[alive, 1] >= 0)
    assert np.all(w.s_pos[alive, 1] < default_config.box_size[1])


def test_seeded_frequencies_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    assert np.all(w.s_freq[alive] >= default_config.freq_min)
    assert np.all(w.s_freq[alive] <= default_config.freq_max)


def test_seeded_polarities_split_roughly_half(default_config):
    w = World(default_config)
    alive = w.s_alive
    even_share = np.mean(w.s_pol[alive])
    assert 0.4 < even_share < 0.6  # within reasonable bounds for n=1000


def test_log_frequency_distribution_skews_low(default_config):
    """Log-distributed frequencies should have median below the arithmetic midpoint."""
    w = World(default_config)
    alive = w.s_alive
    median = float(np.median(w.s_freq[alive]))
    mid = (default_config.freq_min + default_config.freq_max) / 2
    assert median < mid


def test_seeded_speeds_in_range(default_config):
    w = World(default_config)
    alive = w.s_alive
    speeds = np.linalg.norm(w.s_vel[alive], axis=1)
    assert np.all(speeds >= default_config.speed_min - 1e-9)
    assert np.all(speeds <= default_config.speed_max + 1e-9)


def test_initial_node_count_is_zero(default_config):
    w = World(default_config)
    assert w.k_count == 0
    assert not np.any(w.k_alive)


def test_reproducible_seeding(default_config):
    w1 = World(default_config)
    w2 = World(default_config)
    np.testing.assert_array_equal(w1.s_pos, w2.s_pos)
    np.testing.assert_array_equal(w1.s_vel, w2.s_vel)
    np.testing.assert_array_equal(w1.s_freq, w2.s_freq)
    np.testing.assert_array_equal(w1.s_pol, w2.s_pol)
```

- [ ] **Step 3: Run, confirm failure**

```bash
pytest tests/test_state.py -v
```

Expected: ImportError on `from world.state import World`.

- [ ] **Step 4: Implement `world/state.py`**

```python
from __future__ import annotations
import numpy as np
from world.config import WorldConfig


class World:
    """Plain data container for the simulation. No physics methods — those live in `world.physics`."""

    def __init__(self, config: WorldConfig):
        self.config = config
        self.t: float = 0.0
        self.rng = np.random.default_rng(config.rng_seed)

        N = config.n_vibrations_max
        K = config.n_nodes_max

        # Vibration arrays
        self.s_pos = np.zeros((N, 2), dtype=np.float64)
        self.s_vel = np.zeros((N, 2), dtype=np.float64)
        self.s_freq = np.zeros(N, dtype=np.float64)
        self.s_pol = np.zeros(N, dtype=np.bool_)
        self.s_alive = np.zeros(N, dtype=np.bool_)
        self.s_locked_this_tick = np.zeros(N, dtype=np.bool_)
        self.n_alive: int = 0

        # Node arrays
        self.k_pos = np.zeros((K, 2), dtype=np.float64)
        self.k_freq = np.zeros(K, dtype=np.float64)
        self.k_pol = np.zeros(K, dtype=np.bool_)
        self.k_level = np.zeros(K, dtype=np.uint8)
        self.k_birth = np.zeros(K, dtype=np.float64)
        self.k_alive = np.zeros(K, dtype=np.bool_)
        self.k_locked_this_tick = np.zeros(K, dtype=np.bool_)

        # Composition (CSR-like)
        comp_caps = K * 4  # generous; never more than 4 indices per node in this spec
        self.k_comp_offset = np.zeros(K + 1, dtype=np.int32)
        self.k_comp_indices = np.zeros(comp_caps, dtype=np.int32)
        self.k_comp_kind = np.zeros(K, dtype=np.uint8)
        self.k_comp_used: int = 0
        self.k_count: int = 0

        self._seed()

    # ------------------------------------------------------------------ seeding

    def _seed(self) -> None:
        cfg = self.config
        n = cfg.n_initial_vibrations
        if n == 0:
            return
        self.s_pos[:n, 0] = self.rng.uniform(0.0, cfg.box_size[0], size=n)
        self.s_pos[:n, 1] = self.rng.uniform(0.0, cfg.box_size[1], size=n)
        self.s_freq[:n] = self._sample_frequencies(n)
        self.s_pol[:n] = self.rng.random(n) < cfg.polarity_split
        self.s_vel[:n] = self._sample_velocities(n)
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

    def _sample_velocities(self, n: int) -> np.ndarray:
        cfg = self.config
        speeds = self.rng.uniform(cfg.speed_min, cfg.speed_max, size=n)
        angles = self.rng.uniform(0.0, 2 * np.pi, size=n)
        v = np.empty((n, 2), dtype=np.float64)
        v[:, 0] = speeds * np.cos(angles)
        v[:, 1] = speeds * np.sin(angles)
        return v

    # --------------------------------------------------------------- allocation

    def allocate_node(
        self,
        pos: np.ndarray,
        freq: float,
        pol: bool,
        level: int,
        constituents: np.ndarray,
        comp_kind: int,
    ) -> int:
        """Append a new node. Returns its index."""
        i = self.k_count
        if i >= self.config.n_nodes_max:
            raise RuntimeError("Node capacity exhausted; increase n_nodes_max or run compaction")
        self.k_pos[i] = pos
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
        self.s_locked_this_tick[:] = False
        self.k_locked_this_tick[:] = False
```

- [ ] **Step 5: Run tests, confirm pass**

```bash
pytest tests/test_state.py -v
```

Expected: all 9 tests pass.

- [ ] **Step 6: Commit**

```bash
git add world/state.py tests/conftest.py tests/test_state.py
git commit -m "feat(state): World data model with SoA arrays and seeded vibrations"
```

---

## Task 6: Spatial hash (periodic-wrapping grid)

**Files:**
- Create: `world/spatial.py`
- Create: `tests/test_spatial.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_spatial.py`:
```python
import numpy as np
import pytest
from world.spatial import build_grid, neighbors_of, periodic_distance_sq


def test_periodic_distance_no_wrap():
    box = np.array([100.0, 100.0])
    a = np.array([10.0, 10.0])
    b = np.array([13.0, 14.0])
    d2 = periodic_distance_sq(a, b, box)
    assert d2 == pytest.approx(25.0)  # 3² + 4² = 25


def test_periodic_distance_with_wrap():
    box = np.array([100.0, 100.0])
    a = np.array([1.0, 1.0])
    b = np.array([99.0, 99.0])
    d2 = periodic_distance_sq(a, b, box)
    # Direct delta is 98, but wrap delta is 2 in each dim.
    assert d2 == pytest.approx(8.0)


def test_grid_buckets_points_correctly():
    positions = np.array([
        [5.0, 5.0],
        [12.0, 5.0],
        [5.0, 12.0],
        [95.0, 95.0],
    ])
    alive = np.array([True, True, True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    # Cell (0, 0): point 0 only.
    assert 0 in neighbors_of(grid, np.array([5.0, 5.0]), box, cell_size, exclude_self=False, query_index=-1)


def test_neighbors_within_cell_and_adjacent():
    # Two points in adjacent cells should find each other.
    positions = np.array([[5.0, 5.0], [15.0, 5.0]])  # cells (0,0) and (1,0)
    alive = np.array([True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_neighbors_across_periodic_boundary():
    # One point near each edge should be neighbors via wrap.
    positions = np.array([[1.0, 50.0], [99.0, 50.0]])
    alive = np.array([True, True])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 in nbrs


def test_dead_points_excluded():
    positions = np.array([[5.0, 5.0], [6.0, 6.0]])
    alive = np.array([True, False])
    box = np.array([100.0, 100.0])
    cell_size = 10.0
    grid = build_grid(positions, alive, box, cell_size)
    nbrs = neighbors_of(grid, positions[0], box, cell_size, exclude_self=True, query_index=0)
    assert 1 not in nbrs
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_spatial.py -v
```

Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `world/spatial.py`**

```python
from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def periodic_distance_sq(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    bx = box[0]
    by = box[1]
    if dx > bx * 0.5:
        dx -= bx
    elif dx < -bx * 0.5:
        dx += bx
    if dy > by * 0.5:
        dy -= by
    elif dy < -by * 0.5:
        dy += by
    return dx * dx + dy * dy


@njit(cache=True)
def periodic_midpoint(a: np.ndarray, b: np.ndarray, box: np.ndarray) -> np.ndarray:
    """Midpoint under minimum-image convention. Wraps result into the box."""
    out = np.empty(2, dtype=np.float64)
    for d in range(2):
        delta = b[d] - a[d]
        if delta > box[d] * 0.5:
            delta -= box[d]
        elif delta < -box[d] * 0.5:
            delta += box[d]
        m = a[d] + delta * 0.5
        # Wrap into box
        m = m % box[d]
        out[d] = m
    return out


def build_grid(
    positions: np.ndarray,
    alive: np.ndarray,
    box: np.ndarray,
    cell_size: float,
) -> dict[tuple[int, int], list[int]]:
    """Bucket alive points into a grid keyed by (cell_x, cell_y).

    Cell size should equal the maximum query radius. Returns a Python dict because
    Numba's typed.Dict is awkward across boundaries — the inner pairwise loop in
    physics.py operates on alive masks directly, this is only used for the
    neighbor-cell iteration.
    """
    grid: dict[tuple[int, int], list[int]] = {}
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    for i in range(positions.shape[0]):
        if not alive[i]:
            continue
        cx = int(positions[i, 0] // cell_size) % nx
        cy = int(positions[i, 1] // cell_size) % ny
        key = (cx, cy)
        if key not in grid:
            grid[key] = []
        grid[key].append(i)
    return grid


def neighbors_of(
    grid: dict[tuple[int, int], list[int]],
    pos: np.ndarray,
    box: np.ndarray,
    cell_size: float,
    *,
    exclude_self: bool,
    query_index: int,
) -> list[int]:
    """Return indices in the 9-cell (3×3) periodic neighborhood of `pos`."""
    nx = int(np.ceil(box[0] / cell_size))
    ny = int(np.ceil(box[1] / cell_size))
    cx = int(pos[0] // cell_size) % nx
    cy = int(pos[1] // cell_size) % ny
    out: list[int] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            key = ((cx + dx) % nx, (cy + dy) % ny)
            bucket = grid.get(key)
            if bucket is None:
                continue
            for idx in bucket:
                if exclude_self and idx == query_index:
                    continue
                out.append(idx)
    return out
```

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_spatial.py -v
```

Expected: all 6 tests pass. Numba may take 5–10 seconds to compile on first run.

- [ ] **Step 5: Commit**

```bash
git add world/spatial.py tests/test_spatial.py
git commit -m "feat(spatial): periodic-wrap distance, midpoint, and grid neighbor search"
```

---

## Task 7: Motion (`move_vibrations`)

**Files:**
- Create: `world/physics.py`
- Create: `tests/test_motion.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_motion.py`:
```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import move_vibrations


def test_motion_no_friction():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0]
    w.s_vel[0] = [3.0, 4.0]
    w.s_alive[0] = True
    w.n_alive = 1
    dt = 0.5
    n_ticks = 10
    expected_x = (10.0 + 3.0 * dt * n_ticks) % 100.0
    expected_y = (10.0 + 4.0 * dt * n_ticks) % 100.0
    for _ in range(n_ticks):
        move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), dt)
    assert w.s_pos[0, 0] == pytest.approx(expected_x)
    assert w.s_pos[0, 1] == pytest.approx(expected_y)


def test_motion_periodic_boundary_wraps():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    # Place a vibration at x=99, moving right at speed 5; in dt=1, it should land at x=4 (wrapped).
    w.s_pos[0] = [99.0, 50.0]
    w.s_vel[0] = [5.0, 0.0]
    w.s_alive[0] = True
    w.n_alive = 1
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert w.s_pos[0, 0] == pytest.approx(4.0)
    assert w.s_pos[0, 1] == pytest.approx(50.0)


def test_motion_dead_vibrations_unchanged():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [10.0, 10.0]
    w.s_vel[0] = [5.0, 5.0]
    w.s_alive[0] = False
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    assert w.s_pos[0, 0] == pytest.approx(10.0)
    assert w.s_pos[0, 1] == pytest.approx(10.0)


def test_motion_speed_unchanged_after_wrap():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=4, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    w.s_pos[0] = [99.0, 99.0]
    w.s_vel[0] = [3.0, 4.0]
    w.s_alive[0] = True
    w.n_alive = 1
    speed_before = float(np.linalg.norm(w.s_vel[0]))
    move_vibrations(w.s_pos, w.s_vel, w.s_alive, np.array(cfg.box_size), 1.0)
    speed_after = float(np.linalg.norm(w.s_vel[0]))
    assert speed_after == pytest.approx(speed_before)
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_motion.py -v
```

Expected: ImportError for `move_vibrations`.

- [ ] **Step 3: Implement `move_vibrations` in `world/physics.py`**

```python
from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def move_vibrations(
    s_pos: np.ndarray,
    s_vel: np.ndarray,
    s_alive: np.ndarray,
    box: np.ndarray,
    dt: float,
) -> None:
    """In-place: advance alive vibrations by dt with periodic-wrap into the box."""
    n = s_pos.shape[0]
    for i in range(n):
        if not s_alive[i]:
            continue
        s_pos[i, 0] = (s_pos[i, 0] + s_vel[i, 0] * dt) % box[0]
        s_pos[i, 1] = (s_pos[i, 1] + s_vel[i, 1] * dt) % box[1]
```

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_motion.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_motion.py
git commit -m "feat(physics): periodic-wrap motion update for free vibrations"
```

---

## Task 8: Vibration → electron binding

**Files:**
- Modify: `world/physics.py` — add `bind_vibrations_to_electrons`
- Create: `tests/test_binding.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_binding.py`:
```python
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import bind_vibrations_to_electrons


def _seed_two_vibrations(w: World, p1, p2, f1, f2, pol1, pol2):
    w.s_pos[0] = p1
    w.s_pos[1] = p2
    w.s_freq[0] = f1
    w.s_freq[1] = f2
    w.s_pol[0] = pol1
    w.s_pol[1] = pol2
    w.s_alive[0] = True
    w.s_alive[1] = True
    w.s_vel[0] = [0.0, 0.0]
    w.s_vel[1] = [0.0, 0.0]
    w.n_alive = 2


def test_no_binding_same_polarity(empty_world):
    w = empty_world
    # Even+even, within r_1, freq diff 8% — should NOT bind.
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1080.0, True, True)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0
    assert w.s_alive[0] and w.s_alive[1]


def test_no_binding_freq_off(empty_world):
    w = empty_world
    # Opposite polarity, within r_1, but freq diff 5% — should NOT bind.
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1050.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_no_binding_too_far(empty_world):
    w = empty_world
    # Opposite polarity, freq diff 8%, but separated by 2*r_1.
    r1 = w.config.r_1
    _seed_two_vibrations(w, [10.0, 10.0], [10.0 + 2 * r1 + 0.5, 10.0],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 0


def test_electron_forms(empty_world):
    w = empty_world
    _seed_two_vibrations(w, [10.0, 10.0], [12.0, 10.0], 1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    assert w.k_alive[0]
    assert w.k_level[0] == 1
    # Frequency adds
    assert w.k_freq[0] == pytest.approx(1000.0 + 1080.0)
    # Position is midpoint
    assert w.k_pos[0, 0] == pytest.approx(11.0)
    assert w.k_pos[0, 1] == pytest.approx(10.0)
    # Both vibrations marked dead
    assert not w.s_alive[0]
    assert not w.s_alive[1]
    # Composition: two vibration indices
    start = w.k_comp_offset[0]
    end = w.k_comp_offset[1]
    assert end - start == 2
    assert sorted(w.k_comp_indices[start:end].tolist()) == [0, 1]
    assert w.k_comp_kind[0] == 0  # 0 = constituents are vibrations


def test_electron_forms_at_periodic_boundary(empty_world):
    w = empty_world
    box = w.config.box_size
    # Two vibrations separated only by wrap.
    _seed_two_vibrations(w,
                         [box[0] - 1.0, 10.0],
                         [1.0, 10.0],
                         1000.0, 1080.0, True, False)
    bind_vibrations_to_electrons(w)
    assert w.k_count == 1
    # Midpoint under wrap should be near (0, 10) or (box[0], 10)
    mx = w.k_pos[0, 0]
    assert mx < 1.0 or mx > box[0] - 1.0


def test_polarity_randomization_at_electron_level(default_config):
    """Run a small simulation; assert both polarities appear at electron level."""
    cfg = WorldConfig(
        n_initial_vibrations=300,
        box_size=(100.0, 100.0),
        r_1=8.0,
        rng_seed=42,
    )
    w = World(cfg)
    bind_vibrations_to_electrons(w)
    if w.k_count >= 20:
        even_share = float(np.mean(w.k_pol[:w.k_count]))
        assert 0.2 < even_share < 0.8
    else:
        pytest.skip(f"Not enough electrons formed for distribution check ({w.k_count})")
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_binding.py -v
```

Expected: ImportError.

- [ ] **Step 3: Add `bind_vibrations_to_electrons` to `world/physics.py`**

Append to `world/physics.py`:
```python
import math
from world.spatial import build_grid, neighbors_of, periodic_distance_sq, periodic_midpoint


def bind_vibrations_to_electrons(world) -> int:
    """Scan alive vibrations for binding pairs. Forms electrons. Returns count formed.

    Not @njit: builds a dict-based grid and calls into the typed allocate_node.
    The inner pairwise check (distance, polarity, frequency) is still tight.
    """
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
            # Match — form an electron.
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
            break  # i is bound; move to next i

    return formed
```

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_binding.py -v
```

Expected: 6 tests pass. (`test_polarity_randomization_at_electron_level` may skip if not enough electrons form — that's acceptable for now.)

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_binding.py
git commit -m "feat(physics): vibration→electron binding with parity, distance, 8% rule"
```

---

## Task 9: Pair, triad, atom — node upgrades

**Files:**
- Modify: `world/physics.py` — add `bind_nodes_upward`
- Modify: `tests/test_binding.py` — add upgrade tests

- [ ] **Step 1: Write additional tests**

Append to `tests/test_binding.py`:
```python
from world.physics import bind_nodes_upward


def _make_electron(w: World, idx: int, pos, freq, pol):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = 1
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    if idx >= w.k_count:
        w.k_count = idx + 1
        w.k_comp_offset[idx + 1] = w.k_comp_offset[idx]


def test_pair_forms(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [13.0, 10.0], 2160.0, False)  # 8% diff
    bind_nodes_upward(w)
    # Find the new pair
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1
    p = pairs[0]
    assert w.k_freq[p] == pytest.approx(2000.0 + 2160.0)
    # Both electrons marked dead
    assert not w.k_alive[0]
    assert not w.k_alive[1]
    # Composition stores two electron indices
    start = w.k_comp_offset[p]
    end = w.k_comp_offset[p + 1]
    assert end - start == 2
    assert sorted(w.k_comp_indices[start:end].tolist()) == [0, 1]
    assert w.k_comp_kind[p] == 1  # node-level constituents


def _make_node(w: World, idx: int, pos, freq, pol, level, constituents, kind):
    w.k_pos[idx] = pos
    w.k_freq[idx] = freq
    w.k_pol[idx] = pol
    w.k_level[idx] = level
    w.k_alive[idx] = True
    w.k_birth[idx] = w.t
    n_comp = len(constituents)
    start = w.k_comp_used
    w.k_comp_indices[start:start + n_comp] = constituents
    w.k_comp_offset[idx] = start
    w.k_comp_offset[idx + 1] = start + n_comp
    w.k_comp_used = start + n_comp
    w.k_comp_kind[idx] = kind
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_triad_forms_pair_plus_electron(empty_world):
    w = empty_world
    # Two electrons → pair. Then a third electron of opposite parity to the pair.
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0], 2000.0, False)  # placeholder; will be marked dead
    _make_node(w, 2, [11.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[0] = False
    w.k_alive[1] = False
    # Third lone electron, opposite parity to the pair.
    _make_electron(w, 3, [13.0, 10.0], 4493.0, False)  # 8% above 4160
    bind_nodes_upward(w)
    triads = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 3]
    assert len(triads) == 1


def test_atom_forms_triad_plus_electron(empty_world):
    w = empty_world
    # Set up a triad and a lone electron of opposite parity.
    # Pre-populate two electrons (dead, inside the pair) and the pair (dead, inside the triad).
    _make_electron(w, 0, [10.0, 10.0], 2000.0, True)
    _make_electron(w, 1, [10.0, 10.0], 2160.0, False)
    w.k_alive[0] = False
    w.k_alive[1] = False
    _make_node(w, 2, [10.0, 10.0], 4160.0, True, level=2,
               constituents=np.array([0, 1], dtype=np.int32), kind=1)
    w.k_alive[2] = False
    _make_electron(w, 3, [10.0, 10.0], 4493.0, False)
    w.k_alive[3] = False
    _make_node(w, 4, [11.0, 10.0], 8653.0, False, level=3,  # triad, odd parity
               constituents=np.array([2, 3], dtype=np.int32), kind=1)
    # Lone electron, opposite parity (even), within r_2, 8% above the triad freq.
    _make_electron(w, 5, [12.0, 10.0], 9345.0, True)  # 8% above 8653
    bind_nodes_upward(w)
    atoms = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 4]
    assert len(atoms) == 1


def test_atom_indestructible(empty_world):
    """An atom with no neighbors stays at level 4 across many ticks."""
    from world.physics import decay_unstable_nodes
    w = empty_world
    _make_node(w, 0, [50.0, 50.0], 18000.0, True, level=4,
               constituents=np.array([0, 0], dtype=np.int32), kind=1)
    for _ in range(10000):
        decay_unstable_nodes(w, dt=1.0 / 60.0)
    assert w.k_alive[0]
    assert w.k_level[0] == 4


def test_decade_isolation(empty_world):
    w = empty_world
    # Two electrons in same decade, opposite parity, 8% diff → bind.
    _make_electron(w, 0, [10.0, 10.0], 500.0, True)
    _make_electron(w, 1, [13.0, 10.0], 540.0, False)  # 8% above 500, same decade [100,1000)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 1, "same-decade pair should form"


def test_decade_isolation_blocks_cross_decade(empty_world):
    w = empty_world
    _make_electron(w, 0, [10.0, 10.0], 9500.0, True)   # decade 3 (1e3..1e4)
    _make_electron(w, 1, [13.0, 10.0], 10260.0, False)  # decade 4 (1e4..1e5)
    bind_nodes_upward(w)
    pairs = [i for i in range(w.k_count) if w.k_alive[i] and w.k_level[i] == 2]
    assert len(pairs) == 0
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_binding.py -v
```

Expected: ImportError or AttributeError on `bind_nodes_upward`.

- [ ] **Step 3: Implement `bind_nodes_upward` in `world/physics.py`**

Append:
```python
# Pair = level 1+1 → 2; triad = level 2+1 → 3; atom = level 3+1 → 4.
_UPGRADE_TARGET = {
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
}


def _decade(freq: float) -> int:
    return int(math.floor(math.log10(freq)))


def bind_nodes_upward(world) -> int:
    """Scan alive nodes for upgrade pairs. Returns count of upgrades formed."""
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

    # Build a grid over alive nodes.
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
            # Match — upgrade.
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

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_binding.py -v
```

Expected: all tests pass. `test_atom_indestructible` requires Task 10's `decay_unstable_nodes` — if it fails with ImportError, that's the next task.

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_binding.py
git commit -m "feat(physics): node upgrades (pair, triad, atom) with decade isolation"
```

---

## Task 10: Decay (`decay_unstable_nodes`)

**Files:**
- Modify: `world/physics.py` — add `decay_unstable_nodes`
- Create: `tests/test_decay.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_decay.py`:
```python
import math
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import decay_unstable_nodes


def _seed_pair(w: World, idx: int):
    # Constituents
    w.k_alive[idx] = True
    w.k_level[idx] = 2
    w.k_pol[idx] = True
    w.k_freq[idx] = 4000.0
    w.k_pos[idx] = [50.0, 50.0]
    # Two underlying electrons stay dead inside the pair.
    e0, e1 = idx + 100, idx + 101  # dummy indices outside used range
    if e1 + 1 >= w.k_alive.shape[0]:
        return  # capacity hit
    w.k_alive[e0] = False
    w.k_alive[e1] = False
    w.k_level[e0] = 1
    w.k_level[e1] = 1
    start = w.k_comp_used
    w.k_comp_indices[start] = e0
    w.k_comp_indices[start + 1] = e1
    w.k_comp_offset[idx] = start
    w.k_comp_offset[idx + 1] = start + 2
    w.k_comp_kind[idx] = 1
    w.k_comp_used = start + 2
    if idx >= w.k_count:
        w.k_count = idx + 1


def test_pair_decays_eventually():
    """Decayed-fraction over many seeded pairs and many ticks should match 1 - exp(-t/tau)."""
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(1000.0, 1000.0),
                      n_vibrations_max=4096, n_nodes_max=1024,
                      pair_decay_time=5.0, dt=1.0 / 60.0, rng_seed=42)
    n_pairs = 200
    w = World(cfg)
    for k in range(n_pairs):
        _seed_pair(w, k)
    t_end = 5.0  # one mean lifetime
    n_ticks = int(t_end / cfg.dt)
    for _ in range(n_ticks):
        decay_unstable_nodes(w, cfg.dt)
    decayed = sum(1 for k in range(n_pairs) if not w.k_alive[k])
    expected_share = 1.0 - math.exp(-t_end / cfg.pair_decay_time)
    actual_share = decayed / n_pairs
    assert abs(actual_share - expected_share) < 0.08


def test_atom_does_not_decay():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=64, n_nodes_max=32, rng_seed=42)
    w = World(cfg)
    w.k_alive[0] = True
    w.k_level[0] = 4  # atom
    w.k_freq[0] = 18000.0
    w.k_pos[0] = [50.0, 50.0]
    w.k_count = 1
    for _ in range(10000):
        decay_unstable_nodes(w, cfg.dt)
    assert w.k_alive[0]
    assert w.k_level[0] == 4


def test_pair_decay_returns_constituents_alive():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=64, n_nodes_max=32,
                      pair_decay_time=0.001,  # decay almost immediately
                      dt=1.0 / 60.0, rng_seed=42)
    w = World(cfg)
    # Two electrons (dead, inside the pair).
    w.k_alive[0] = False
    w.k_level[0] = 1
    w.k_alive[1] = False
    w.k_level[1] = 1
    # The pair.
    w.k_alive[2] = True
    w.k_level[2] = 2
    w.k_freq[2] = 4000.0
    w.k_pos[2] = [50.0, 50.0]
    start = w.k_comp_used
    w.k_comp_indices[start] = 0
    w.k_comp_indices[start + 1] = 1
    w.k_comp_offset[2] = start
    w.k_comp_offset[3] = start + 2
    w.k_comp_kind[2] = 1
    w.k_comp_used = start + 2
    w.k_count = 3
    # Force decay quickly.
    for _ in range(1000):
        decay_unstable_nodes(w, cfg.dt)
        if not w.k_alive[2]:
            break
    assert not w.k_alive[2]
    assert w.k_alive[0]  # constituent electron came back alive
    assert w.k_alive[1]
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_decay.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `decay_unstable_nodes`**

Append to `world/physics.py`:
```python
def decay_unstable_nodes(world, dt: float) -> int:
    """Probabilistic exponential decay of pairs (level 2) and triads (level 3)."""
    cfg = world.config
    decay_time = {2: cfg.pair_decay_time, 3: cfg.triad_decay_time}
    rng = world.rng
    decayed = 0
    for i in range(world.k_count):
        if not world.k_alive[i]:
            continue
        level = int(world.k_level[i])
        if level not in (2, 3):
            continue
        tau = decay_time[level]
        p = dt / tau
        if rng.random() < p:
            world.k_alive[i] = False
            start = world.k_comp_offset[i]
            end = world.k_comp_offset[i + 1]
            for j in range(start, end):
                idx = int(world.k_comp_indices[j])
                world.k_alive[idx] = True
            decayed += 1
    return decayed
```

- [ ] **Step 4: Run tests, confirm pass**

```bash
pytest tests/test_decay.py -v
pytest tests/test_binding.py::test_atom_indestructible -v
```

Expected: all decay tests + the indestructibility test pass.

- [ ] **Step 5: Commit**

```bash
git add world/physics.py tests/test_decay.py
git commit -m "feat(physics): exponential decay for pairs and triads, atoms permanent"
```

---

## Task 11: `tick(world, dt)` — composition + compaction

**Files:**
- Modify: `world/physics.py` — add `tick`
- Modify: `world/state.py` — add `compact()`
- Create: `tests/test_tick.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_tick.py`:
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
    tick(w, 0.5)
    assert w.t == pytest.approx(1.0)


def test_tick_runs_full_default_world():
    """One tick on the default seeded world should not crash."""
    cfg = WorldConfig(rng_seed=42)
    w = World(cfg)
    tick(w, cfg.dt)
    assert w.t == pytest.approx(cfg.dt)


def test_compact_repacks_alive():
    cfg = WorldConfig(n_initial_vibrations=0, box_size=(100.0, 100.0),
                      n_vibrations_max=8, n_nodes_max=4, rng_seed=42)
    w = World(cfg)
    # Mark slots 0, 2, 4, 6 alive.
    for i in (0, 2, 4, 6):
        w.s_pos[i] = [float(i), 0.0]
        w.s_alive[i] = True
    w.n_alive = 4
    w.compact()
    # After compaction, slots 0..3 should be alive and 4..7 dead.
    assert w.s_alive[0] and w.s_alive[1] and w.s_alive[2] and w.s_alive[3]
    assert not w.s_alive[4] and not w.s_alive[5] and not w.s_alive[6] and not w.s_alive[7]
    # Positions match the originally-alive set.
    actual = sorted(w.s_pos[:4, 0].tolist())
    assert actual == [0.0, 2.0, 4.0, 6.0]
```

- [ ] **Step 2: Run, confirm failure**

```bash
pytest tests/test_tick.py -v
```

Expected: ImportError on `tick`.

- [ ] **Step 3: Implement `tick` in `world/physics.py`**

Append:
```python
def tick(world, dt: float) -> None:
    box = np.asarray(world.config.box_size, dtype=np.float64)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    world.t += dt
```

- [ ] **Step 4: Implement `World.compact` in `world/state.py`**

Append to `World`:
```python
    def compact(self) -> None:
        """Pack alive vibrations into the front of the array. Node compaction is deferred."""
        alive_idx = np.where(self.s_alive)[0]
        n = len(alive_idx)
        if n == 0:
            self.s_pos[:] = 0
            self.s_vel[:] = 0
            self.s_freq[:] = 0
            self.s_pol[:] = False
            self.s_alive[:] = False
            self.n_alive = 0
            return
        self.s_pos[:n] = self.s_pos[alive_idx]
        self.s_vel[:n] = self.s_vel[alive_idx]
        self.s_freq[:n] = self.s_freq[alive_idx]
        self.s_pol[:n] = self.s_pol[alive_idx]
        self.s_alive[:n] = True
        self.s_alive[n:] = False
        self.n_alive = n
```

- [ ] **Step 5: Run tests, confirm pass**

```bash
pytest tests/test_tick.py tests/ -v
```

Expected: all tests across all files pass.

- [ ] **Step 6: Commit**

```bash
git add world/physics.py world/state.py tests/test_tick.py
git commit -m "feat(physics): tick() composing motion, binding, decay; vibration compaction"
```

---

## Task 12: Renderer scaffold

**Files:**
- Create: `world/render.py`

- [ ] **Step 1: Implement renderer skeleton**

```python
"""Pygame renderer. Reads World state; never mutates it."""
from __future__ import annotations
import math
import numpy as np
import pygame

BG_COLOR = (14, 14, 20)
COLOR_VIBR_EVEN = (74, 144, 226)   # #4A90E2
COLOR_VIBR_ODD = (231, 76, 60)     # #E74C3C
COLOR_ELECTRON = (243, 156, 18)    # #F39C12
COLOR_ATOM = (255, 255, 255)
COLOR_LINE_PAIR = (204, 204, 204, 128)
COLOR_LINE_TRIAD = (220, 220, 220, 200)
COLOR_LINE_ATOM = (255, 240, 200, 255)

WINDOW_SIZE = (1024, 1024)
MARGIN = 12


class Renderer:
    def __init__(self, world):
        self.world = world
        pygame.init()
        pygame.display.set_caption("World of Vibrations")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Menlo,Monaco,Consolas,monospace", 14)
        self.line_surf = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        self._build_atom_halo()
        self.viewport_w = WINDOW_SIZE[0] - 2 * MARGIN
        self.viewport_h = WINDOW_SIZE[1] - 2 * MARGIN
        self.scale_x = self.viewport_w / world.config.box_size[0]
        self.scale_y = self.viewport_h / world.config.box_size[1]
        self.fps = 60.0

    def _build_atom_halo(self) -> None:
        size = 64
        self.halo = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        for y in range(size):
            for x in range(size):
                d = math.hypot(x - cx, y - cy)
                if d > cx:
                    continue
                alpha = max(0, int(180 * (1 - d / cx) ** 2))
                self.halo.set_at((x, y), (255, 220, 160, alpha))

    def world_to_screen(self, pos: np.ndarray) -> tuple[int, int]:
        return (
            int(MARGIN + pos[0] * self.scale_x),
            int(MARGIN + pos[1] * self.scale_y),
        )

    def draw(self) -> None:
        w = self.world
        self.screen.fill(BG_COLOR)
        self.line_surf.fill((0, 0, 0, 0))
        self._draw_lines(w)
        self.screen.blit(self.line_surf, (0, 0))
        self._draw_vibrations(w)
        self._draw_nodes(w)
        self._draw_stats(w)
        pygame.display.flip()
        self.fps = self.clock.get_fps() or self.fps
        self.clock.tick(60)

    def _draw_vibrations(self, w) -> None:
        for i in range(w.s_pos.shape[0]):
            if not w.s_alive[i]:
                continue
            color = COLOR_VIBR_EVEN if w.s_pol[i] else COLOR_VIBR_ODD
            r = max(2, int(math.log10(max(w.s_freq[i], 10.0)) - 1))
            pygame.draw.circle(self.screen, color, self.world_to_screen(w.s_pos[i]), r)

    def _draw_nodes(self, w) -> None:
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            pos = self.world_to_screen(w.k_pos[i])
            if level == 1:
                pygame.draw.circle(self.screen, COLOR_ELECTRON, pos, 5)
            elif level == 4:
                hx, hy = pos
                self.screen.blit(self.halo, (hx - 32, hy - 32),
                                 special_flags=pygame.BLEND_RGBA_ADD)
                pygame.draw.circle(self.screen, COLOR_ATOM, pos, 7)

    def _draw_lines(self, w) -> None:
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            if level not in (2, 3, 4):
                continue
            color = {
                2: COLOR_LINE_PAIR,
                3: COLOR_LINE_TRIAD,
                4: COLOR_LINE_ATOM,
            }[level]
            ground = self._ground_electron_positions(w, i)
            for a in range(len(ground)):
                for b in range(a + 1, len(ground)):
                    pa = self.world_to_screen(ground[a])
                    pb = self.world_to_screen(ground[b])
                    pygame.draw.line(self.line_surf, color, pa, pb, 1)

    def _ground_electron_positions(self, w, i: int) -> list[np.ndarray]:
        """Walk composition one indirection deep to gather electron positions."""
        out: list[np.ndarray] = []
        start = int(w.k_comp_offset[i])
        end = int(w.k_comp_offset[i + 1])
        if int(w.k_comp_kind[i]) == 0:
            return [w.k_pos[i].copy()]  # electron — its own position
        for j in range(start, end):
            child = int(w.k_comp_indices[j])
            child_level = int(w.k_level[child])
            if child_level == 1:
                out.append(w.k_pos[child].copy())
            else:
                # Recurse one more level (atoms have triad inside; pairs/triads have electrons).
                out.extend(self._ground_electron_positions(w, child))
        return out

    def _draw_stats(self, w) -> None:
        n_v = int(w.n_alive)
        n_e = int(np.sum((w.k_level[:w.k_count] == 1) & w.k_alive[:w.k_count]))
        n_p = int(np.sum((w.k_level[:w.k_count] == 2) & w.k_alive[:w.k_count]))
        n_t = int(np.sum((w.k_level[:w.k_count] == 3) & w.k_alive[:w.k_count]))
        n_a = int(np.sum((w.k_level[:w.k_count] == 4) & w.k_alive[:w.k_count]))
        text = (f"t = {w.t:7.2f} s | FPS {self.fps:4.0f} | "
                f"vibr {n_v:5d} | e- {n_e:4d} | pair {n_p:4d} | "
                f"triad {n_t:4d} | atom {n_a:4d}")
        surf = self.font.render(text, True, (230, 230, 230))
        self.screen.blit(surf, (MARGIN, MARGIN // 2))

    def close(self) -> None:
        pygame.quit()
```

- [ ] **Step 2: Manual smoke test**

```bash
python -c "
from world.config import WorldConfig
from world.state import World
from world.render import Renderer
import pygame, sys

cfg = WorldConfig()
w = World(cfg)
r = Renderer(w)
for _ in range(60):
    r.draw()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            r.close()
            sys.exit(0)
r.close()
"
```

Expected: a window opens for ~1 second showing 1000 colored dots, then closes. No exceptions.

- [ ] **Step 3: Commit**

```bash
git add world/render.py
git commit -m "feat(render): Pygame renderer with vibrations, electrons, atoms, halos, stats"
```

---

## Task 13: CLI (`world/run.py`)

**Files:**
- Create: `world/run.py`

- [ ] **Step 1: Implement CLI**

```python
"""CLI entry point for the World of Vibrations simulation."""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
import numpy as np

from world.config import WorldConfig, load_config
from world.state import World
from world.physics import tick


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="world", description="World of Vibrations")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run the simulation")
    run.add_argument("--config", type=Path, default=None,
                     help="TOML override file for WorldConfig")
    run.add_argument("--headless", action="store_true",
                     help="run without opening a Pygame window")
    run.add_argument("--duration", type=float, default=None,
                     help="seconds of simulated time (headless only)")
    run.add_argument("--snapshot-every", type=float, default=None,
                     help="print stats line every N simulated seconds (headless)")
    run.add_argument("--save", type=Path, default=None,
                     help="write final state to NPZ on exit")
    run.add_argument("--seed", type=int, default=None, help="override rng_seed")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    if args.seed is not None:
        from dataclasses import replace
        cfg = replace(cfg, rng_seed=args.seed)
    world = World(cfg)

    if args.headless:
        return _run_headless(world, cfg, args)
    return _run_window(world, cfg)


def _run_headless(world: World, cfg: WorldConfig, args) -> int:
    duration = args.duration if args.duration is not None else 60.0
    n_ticks = int(duration / cfg.dt)
    snap_step = int(args.snapshot_every / cfg.dt) if args.snapshot_every else None
    start = time.time()
    for k in range(n_ticks):
        tick(world, cfg.dt)
        if snap_step and (k + 1) % snap_step == 0:
            _print_stats(world)
    wall = time.time() - start
    print(f"# done — {duration:.1f} simulated s in {wall:.1f} wall s "
          f"({duration / wall:.1f}× real-time)")
    _print_stats(world)
    if args.save:
        _save_state(world, args.save)
    return 0


def _run_window(world: World, cfg: WorldConfig) -> int:
    import pygame
    from world.render import Renderer
    renderer = Renderer(world)
    paused = False
    try:
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return 0
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        return 0
                    if ev.key == pygame.K_SPACE:
                        paused = not paused
                    if ev.key == pygame.K_r:
                        world = World(cfg)
                        renderer.world = world
                        paused = False
            if not paused:
                tick(world, cfg.dt)
            renderer.draw()
    finally:
        renderer.close()


def _print_stats(world: World) -> None:
    n_v = int(world.n_alive)
    n_e = int(np.sum((world.k_level[:world.k_count] == 1) & world.k_alive[:world.k_count]))
    n_p = int(np.sum((world.k_level[:world.k_count] == 2) & world.k_alive[:world.k_count]))
    n_t = int(np.sum((world.k_level[:world.k_count] == 3) & world.k_alive[:world.k_count]))
    n_a = int(np.sum((world.k_level[:world.k_count] == 4) & world.k_alive[:world.k_count]))
    print(f"t = {world.t:7.2f} | vibr {n_v:5d} | e- {n_e:4d} | "
          f"pair {n_p:4d} | triad {n_t:4d} | atom {n_a:4d}")


def _save_state(world: World, path: Path) -> None:
    np.savez(path,
             s_pos=world.s_pos, s_vel=world.s_vel, s_freq=world.s_freq,
             s_pol=world.s_pol, s_alive=world.s_alive,
             k_pos=world.k_pos, k_freq=world.k_freq, k_pol=world.k_pol,
             k_level=world.k_level, k_birth=world.k_birth, k_alive=world.k_alive,
             k_comp_offset=world.k_comp_offset, k_comp_indices=world.k_comp_indices,
             k_comp_kind=world.k_comp_kind, t=world.t)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke test the CLI**

```bash
python -m world run --headless --duration 5 --snapshot-every 1
```

Expected: prints periodic stats, ends with summary; takes a few seconds; no errors.

- [ ] **Step 3: Commit**

```bash
git add world/run.py
git commit -m "feat(cli): run subcommand with --headless, --duration, --save, --seed"
```

---

## Task 14: Calibration smoke test

**Files:**
- Create: `tests/calibration_smoke.py`

- [ ] **Step 1: Write smoke test**

```python
"""60-second headless smoke test against INITIAL_CONFIG. Excluded from default pytest."""
from __future__ import annotations
import sys
import numpy as np
from world.config import INITIAL_CONFIG
from world.state import World
from world.physics import tick


def main() -> int:
    cfg = INITIAL_CONFIG
    w = World(cfg)
    duration = 60.0
    n_ticks = int(duration / cfg.dt)
    seen = {1: 0, 2: 0, 3: 0, 4: 0}
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        for level in (1, 2, 3, 4):
            seen[level] = max(seen[level],
                              int(np.sum((w.k_level[:w.k_count] == level) &
                                         w.k_alive[:w.k_count])))
    print(f"max counts: e- {seen[1]} | pair {seen[2]} | triad {seen[3]} | atom {seen[4]}")
    failures = []
    if seen[1] < 1: failures.append("no electrons formed")
    if seen[2] < 1: failures.append("no pairs formed")
    if seen[3] < 1: failures.append("no triads formed")
    # Atoms intentionally not asserted — that's the calibration target.
    if failures:
        print("FAIL:", "; ".join(failures))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run smoke test**

```bash
python tests/calibration_smoke.py
```

Expected: prints max counts, exits 0 if at least one electron, pair, and triad were observed. If it fails, the calibration phase begins — adjust `r_1`, `r_2`, decay times via TOML override, log results in `LOGBOOK.md`. **Failure here does not block the plan from being marked complete; it kicks off the calibration phase.**

- [ ] **Step 3: Commit**

```bash
git add tests/calibration_smoke.py
git commit -m "test(smoke): 60-second headless calibration smoke test"
```

---

## Task 15: LOGBOOK.md template + first session entry

**Files:**
- Create: `LOGBOOK.md`
- Create: `docs/logbook/.gitkeep`

- [ ] **Step 1: Write LOGBOOK.md template**

```markdown
# World of Vibrations — Logbook

Research diary. Each session is one entry. Document what you ran, what you observed, what you adjusted, what you learned. Screenshots go under `docs/logbook/`.

---

## 2026-05-05 — Session 1: Plan complete, build complete, first smoke run

- **Config:** defaults (`INITIAL_CONFIG`, see `world/config.py`)
- **Run:** `python tests/calibration_smoke.py`
- **Observation:** [fill in after first run — max counts of e-, pair, triad, atom]
- **Hypotheses if smoke fails:**
  - Too few electrons → raise `r_1` and/or `freq_tolerance`
  - Electrons but no pairs → raise `r_2`
  - Pairs but no triads → raise `pair_decay_time` (pairs decaying before triad-forming partner shows up)
  - Triads but no atoms → raise `triad_decay_time` and/or `r_2`
- **Next:** [TBD — adjust one parameter at a time, save calibration TOML files numbered v1, v2, ...]
```

- [ ] **Step 2: Create logbook screenshot directory**

```bash
mkdir -p docs/logbook
touch docs/logbook/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
git add LOGBOOK.md docs/logbook/.gitkeep
git commit -m "docs: logbook template with first session entry placeholder"
```

---

## Task 16: Final acceptance check

**Files:** none — verification only.

- [ ] **Step 1: Run full test suite**

```bash
pytest -v
```

Expected: all 13+ tests across `test_config`, `test_state`, `test_spatial`, `test_motion`, `test_binding`, `test_decay`, `test_tick` pass.

- [ ] **Step 2: Verify spec acceptance criteria from §14**

```bash
# 1. Window mode opens, vibrations move, etc.  (manual — exit with Esc)
python -m world run

# 2. Headless mode runs to completion
python -m world run --headless --duration 60 --snapshot-every 10

# 3. Test suite passes
pytest

# 4. Calibration smoke
python tests/calibration_smoke.py

# 5. German originals preserved
ls files/*.de.md
# Expected: README.de.md, SKILL.de.md, SPEZIFIKATION.de.md

# 6. LOGBOOK exists with entry
head -20 LOGBOOK.md
```

Expected: each command runs without error. Window-mode test is manual.

- [ ] **Step 3: Update LOGBOOK with first observations**

Edit `LOGBOOK.md` Session 1 entry with the actual smoke-test numbers. Add a hypothesis about whether atoms will form with default config or whether calibration is needed.

- [ ] **Step 4: Final commit**

```bash
git add LOGBOOK.md
git commit -m "docs(logbook): record first observations from default-config smoke run"
git log --oneline | head -20
```

Expected: 16 task-commits plus the initial spec/skeleton commits.

---

## Self-review notes

Spec coverage check:

| Spec section | Covered by task |
|---|---|
| §2 Resolutions | Tasks 8, 9 (random parity at formation, level-based upgrade rules) |
| §4 Project layout | Tasks 0, 4, 5, 6, 7, 12, 13 |
| §5 Data model | Tasks 4, 5, 11 (compact) |
| §6 Main loop | Tasks 7, 8, 9, 10, 11 |
| §7 Renderer | Task 12 |
| §8 Configuration & CLI | Tasks 4, 13 |
| §9 Bootstrap | Tasks 0, 1, 2, 3 |
| §10 Tests | Tasks 4, 5, 6, 7, 8, 9, 10, 11 |
| §10.1 Calibration smoke | Task 14 |
| §11 Logbook | Task 15 |
| §12 Implementation order | Tasks 4–11 follow §12 step ordering (steps 1–5 of the source checklist) |
| §13 Out of scope | enforced by absence of tasks for higher hierarchies, threading, GPU, 3D |
| §14 Acceptance | Task 16 |

No placeholders. All function names match across tasks (`bind_vibrations_to_electrons`, `bind_nodes_upward`, `decay_unstable_nodes`, `tick`, `compact`).
