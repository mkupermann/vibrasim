# Phase 1 v2 — 3D Substrate and Risk-Mitigation Design Specification

**Status:** Draft for review
**Date:** 2026-05-05
**Source documents:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 (the conceptual paper this spec implements)
**Supersedes:** Phase 1 v1 design at [`2026-05-05-world-of-vibrations-design.md`](2026-05-05-world-of-vibrations-design.md)

**Scope:** Migrate the existing 2D Phase 1 implementation to the 3D substrate of CONCEPT.md v2 (§4.1), implement scale separation through repulsion (§4.6), implement ambient regeneration (§4.7), replace the live Pygame renderer with a decoupled Open3D preview + headless Blender Cycles keyframe pipeline (§7.1), build the parameter sweep harness with Optuna backend (§7.4), and add a frequency-histogram observation tool. Phases 2–8 are out of scope.

---

## 1. Goal

Bring the simulation to a state in which:

1. The substrate is three-dimensional with periodic boundaries on all three axes.
2. The four foundational laws of CONCEPT.md v2 §4 are all implemented (motion, binding, hierarchical formation, scale separation through repulsion).
3. The §4.7 ambient regeneration mechanism is in place, maintaining steady-state vibration density.
4. Physics is fully decoupled from rendering: headless tick + snapshot files; live preview via Open3D; high-quality keyframes via headless Blender Cycles.
5. A calibration harness can sweep the parameter space programmatically, with both grid/random search and Optuna backends.
6. A frequency-histogram observation tool reads any snapshot and produces per-level frequency distributions.

This satisfies CONCEPT.md v2 Phase 1 success criteria (§5 Phase 1, v2) — atoms reproducibly form, scale-separation by frequency decade is observable, ambient density holds within ±20 % of seeded value over a one-hour calibration run.

## 2. Architectural decisions

| Decision | Choice | Why |
|---|---|---|
| Forward migration vs side-by-side | Forward migrate: 3D replaces 2D in `world/`. Old code lives in git history. | Keeps the package focused. The 2D version was a stepping stone; v2 closes the open spec questions. |
| Position arrays | `float64[N, 3]` everywhere | Cache-friendly, NumPy-natural, Numba-compatible |
| Spatial hash | 3D periodic-wrap grid, 27 neighbour cells per query | Direct generalisation of v1's 2D grid |
| Ambient regeneration | Per-tick Poisson generation of new vibrations + per-tick Poisson decay of unstable nodes back to free vibrations | Conservation-respecting (§4.7); two new parameters `lambda_gen`, `lambda_dec` |
| Live preview | Open3D, ~10 fps polling, separate process or thread | Sanity-check long calibration runs without coupling to the tick loop |
| Keyframe rendering | Headless Blender Cycles, scene constructed from snapshot NPZ | Publication-grade output, decoupled from physics |
| Snapshot format | NPZ files, timestamped (`snapshot_t000123.5.npz`) | NumPy-native, zero-config, re-loadable for re-rendering |
| Parameter sweep | Multi-process worker pool, JSON-line result log, optional Optuna integration | Simple now, smart later |
| Pygame | Removed. The live preview is now Open3D; Pygame is no longer a dependency. | One renderer is enough. |

## 3. Project layout (changes from v1)

