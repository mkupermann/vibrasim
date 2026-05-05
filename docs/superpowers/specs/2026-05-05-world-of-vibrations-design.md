# World of Vibrations — Design Specification

**Status:** Draft for review
**Date:** 2026-05-05
**Source documents:** `files/SPEZIFIKATION.md`, `files/SKILL.md`, `files/README.md` (German originals)
**Scope:** Implementation Checklist steps 1–5 (scaffolding → free vibrations → first binding to electrons → pairs and triads with decay → indestructible atoms). Steps 6–8 (scale repulsion, control overlay, performance pass) and brain phases (SKILL phases 2+) are out of scope and live in their own future specs.

---

## 1. Goal

Implement a real-time 2D simulation in which the only primitive substance is a **vibration**. Through a small set of natural laws, vibrations bind into **electrons**, electrons into **pairs** and **triads**, and four electrons lock into a permanent **atom**. The result must run in real time at the default configuration (1000 vibrations, 60 fps), expose the physics to direct testing, and support headless multi-hour calibration runs.

This spec is intentionally narrow: build a stable, observable, calibratable base world. Higher hierarchies (molecules, membranes, neurons) are explicitly deferred.

## 2. Resolutions of open issues in the source spec

The German `SPEZIFIKATION.md` contains one inconsistency that must be resolved before any code is written.

### 2.1 The structural problem in the source spec

The source spec keeps "even meets odd" as the universal binding rule across all levels, then proposes counting parity per electron (electron = 1 → odd, pair = 2 → even, triad = 3 → odd, atom = 4 → even). Under that scheme **every entity at a given level has the same parity**, so two same-level entities can never satisfy "even meets odd". The hierarchy dies one level above where it started.

Both candidate counting schemes the source describes — Variante 3 (count vibrations) and the proposed Lösung (count electrons) — collapse to the same dead end. A different fix is needed.

### 2.2 Resolution adopted here

**Node-level parity is sampled uniformly at random at the moment a node forms.** Each new electron, pair, triad, and atom independently gets `k_pol = True` or `False` with probability 0.5. The seed is `WorldConfig.rng_seed` so runs are reproducible.

Consequences:

- The population at each level contains both polarities. "Even meets odd" remains satisfiable, so binding can proceed level by level without dead ends.
- Atom formation is still **triad + electron** (the source spec's mechanism), because both triads and electrons exist in both polarities. The total electron count in an atom is four (3 from the triad + 1).
- The vibration-level rule is unchanged: a vibration carries an intrinsic, fixed polarity sampled at world seeding.
- Polarity at the node level is a *fresh* property of a node, not derived from its constituents. Internally an electron still contains two oscillating vibrations; the externally visible parity is independent.

This is a meaningful departure from the source's "Parität durch Größe" framing, but it is the smallest change that lets the hierarchy actually work. The §10 test suite asserts both polarities are present at each level after a short warm-up.

### 2.3 Decay semantics

The source spec says "the pair can decay back into two electrons after a characteristic decay time." This is implemented as **memoryless exponential decay**: at each tick, each unstable node (level 2 or 3) decays with probability `dt / decay_time`. Mean lifetime equals `decay_time`. Two simultaneously formed pairs do not decay together — they decay on independent Poisson clocks.

## 3. Architectural decisions

| Decision | Choice | Why |
|---|---|---|
| Coupling of physics and rendering | Decoupled — `World` is a pure data model, renderer reads only | Headless calibration runs over hours; physics testable in isolation; clean upgrade path to GPU later |
| Data layout | Struct-of-arrays (NumPy), no Python objects in hot paths | Numba compatibility, cache-friendly, spatial-hash indices are integer arrays |
| Performance strategy | Numba `@njit` from day one on hot loops | Spec requires 60 fps with 1000 vibrations and scales toward 10 000; deferring this means a structural rewrite later |
| Configuration | Frozen dataclass + optional TOML override | Typed, autocompletable, hand-editable for calibration sessions |
| Persistence | None in this spec (save/load deferred to step-7 spec) | YAGNI for first iteration; calibration uses snapshot-to-stdout instead |

## 4. Project layout

```
EQMOD/
├── files/
│   ├── README.md                   # English (translated step 0)
│   ├── README.de.md                # German original, preserved
│   ├── SKILL.md                    # English (translated step 0)
│   ├── SKILL.de.md                 # German original, preserved
│   ├── SPECIFICATION.md            # English (translated from SPEZIFIKATION.md)
│   └── SPEZIFIKATION.de.md         # German original, preserved
├── docs/
│   ├── superpowers/specs/          # design specs (this file lives here)
│   └── logbook/                    # screenshots referenced from LOGBOOK.md
├── world/                          # Python package
│   ├── __init__.py
│   ├── state.py                    # World data model (SoA arrays, no logic)
│   ├── physics.py                  # @njit hot loops: motion, binding, decay
│   ├── spatial.py                  # spatial hashing, periodic-wrapping grid
│   ├── config.py                   # WorldConfig dataclass, INITIAL_CONFIG
│   ├── render.py                   # Pygame renderer (reads state, never mutates)
│   └── run.py                      # CLI entry: `python -m world run [...]`
├── tests/
│   ├── test_natural_laws.py        # pytest against physics functions
│   └── calibration_smoke.py        # 60-second headless smoke run
├── pyproject.toml                  # numpy, numba, pygame, pytest, py >= 3.11
├── LOGBOOK.md                      # research diary, committed to git
├── README.md                       # English (translated step 0)
└── README.de.md                    # German original, preserved
```

The German source files in `files/` and at the repo root are translated to English in step 0 (§9). The German originals are preserved as `*.de.md` siblings for traceability.

## 5. Data model (`world/state.py`)

`World` is a plain class holding NumPy arrays. No methods that touch physics; those live in `world/physics.py` as free functions taking arrays.

### 5.1 Vibration arrays (free-moving population)

```
s_pos    : float64[N_max, 2]    # position
s_vel    : float64[N_max, 2]    # velocity
s_freq   : float64[N_max]       # frequency in Hz
s_pol    : bool[N_max]          # True = even polarity, False = odd
s_alive  : bool[N_max]          # True if still free; False once bound into a node
n_alive  : int                  # cached count of alive vibrations
```

A vibration that becomes part of an electron flips `s_alive[i] = False` but stays in the array. Conceptually it keeps oscillating "inside" the electron. Compaction (§5.4) reclaims the slot when alive-fraction drops below 50%.

### 5.2 Node arrays (electrons, pairs, triads, atoms)

```
k_pos    : float64[K_max, 2]    # spatial position; fixed once formed
k_freq   : float64[K_max]       # cumulative frequency
k_pol    : bool[K_max]          # node-level parity (per §2.2)
k_level  : uint8[K_max]         # 1=electron, 2=pair, 3=triad, 4=atom
k_birth  : float64[K_max]       # simulation time when this node formed
k_alive  : bool[K_max]
k_count  : int                  # cached count of alive nodes
```

### 5.3 Composition (CSR-style flat arrays)

```
k_comp_offset  : int32[K_max + 1]   # offsets into k_comp_indices
k_comp_indices : int32[total_caps]  # flat list of constituent indices
k_comp_kind    : uint8[K_max]       # 0 = constituents are vibrations (electron),
                                    # 1 = constituents are nodes (pair/triad/atom)
```

For an electron, `k_comp_indices[k_comp_offset[i] : k_comp_offset[i]+2]` are two vibration indices. For a pair, two electron node indices. For a triad, two node indices: the constituent pair and the constituent electron. For an atom, two node indices: the constituent triad and the constituent electron. CSR slices are always exactly two entries for nodes at level 2, 3, and 4 — only electrons (level 1) carry vibration indices.

`k_comp_kind` lets inspection (visualization, stats) walk one indirection deep without recursing all the way to vibrations.

### 5.4 Capacity sizing and compaction

| Array | Capacity | Reasoning |
|---|---|---|
| `N_max` | 4096 | 4× the default 1000 starting vibrations; survives early binding cycles |
| `K_max` | 1024 | At most one node per ~4 vibrations |
| `total_caps` | 8192 | Average ~8 constituent slots per node, conservative |

Compaction: every ~1 simulated second, if `n_alive / N_max < 0.5`, scan-and-pack. CSR offsets in `k_comp_indices` are remapped during the same pass. Compaction is `O(N + K + total)` and runs outside the hot tick path — once per ~60 ticks at default `dt`.

## 6. Main loop (`world/physics.py`)

Single function `tick(world, dt)` with five steps:

```python
def tick(world, dt):
    move_vibrations(world, dt)              # 1
    bind_vibrations_to_electrons(world)     # 2
    bind_nodes_upward(world)                # 3
    decay_unstable_nodes(world, dt)         # 4
    world.t += dt                           # 5 (bookkeeping)
```

### 6.1 Step 1 — Motion

Vectorized: `s_pos[s_alive] += s_vel[s_alive] * dt`, then `s_pos %= box_size` for periodic wrap. Implemented as a `@njit` function that takes `s_pos`, `s_vel`, `s_alive`, `box_size`, `dt` as raw arrays and scalars.

### 6.2 Step 2 — Vibration → electron

1. Build a spatial hash on alive vibrations with cell size = `r_1`. Periodic-wrapping grid (3×3 neighbor cells with wrap).
2. For each pair `(i, j)` of alive vibrations within the same or neighboring cells:
   - squared distance < `r_1²` (compute under minimum-image convention for periodic wrap)
   - `s_pol[i] != s_pol[j]`
   - `|s_freq[i] − s_freq[j]| / min(s_freq[i], s_freq[j])` lies within `[freq_ratio − freq_tolerance, freq_ratio + freq_tolerance]`
3. On match, allocate a node:
   - `k_pos = midpoint(s_pos[i], s_pos[j])` — under minimum-image
   - `k_freq = s_freq[i] + s_freq[j]`
   - `k_pol = uniform_bool(rng)` — per §2.2, sampled fresh at formation
   - `k_level = 1`
   - `k_birth = world.t`
   - constituents `[i, j]`, `k_comp_kind = 0`
4. Set `s_alive[i] = s_alive[j] = False`. To prevent double-binding within one tick: lock partners as the scan proceeds (a `s_locked_this_tick` boolean array, reset per tick). A parallel scan with conflict resolution is deferred.

### 6.3 Step 3 — Node upgrades

Spatial hash on alive nodes with cell size = `r_2`. For each candidate node pair `(i, j)` within the same or neighboring cells:

| Trigger | Required levels | Resulting level |
|---|---|---|
| Pair formation | both 1 | 2 |
| Triad formation | one 2, one 1 | 3 |
| Atom formation | one 3, one 1 | 4 (atom, inert) |

Additional checks for every upgrade:

- squared distance < `r_2²`
- `k_pol[i] != k_pol[j]` (even meets odd)
- frequency 8% rule on `k_freq[i]`, `k_freq[j]` (same as §6.2 step 3)
- same frequency decade: `floor(log10(k_freq[i])) == floor(log10(k_freq[j]))`

On match:
- new node `k_pos = midpoint(...)`, `k_freq = k_freq[i] + k_freq[j]`, `k_level = next_level`, `k_pol = uniform_bool(rng)` per §2.2
- constituents are `[i, j]`, `k_comp_kind = 1`
- mark `k_alive[i] = k_alive[j] = False`
- atom (`k_level = 4`) is permanent: never visited by step 4

The atom mechanism (triad + electron) preserves the source spec's intuition that "the fourth electron snaps in" — a single lone electron is what completes an atom from a triad. The pair mechanism (electron + electron) and triad mechanism (pair + electron) work the same way: each upgrade absorbs one new constituent, except pair formation which fuses two electrons. This stays compatible with the parity-randomization rule in §2.2 because both polarities are present at every level.

### 6.4 Step 4 — Decay

For each node with `k_alive == True` and `k_level ∈ {2, 3}`:

- pair: `p = dt / pair_decay_time`
- triad: `p = dt / triad_decay_time`

Draw a uniform sample. If `u < p`, dissolve the node:

- Set `k_alive[node] = False`.
- For each constituent index in the CSR slice: set `k_alive[constituent] = True` (it returns to the alive node population — it does **not** decay all the way back to free vibrations). When a pair decays, both constituent electrons come back alive. When a triad decays, the constituent pair and constituent electron both come back alive — the pair's own internal electrons stay bound inside it.

Atoms (`k_level = 4`) and electrons (`k_level = 1`) are skipped here. Electrons are marked stable in this iteration; their decay back to free vibrations is deferred.

### 6.5 Ordering rationale

Bind first, then decay. A pair that just gained a third electron should become a triad in the same tick, not first roll for decay and then maybe survive long enough to be upgraded. Upgrades take precedence; the world's tendency is upward.

## 7. Renderer (`world/render.py`)

Single Pygame loop in the same process and thread as the simulation. Reads `World` arrays directly after each `tick`. Never mutates state.

### 7.1 Visual rules

| Entity | Shape | Color | Notes |
|---|---|---|---|
| Vibration, even | dot, r=2–3 px | `#4A90E2` | radius scales `log(freq)` |
| Vibration, odd | dot, r=2–3 px | `#E74C3C` | radius scales `log(freq)` |
| Electron | dot + soft glow, ~5 px | `#F39C12` | gentle pulse via `sin` of inner-frequency phase |
| Pair | 2 electrons + thin line | line `#CCCCCC` α=0.5 | reads as fragile |
| Triad | 3 electrons + 3 lines | denser, less transparent | hint of triangle |
| Atom | 4 electrons + 4 lines + halo | `#FFFFFF` with warm aura | the "stars" of the world |

Lines with alpha are drawn onto a per-frame `pygame.Surface(SRCALPHA)` and blitted. Atom halos are pre-rendered radial-gradient surfaces blitted at each atom's position to avoid per-frame gradient recomputation.

### 7.2 Stats overlay

Top-left, monospace font, single line:

```
t = 1234.5 s | FPS 60 | vibr 873 | e⁻ 64 | pair 8 | triad 3 | atom 5
```

The implementation checklist places stats at step 7. A minimal counter line is included here because calibration without it is impossible.

### 7.3 Controls

| Key | Action |
|---|---|
| `Esc` | quit |
| `Space` | pause / resume |
| `R` | reset (re-seed from `INITIAL_CONFIG` plus current `--config` overrides) |

Zoom, pan, click-to-add-vibration, save and load are explicitly out of scope and deferred to a step-7 spec.

### 7.4 Coordinate transform

Identity scale: world `(0, 0) → (box_size_x, box_size_y)` mapped to a margined viewport on a 1024×1024 window. No zoom and no pan. With default `box_size = 1000` and a 12 px margin, scale ≈ 1.0.

## 8. Configuration & CLI

### 8.1 `world/config.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class WorldConfig:
    # Seeding
    n_initial_vibrations: int = 1000
    box_size: tuple[float, float] = (1000.0, 1000.0)
    freq_min: float = 100.0
    freq_max: float = 10000.0
    freq_distribution: str = "log"          # "log" | "uniform"
    speed_min: float = 10.0
    speed_max: float = 50.0
    polarity_split: float = 0.5             # share of even-polarity vibrations

    # Binding
    r_1: float = 5.0                        # vibration → electron
    r_2: float = 10.0                       # node → node (any upgrade)
    freq_ratio: float = 0.08                # the 8% rule
    freq_tolerance: float = 0.005           # ±0.5% around freq_ratio

    # Decay (mean exponential lifetimes, seconds)
    pair_decay_time: float = 5.0
    triad_decay_time: float = 30.0

    # Simulation
    dt: float = 1.0 / 60.0                  # one tick = one frame at 60 fps
    rng_seed: int | None = 42

    # Capacity (pre-allocated array sizes)
    n_vibrations_max: int = 4096
    n_nodes_max: int = 1024

INITIAL_CONFIG = WorldConfig()
```

TOML overrides loaded via `tomllib` (stdlib in Python 3.11+) and merged over the dataclass defaults. A partial TOML file with just `r_1 = 7.0` is valid and changes only that field.

### 8.2 CLI (`world/run.py`)

`argparse` is sufficient. One subcommand for now: `run`.

```bash
python -m world run                                    # window, default config
python -m world run --config calibration_v3.toml       # window, override
python -m world run --headless --duration 60 \
                   --snapshot-every 5                  # headless, periodic stats
python -m world run --headless --duration 1800 \
                   --save final_state.npz              # long calibration run
python -m world run --seed 7                           # override rng_seed
```

| Flag | Meaning |
|---|---|
| `--headless` | Skip Pygame import entirely. Loop runs as fast as the CPU allows |
| `--config PATH` | TOML override file |
| `--duration SECONDS` | Only meaningful with `--headless`; window mode runs until `Esc` |
| `--snapshot-every SECONDS` | In headless mode, print one stats line every N simulated seconds |
| `--save PATH` | On exit, write `World` arrays to a NumPy `.npz` archive |
| `--seed N` | Override `rng_seed` |

The CLI never imports `world.render` unless not in headless mode — `import` is conditional inside `run.py`.

## 9. Bootstrap (step 0, before any code)

Three preparatory tasks, in order:

### 9.1 Translate German source files

| Source | Action |
|---|---|
| `files/README.md` | translate to English; preserve original as `files/README.de.md` |
| `files/SKILL.md` | translate to English; preserve original as `files/SKILL.de.md` |
| `files/SPEZIFIKATION.md` | translate to English at `files/SPECIFICATION.md`; preserve original as `files/SPEZIFIKATION.de.md` |
| `README.md` (repo root) | translate to English; preserve original as `README.de.md` |

Translation rule: faithful, no rewrites. The English files are working documents; the `*.de.md` files are historical record.

### 9.2 `pyproject.toml`

```toml
[project]
name = "world"
version = "0.1.0"
description = "World of Vibrations — a simulated physical substrate built from vibrations alone."
requires-python = ">=3.11"
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
```

### 9.3 Sanity import check

```bash
python -c "import world; import numpy, numba, pygame; print('OK')"
```

Must succeed before any physics code is written. Catches environment problems while there's nothing to debug.

## 10. Tests (`tests/test_natural_laws.py`)

Pytest suite that exercises the `@njit` functions directly. Each test seeds a tiny world (2–8 vibrations) so outcomes are deterministic and the failure tells you exactly which rule broke.

| Test | Asserts |
|---|---|
| `test_motion_periodic` | A vibration crossing the box edge re-enters at the opposite side; speed unchanged |
| `test_motion_no_friction` | Position after `n` ticks equals `pos₀ + n·dt·v` (mod box) |
| `test_no_binding_same_polarity` | Two vibrations, even+even, within `r_1`, freq diff 8% → no electron forms |
| `test_no_binding_freq_off` | Two vibrations, opposite polarity, within `r_1`, freq diff 5% → no electron |
| `test_no_binding_too_far` | Two vibrations meeting all rules but separated by `2·r_1` → no electron |
| `test_electron_forms` | Two vibrations meeting all three rules → exactly one electron at the midpoint, `k_freq = f₁+f₂`, both vibrations marked dead. Polarity is sampled per §2.2 — assertion is on existence and structure, not on parity value |
| `test_pair_forms` | Two electrons of opposite parity, same decade, freq diff 8%, within `r_2` → pair, both electrons marked dead. Pair `k_pol` is sampled per §2.2 |
| `test_triad_forms_pair_plus_electron` | Pair + electron of opposite parity, within `r_2`, decade match, freq diff 8% → triad |
| `test_atom_forms_triad_plus_electron` | Triad + electron of opposite parity, within `r_2`, decade match, freq diff 8% → atom at level 4 |
| `test_atom_indestructible` | Run 10 000 ticks with no neighbors; atom's `k_alive` stays `True`, `k_level` stays 4 |
| `test_pair_decays_eventually` | Many seeded pairs over 10⁴ ticks at `pair_decay_time = 5 s`, `dt = 1/60`. Decayed-fraction within ±5% of `1 − exp(−t/τ)` |
| `test_decade_isolation` | 500 Hz + 540 Hz (same decade) → can bind. 9000 Hz + 9720 Hz → fine. 9500 Hz + 10260 Hz (different decades) → no bind |
| `test_polarity_distribution_at_each_level` | After a warm-up run that produces ≥ 200 electrons and ≥ 50 pairs, both parities are present at electron and pair levels, with each parity's share between 30 % and 70 % (binomial check at fixed seed) |

The decay test is the only stochastic one and uses a fixed `rng_seed`. Everything else is deterministic.

### 10.1 Calibration smoke test

`tests/calibration_smoke.py` runs headless for 60 simulated seconds with `INITIAL_CONFIG`. Asserts: at least one electron, at least one pair, at least one triad observed at any point during the run. Atoms are not asserted — closing that gap is the whole point of the calibration phase. The smoke test is excluded from the default `pytest` run (it's slow) and invoked explicitly:

```bash
python tests/calibration_smoke.py
```

## 11. Logbook (`LOGBOOK.md`)

Created at first run from a template. Each session is one section, manually written. Committed to git so research history is part of the repo.

```markdown
# World of Vibrations — Logbook

## 2026-05-05 — Session 1: First run

- Config: defaults (INITIAL_CONFIG, see config.py at commit <sha>)
- Observation: 87 electrons formed in first 10 s, then plateau. No pairs.
- Hypothesis: r_2 too small at 10.0 — electrons can't find each other at that density.
- Adjustment: r_2 → 25.0 in calibration_v1.toml
- Result: pairs forming, ~3 per minute. Continuing to calibrate.
- Screenshot: docs/logbook/2026-05-05-first-pairs.png
```

Screenshots go under `docs/logbook/`. There is no automation around the logbook — this is the artifact that, per the source README, "becomes one of the most valuable documents of the project."

## 12. Implementation order

Each step is a working, runnable artifact. No step is started until the previous one runs end-to-end.

1. **Step 0 — Bootstrap.** §9.
2. **Step 1 — Scaffolding.** Empty `World`, empty Pygame window opens with a black background and `Esc` closes it. CLI dispatches `run`.
3. **Step 2 — Free vibrations.** `World` seeded from `INITIAL_CONFIG`. Vibrations move, periodic wrap works, dots render in correct colors and sizes. No binding.
4. **Step 3 — Vibration → electron.** Spatial hash, binding rule from §6.2, electrons render with glow and pulse. Vibration count drops as electrons form.
5. **Step 4 — Pair and triad with decay.** Node upgrades from §6.3 limited to levels 1→2 and 2→3 (i.e., pairs and triads only). Decay from §6.4. All visual rules render correctly.
6. **Step 5 — Atom.** Triad + electron → atom. Atom never decays. Halo renders. Smoke test passes. **Spec scope ends here.**

Out-of-scope follow-up specs:

- **Step 6 — Scale repulsion.** Cross-decade nodes repel. Spatial sorting becomes visible.
- **Step 7 — Statistics and controls.** Histogram, save/load, zoom/pan, click-to-add, speed control.
- **Step 8 — Performance pass.** Profile, tune Numba, possibly switch to GPU primitives if 10 000 vibrations is the target.

## 13. What this spec deliberately does not include

Each exclusion below carries reasoning, not just a tag — both to head off rework and to mark which excluded items get their own future spec.

### 13.1 Higher hierarchies (molecules, membranes, neurons)

Out of scope. Each gets its own future spec, sequenced according to the source `SKILL.md` phase plan:

- **Phase 2 — molecules** (atoms binding to atoms, structural patterns, recurring motif identification)
- **Phase 3 — membrane-like structures** (closed atom/molecule rings separating "inside" from "outside")
- **Phase 4 — neuron models** (clusters with input region, integration, threshold, output, refractory period)
- **Phase 5 — synaptic connections** (Hebbian plasticity)
- **Phase 6 — small networks** (pattern recognition, Hopfield-style memory, simple learning)
- **Phase 7 — attention and selection** (global carrier frequency, lateral inhibition)
- **Phase 8 — larger structures** (open research)

The SKILL document is explicit that **Phase 1 (this spec) must be stable and productive before Phase 2 begins**. Attempting to build neurons on top of a base world that does not yet reliably produce atoms is exactly the path the source skill warns against ("Frust und falsche Schlüsse"). A reliable atom-producing base world is the precondition for everything above.

### 13.2 Multi-threading / multiprocessing

Out of scope, on purpose. Three reasons:

1. **The bottleneck isn't CPU parallelism yet.** Numba on a single core, with a spatial hash, comfortably handles 1 000–10 000 vibrations at 60 fps. We have not yet observed the workload where a thread split would help.
2. **Concurrency invalidates determinism.** All §10 tests rely on deterministic ordering of binding scans. Adding threads means scans race, and "the same seed produces the same world" stops being true. That property is more valuable in Phase 1 than the speedup would be.
3. **Numba `@njit(parallel=True)` is the right level if we eventually need it.** It auto-vectorizes inner loops without us writing thread code or managing locks. Reaching for it later is a one-line annotation per hot function. Reaching for `multiprocessing` or raw threads now would be a structural commitment with a different cost profile.

If a Phase 6+ network ever exceeds single-core throughput, the right move is GPU (`@cuda.jit` or CuPy), not CPU threads. Same code shape, same SoA layout, ~100× headroom — see the source `SKILL.md` performance note.

### 13.3 3D space

The source spec is explicit: "Der Raum ist zweidimensional." This spec inherits that. Reasons it's the right choice for Phase 1, and worth preserving into later phases:

1. **Observability.** The whole research method depends on watching what emerges — pairs forming, triads decaying, atoms locking in, later spatial sorting by frequency decade. In 2D the pattern is on the screen with no camera work. In 3D you'd be debugging both the simulation and the projection: "did that cluster not form, or am I just looking at the wrong z-slice?"
2. **Encounter rate.** A vibration with binding radius `r_1 = 5` in a 1000×1000 box explores ~`r_1 / box_size = 0.5%` of the world per unit travel. In a 1000×1000×1000 cube it's `(r_1 / box_size)² ≈ 0.0025%`. To get the same partner-finding rate in 3D you'd need either more vibrations (more compute), longer simulations (more wall time), or larger `r_1` (which blurs the locality of the 8% rule). The source spec's calibration values are tuned to a 2D regime.
3. **Spatial hashing cost.** 2D periodic-wrap neighbor search visits 9 cells per query (`3×3`). 3D visits 27 (`3×3×3`). At equal grid resolution, that's 3× the inner-loop work — and grid resolution itself has to scale up to keep cell occupancy reasonable, compounding the cost.
4. **Numba and visualization paths.** Pygame is 2D-native. Adding 3D means swapping the renderer for ModernGL/Pyglet or similar before we even know whether the physics is calibrated. That's exactly the kind of premature commitment the SKILL document tells us to avoid.
5. **No physical insight gained.** None of the rules — 8% frequency rule, polarity match, decade isolation, scale repulsion later — depend on dimensionality. The brain-emergence research path doesn't need 3D either; small biological networks (C. elegans–scale, retina-slice models) are routinely studied in 2D abstractions. If a Phase 7+ result eventually demanded 3D, the move is a separate project, not a retrofit.

### 13.4 Other deferred items

- **GPU / CUDA acceleration.** Premature optimization for current scale. See §13.2 for the trigger condition.
- **Networked / multi-user simulation.** No use case in the research arc.
- **Interactive parameter-tuning UI** (sliders, live config). TOML edit + restart is faster feedback than building widgets we'd throw away.
- **Save / load of simulation state.** Deferred to a step-7 spec.
- **Decay of free electrons back to vibrations.** Electrons are stable in this iteration. Adding electron decay creates loops in the hierarchy that complicate calibration; revisited only if observation shows the world dies out without it.
- **Anything past step 5 of the implementation checklist.**

## 14. Acceptance criteria

This spec is satisfied when:

1. `python -m world run` opens a window, vibrations move, electrons form, pairs and triads form and decay, atoms form and persist *under at least one calibration TOML* (default config is documentary; see §14.4 below).
2. `python -m world run --headless --duration 60` runs to completion and prints periodic stats.
3. `pytest` passes all 13 listed tests across the test files.
4. `python tests/calibration_smoke.py` produces a result — pass or fail. **Smoke passing at default config is not required for Phase 1 to ship.** The smoke test is a calibration tool, not an acceptance gate. The defaults in §8.1 are taken straight from the source German spec and have not been calibrated; the LOGBOOK records the tuning of `r_1`, `r_2`, `freq_tolerance`, `box_size`, and `pair_decay_time` that makes the world productive. Phase 1 ships when the smoke test *runs cleanly* (no crashes, deterministic output) — not when it returns 0.
5. The three German source files have English translations and preserved `*.de.md` originals.
6. `LOGBOOK.md` exists with at least one session entry, including the smoke-test result and the next calibration hypothesis.

Calibration of the parameters to reliably produce atoms is **not** an acceptance criterion of this spec — that is the next phase of work, with the smoke test and logbook as its tools.