```
EQMOD/
├── world/
│   ├── __init__.py
│   ├── state.py              # 3D arrays; new ambient parameters; node decay-back-to-vibrations
│   ├── physics.py            # 3D motion, binding, decay, scale repulsion, ambient regeneration
│   ├── spatial.py            # 3D periodic-wrap grid, 27-cell neighbour iteration, 3D distance/midpoint
│   ├── config.py             # WorldConfig with 3D box_size, lambda_gen, lambda_dec, repulsion_k
│   ├── snapshot.py           # NEW — write/read snapshot NPZ files
│   ├── preview.py            # NEW — Open3D live preview (replaces Pygame render.py)
│   └── run.py                # CLI: headless run with snapshot intervals, optional --preview flag
├── tools/                    # NEW directory — non-package Python scripts
│   ├── render_blender.py     # NEW — Blender Cycles keyframe renderer (invoked via blender --python ...)
│   ├── sweep.py              # NEW — parameter sweep harness, grid + random + Optuna backends
│   ├── histogram.py          # NEW — read a snapshot, print/plot frequency histograms per level
│   └── compare_runs.py       # NEW — compare snapshots across runs (max counts, time-to-first-atom)
├── tests/
│   ├── test_state.py         # updated for 3D + ambient
│   ├── test_spatial.py       # updated for 3D 27-cell grid
│   ├── test_motion.py        # updated for 3D
│   ├── test_binding.py       # updated for 3D
│   ├── test_decay.py         # updated for 3D + ambient regeneration
│   ├── test_repulsion.py     # NEW — scale repulsion tests
│   ├── test_ambient.py       # NEW — ambient regeneration / decay tests
│   ├── test_snapshot.py      # NEW — snapshot round-trip tests
│   ├── test_sweep.py         # NEW — sweep-harness tests
│   └── test_tick.py          # composition test, 3D world
├── pyproject.toml            # add open3d, optuna; remove pygame
└── docs/
    └── superpowers/specs/    # this spec lives here
```

The `render.py` file (Pygame 2D renderer) is removed; the `world/preview.py` Open3D version takes its place. The `world/__main__.py` shim stays.

## 4. Substrate changes (`world/state.py`, `world/spatial.py`)

### 4.1 Position and velocity arrays

```python
s_pos    : float64[N_max, 3]    # 3D position
s_vel    : float64[N_max, 3]    # 3D velocity
s_freq   : float64[N_max]
s_pol    : bool[N_max]
s_alive  : bool[N_max]
```

Node arrays similarly: `k_pos: float64[K_max, 3]`, `k_vel: float64[K_max, 3]` (now needed because nodes can be moved by repulsion; in v1 nodes were stationary, in v2 they can drift apart).

### 4.2 Box and periodic boundaries

`WorldConfig.box_size` becomes `tuple[float, float, float]` defaulting to `(1000.0, 1000.0, 1000.0)`. All distance, midpoint, and motion functions wrap on three axes.

### 4.3 Spatial hash (3D)

Cell grid is 3D. `build_grid` keys by `(cx, cy, cz)`. `neighbors_of` iterates the 27 surrounding cells (3³) with periodic wrap on all three axes. `periodic_distance_sq` and `periodic_midpoint` operate on length-3 arrays.

### 4.4 Seeding

Vibrations seeded uniformly in the 3D box volume; velocities sampled with isotropic 3D directions (random spherical angles instead of 2D angle).

## 5. Scale separation through repulsion (`world/physics.py`)

### 5.1 Force law

Per CONCEPT.md v2 §4.6:

```
F_ij = -k · (frequency_ratio_ij - 1000) / r_ij²    if  ratio_ij > 1000
F_ij = 0                                           otherwise
```

where `frequency_ratio_ij = max(f_i, f_j) / min(f_i, f_j)`, and the force acts along the unit vector from *j* to *i* (repulsive). New configuration parameter: `repulsion_k: float = 100.0`.

### 5.2 Implementation

A new tick step `apply_scale_repulsion(world, dt)`:

1. Build a coarser spatial grid (cell size = a tunable `repulsion_cell_size`, default 100 — much larger than `r_2` because repulsion acts at long range when frequency ratios are extreme).
2. For each alive node *i*, accumulate force contributions from neighbours *j* with `freq_ratio_ij > 1000`.
3. Update node velocity and position: `v_i += F_i * dt / m_i; pos_i += v_i * dt`. Node "mass" `m_i` is taken proportional to `k_level` (electron = 1, pair = 2, triad = 3, atom = 4) — heavier nodes move less under the same force.

Atoms are not exempt; they participate in repulsion.

### 5.3 Ordering in `tick()`

The tick step list expands to:

```
1. move_vibrations(...)               # 3D motion of free vibrations
2. apply_scale_repulsion(...)         # repulsive force on nodes (NEW)
3. move_nodes(...)                    # nodes advance their accumulated velocity (NEW)
4. bind_vibrations_to_electrons(...)  # 3D binding scan
5. bind_nodes_upward(...)             # 3D binding scan, decade rule
6. decay_unstable_nodes(...)          # exponential decay of pairs/triads
7. ambient_regeneration(...)          # NEW — see §6
8. world.t += dt
```

### 5.4 Tests (`tests/test_repulsion.py`)

| Test | Asserts |
|---|---|
| `test_no_force_below_threshold` | Two nodes with `freq_ratio < 1000` feel zero repulsive force |
| `test_repulsion_above_threshold` | Two nodes with `freq_ratio = 2000` move apart over many ticks |
| `test_repulsion_strength_scales_with_ratio` | Force at `ratio=2000` is stronger than at `ratio=1100` |
| `test_repulsion_inverse_square` | At fixed ratio, force at distance `2d` is one-quarter the force at distance `d` |
| `test_repulsion_periodic_wrap` | Two nodes near opposite faces of the 3D box repel through the wrap, not through the long path |
| `test_atom_not_exempt_from_repulsion` | An atom and a vibration cluster of much smaller frequency drift apart over time |
| `test_repulsion_with_h2_smoke` | After a 1-hour calibration run, electrons and atoms cluster spatially by frequency decade — `floor(log10(freq))` is a significant predictor of position quadrant |

## 6. Ambient regeneration (`world/physics.py`)

### 6.1 Generation

Per tick, draw `n_new = Poisson(lambda_gen * volume * dt)` new vibrations. Each new vibration is placed uniformly at random in the 3D box, with frequency drawn from the same distribution as the seeding (`freq_distribution` parameter), polarity 50/50, and an isotropically sampled velocity in `[speed_min, speed_max]`.

If allocation would exceed `n_vibrations_max`, drop the surplus and warn (in the snapshot or log).

### 6.2 Decay back to vibrations

For every alive node with level ∈ {1, 2, 3} (i.e. electrons, pairs, triads — atoms exempt), draw per tick from a Bernoulli with `p = lambda_dec * dt`. On decay:

- Mark `k_alive[i] = False`.
- For each constituent index in the CSR slice, mark it alive again (recursively if the constituent is itself a node — this is the standard cascade decay).
- For an electron specifically, the decay restores its two source vibrations to `s_alive = True` at the electron's last position with random thermal velocity in `[speed_min, speed_max]`.

This is in addition to the existing per-tick decay rates `pair_decay_time` and `triad_decay_time` from v1; `lambda_dec` provides a second, much slower channel that also drains electrons (which v1 did not).

### 6.3 Conservation accounting

Two new measurements per snapshot, exposed in the stats line:

- `total_vibrations` = `sum(s_alive) + 2 * sum(k_alive[k_level == 1]) + 4 * sum(k_alive[k_level == 2]) + 6 * sum(k_alive[k_level == 3]) + 8 * sum(k_alive[k_level == 4])`
- `ambient_density` = `sum(s_alive) / volume`

These let the calibration loop assert "ambient density holds within ±20 % of seeded value over the run".

### 6.4 Tests (`tests/test_ambient.py`)

| Test | Asserts |
|---|---|
| `test_no_ambient_with_zero_lambda` | With `lambda_gen = 0` and `lambda_dec = 0`, total vibration count is conservatively unchanged over 1000 ticks (no electron→vibration channel active) |
| `test_generation_rate_matches_lambda` | With `lambda_gen = 0.001`, average new vibrations per tick over 1000 ticks matches `lambda_gen * volume * dt` within 5 % |
| `test_decay_rate_matches_lambda` | Seed 200 electrons. Run with `lambda_dec = 0.01`. Decayed-fraction over time matches `1 - exp(-t * lambda_dec)` within 5 % |
| `test_atoms_immune_to_ambient_decay` | An atom does not decay under any value of `lambda_dec` |
| `test_steady_state_density` | With seeded equilibrium params (calibration target) the ambient density at t=300 s is within ±10 % of t=0 |
| `test_capacity_overflow_safe` | When `n_vibrations_max` is reached, generation drops the surplus without crashing and reports it |

## 7. Snapshot format (`world/snapshot.py`)

A snapshot is a NumPy `.npz` archive containing every world array plus metadata.

### 7.1 File naming

`snapshot_t{simulated_time:09.2f}.npz` — e.g. `snapshot_t0000123.50.npz`. Lexicographic sort gives chronological order.

### 7.2 Contents

- All arrays from `World`: `s_pos`, `s_vel`, `s_freq`, `s_pol`, `s_alive`, `s_locked_this_tick`; `k_pos`, `k_vel`, `k_freq`, `k_pol`, `k_level`, `k_birth`, `k_alive`, `k_locked_this_tick`; `k_comp_offset`, `k_comp_indices`, `k_comp_kind`.
- `n_alive`, `k_count`, `k_comp_used`, `t`.
- `config_dict` — dataclass-as-dict serialisation of the `WorldConfig` used for this run.
- `meta` — git commit SHA, timestamp, software version.

### 7.3 API

```python
def save_snapshot(world: World, path: Path) -> None: ...
def load_snapshot(path: Path) -> World: ...
```

`load_snapshot` returns a new `World` instance with arrays restored. `t`, `n_alive`, `k_count`, `k_comp_used` are restored from the archive.

### 7.4 CLI integration

`world run --headless --duration 60 --snapshot-every 5 --snapshot-dir ./snapshots/run-001/` writes a snapshot every 5 simulated seconds.

### 7.5 Tests (`tests/test_snapshot.py`)

| Test | Asserts |
|---|---|
| `test_round_trip` | Save a world, load it, every array is bit-identical |
| `test_filename_chronological_sort` | Snapshots at t=1, t=10, t=100 sort in chronological order |
| `test_metadata_preserved` | `config_dict` round-trips; `t` is restored |
| `test_compaction_safe_after_load` | A loaded world can run `tick()` without crashing |

## 8. Live preview (`world/preview.py`)

### 8.1 Open3D viewer

A separate process polls a shared shared-memory or file-watcher reference to the latest snapshot. Renders:

- Vibrations as small spheres, colour by polarity (blue/red), radius scaled by `log10(freq)`.
- Electrons as orange spheres with emissive material.
- Pairs/triads as connecting tubes (thin cylinder primitives).
- Atoms as bright white spheres with halo (point-light + glow).

Camera defaults to a 3D orbit. User can rotate/zoom interactively.

### 8.2 Performance target

10 fps is plenty. The preview is for sanity-checking long runs, not for primary observation.

### 8.3 Lifecycle

`world run --preview` starts the simulation and the preview side by side. Closing the preview window does not stop the simulation. Closing the simulation stops both.

### 8.4 Tests

Snapshot of the rendering itself is hard to test programmatically. We verify only that:

- `world/preview.py` imports cleanly (`pytest tests/test_preview_imports.py`).
- The preview process starts and exits cleanly when given a valid world (manual smoke).

## 9. Keyframe rendering (`tools/render_blender.py`)

### 9.1 Pipeline

```bash
blender -b -P tools/render_blender.py -- --snapshot snapshots/run-001/snapshot_t0000300.00.npz \
                                          --output renders/run-001/keyframe-0300.png \
                                          --quality high
```

The `tools/render_blender.py` script is invoked inside Blender's bundled Python interpreter:

1. Parse arguments after the `--` separator.
2. Load the snapshot NPZ.
3. Construct the Blender scene programmatically:
   - Camera at a configurable position, pointing at the box centre.
   - Three-point lighting (key, fill, rim) — soft area lights.
   - One mesh per node level: instanced spheres for vibrations and electrons, mesh tubes for pairs/triads, glowing emissive spheres for atoms.
   - Materials: PBR with subtle subsurface scattering for the bound-node spheres; the ambient vibration field can be visualised as a faint volumetric.
   - Render output directory configurable.
4. Set Cycles renderer, sample count from `--quality` flag (`low=64, medium=256, high=1024, paper=4096`).
5. Render and save.

### 9.2 Batch mode

For rendering all snapshots in a run as a video frame sequence:

```bash
tools/render_blender_batch.sh snapshots/run-001/ renders/run-001/ --quality medium
```

This wraps a loop calling `tools/render_blender.py` per snapshot.

### 9.3 Tests

Blender pipeline is hard to unit-test (requires the Blender binary). The script is exercised via:

- `tests/test_render_blender_smoke.py` — checks the script parses arguments correctly when invoked with `--help` (no Blender required for this).
- A manual check during the implementation: render one keyframe at `--quality low` to verify the full pipeline.

## 10. Parameter sweep harness (`tools/sweep.py`)

### 10.1 Backends

Two interchangeable backends, selected by flag:

- `--backend grid` — Cartesian product of named parameter ranges
- `--backend random` — random sampling over named ranges
- `--backend optuna` — Bayesian optimisation; needs `--objective` flag specifying the score function

### 10.2 Objective functions (named registry)

Phase 1 v2 ships with three objectives:

- `time_to_first_atom` — minimise the simulated-time at which the first atom forms
- `spatial_sorting_score` — maximise the predictivity of `floor(log10(freq))` for spatial position quadrant after a 1-hour run (Hypothesis H2 measurement)
- `ambient_density_stability` — maximise `1 - max_deviation_from_seed / seed_density` over the run

Phases 2+ register additional objectives.

### 10.3 Worker model

Each parameter configuration runs in a separate Python process (parallel via `multiprocessing.Pool`). Each worker:

1. Constructs the `World` from the parameter dict.
2. Runs headless for the configured duration.
3. Computes the objective from the final state and any periodic measurements.
4. Writes one JSON line to the result log: `{"params": {...}, "objective": 0.74, "duration_s": 60.0, "wall_s": 8.4, "snapshot_path": "..."}`.

### 10.4 Optuna integration

When `--backend optuna`:

- Each worker is one trial.
- Optuna study persists in SQLite (`sweep_study.db`) so sweeps can be resumed.
- Search space defined by per-parameter bounds in the config TOML.

### 10.5 CLI

```bash
tools/sweep.py --backend grid --params r_2,freq_tolerance \
               --r_2 10:50:5 --freq_tolerance 0.005:0.025:0.005 \
               --duration 60 --workers 8 --output sweeps/sweep-2026-05-05/

tools/sweep.py --backend optuna --objective spatial_sorting_score \
               --bounds-toml sweeps/h2-bounds.toml \
               --trials 200 --workers 8 --output sweeps/h2-2026-05-12/
```

### 10.6 Tests (`tests/test_sweep.py`)

| Test | Asserts |
|---|---|
| `test_grid_enumeration` | Grid backend with ranges `[1,2,3]` × `[A,B]` produces exactly 6 configurations |
| `test_random_backend_n_trials` | Random backend with `--trials 50` produces exactly 50 |
| `test_objective_time_to_first_atom_returns_finite` | On a hand-tuned productive config, `time_to_first_atom` returns a finite value < duration |
| `test_objective_inf_when_atom_never_forms` | On default config (known to not produce atoms), the objective returns `inf` |
| `test_worker_isolation` | Two parallel workers with the same seed produce the same world (no shared state leakage) |
| `test_resume_optuna_study` | Optuna study with 50 trials saved, reopened, can resume to 100 |

## 11. Frequency-histogram observation tool (`tools/histogram.py`)

### 11.1 What it produces

Given a snapshot NPZ:

- A per-level frequency histogram (vibrations, electrons, pairs, triads, atoms) with logarithmic bins matching the decade rule.
- A spatial-density heatmap projected onto each of the three coordinate planes.
- A summary table: count and mean frequency per level.

### 11.2 Output formats

`--format text` prints to stdout (for LOGBOOK paste-in). `--format png` saves a multi-panel matplotlib figure. `--format json` machine-readable.

### 11.3 CLI

```bash
tools/histogram.py snapshots/run-001/snapshot_t0003600.00.npz --format text
tools/histogram.py snapshots/run-001/snapshot_t0003600.00.npz --format png --output histogram-3600.png
```

### 11.4 Tests (`tests/test_histogram.py`)

| Test | Asserts |
|---|---|
| `test_histogram_text_output` | A hand-built world with known per-level counts produces the right text counts |
| `test_decade_binning` | Frequencies at 100, 1000, 10000 fall into three different bins |
| `test_empty_world_no_crash` | A world with zero alive entities at all levels produces output without errors |

## 12. Configuration changes (`world/config.py`)

```python
@dataclass(frozen=True)
class WorldConfig:
    # Seeding (3D)
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float, float] = (1000.0, 1000.0, 1000.0)  # CHANGED from 2-tuple
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

    # Decay (mean exponential lifetimes)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Scale separation (NEW, §4.6)
    repulsion_k: float = 100.0
    repulsion_cell_size: float = 100.0   # spatial-hash cell size for the long-range force
    repulsion_threshold_ratio: float = 1000.0   # only acts above this freq ratio

    # Ambient regeneration (NEW, §4.7)
    lambda_gen: float = 0.0001    # vibrations per unit volume per unit time
    lambda_dec: float = 0.001     # per node per unit time, applied to electrons/pairs/triads

    # Simulation
    dt: float = 1.0 / 60.0
    rng_seed: int | None = 42

    # Capacity
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024
```

`box_size` becomes a 3-tuple. New parameter blocks for repulsion and ambient regeneration. Default values for `lambda_gen` and `lambda_dec` are placeholders — the calibration sweep will find productive values.

## 13. CLI changes (`world/run.py`)

```bash
# Headless run with snapshots
python -m world run --headless --duration 3600 --snapshot-every 30 \
                   --snapshot-dir ./snapshots/calibration-001/ \
                   --config calibration_v1.toml

# Headless + live Open3D preview alongside
python -m world run --headless --duration 3600 --snapshot-every 30 \
                   --snapshot-dir ./snapshots/calibration-001/ \
                   --preview

# Save final state
python -m world run --headless --duration 60 --save final.npz
```

The `run` subcommand drops the old window mode (Pygame is gone). `--preview` opens Open3D in a side process.

## 14. Bootstrap

The migration is destructive — 2D code is replaced. No need to translate documents (they're already English). Steps:

1. Update `pyproject.toml`: drop `pygame`, add `open3d >= 0.18`, `optuna >= 3.6`.
2. `pip install -e ".[dev]"` to refresh the venv.
3. Verify `python -c "import open3d; import optuna"` succeeds.
4. Verify Blender is callable: `blender --version` (install via `brew install --cask blender` if missing on macOS).

## 15. Acceptance criteria

This spec is satisfied when:

1. The 3D substrate runs end-to-end: `python -m world run --headless --duration 60 --snapshot-every 5` produces 12 snapshot files, each with 3D position arrays.
2. `pytest` passes all tests, including the new `test_repulsion`, `test_ambient`, `test_snapshot`, `test_sweep`, `test_histogram` test files.
3. Ambient density holds within ±20 % of the seeded value over a 1-hour calibration run with the calibration TOML produced by the sweep harness.
4. `tools/sweep.py --backend grid` runs at least one parameter sweep end-to-end and produces a JSON-line result log.
5. `tools/histogram.py` reads any snapshot and produces both text and PNG output without errors.
6. `tools/render_blender.py` produces at least one publication-quality image from a snapshot.
7. The Open3D preview window opens and closes cleanly when invoked with `--preview` on a running simulation.
8. CONCEPT.md v2 Phase 1 success criteria are demonstrably testable (atoms forming + spatial sorting + ambient stability) with at least one parameter setting.

Calibrating the parameters to *meet* those Phase 1 success criteria is the next research phase, with the sweep harness and Blender pipeline as its tools — *that work is not part of this spec*.

## 16. What this spec deliberately does not include

- Phases 2–8 of CONCEPT.md v2.
- Multi-GPU or distributed simulation (single-machine only; GPU path is Phase 4+).
- Cloud rendering (Blender pipeline runs locally).
- A web-based preview (Open3D desktop window only).
- Fancy materials in Blender (start with PBR spheres + glow; refined materials are a follow-up).
- Time-series video rendering automation beyond a simple shell loop.
- An interactive parameter-tuning UI (TOML edit + sweep is the calibration loop).
