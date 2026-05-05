# Tutorial: Running the World of Vibrations

This walks you through every step from a fresh clone to a calibrated, productive simulation. It assumes you've never seen the project before and that you've read the root `README.md` once. Allow about an hour for the first walkthrough; allow a full evening (or several) for the calibration phase that follows.

The tutorial is written in the order you'll actually do things. Skim it once, then come back to the relevant section when you're at that step.

---

## Part 0 — What you're about to run, conceptually

The simulation has one primitive: a **vibration**. Each vibration carries four properties — frequency in Hz, polarity (even or odd), 2D position, 2D velocity. Free vibrations move in straight lines through a 2D box with periodic boundaries (cross the right edge, re-enter from the left).

When two vibrations meet, three conditions decide whether they bind:

1. They are within `r_1` of each other.
2. One is even-polarity, the other odd.
3. Their frequencies differ by exactly 8 % (with a tolerance of ±0.5 %).

If all three hold, they fuse into an **electron**. The electron sits at the midpoint, takes the sum of the two source frequencies, and freezes — electrons do not move. Both source vibrations are absorbed.

Electrons can then bind into pairs (level 2), pairs plus electrons into triads (level 3), triads plus electrons into atoms (level 4). The same three conditions apply, with `r_2` instead of `r_1`, plus one extra: the two binding partners must be in the same frequency decade. Atoms are permanent. Pairs and triads decay back into their constituents on a Poisson clock — mean lifetime 5 seconds and 30 seconds at the defaults.

That's the whole physics. Three rules, four hierarchy levels, one decay process.

The interesting question is whether, with parameters that match this small ruleset, atoms reliably form. The answer at the source spec's defaults is no — the world is too sparse. So the second half of the tutorial covers calibration.

---

## Part 1 — Setup

You need Python 3.13 (3.14 is too new for Numba 0.65 at the time of writing) and a working pip. macOS / Linux / Windows-with-WSL all work; Windows native may have Pygame-init quirks.

```bash
git clone <wherever-this-is>
cd EQMOD

python3.13 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[dev]"
```

The install pulls NumPy, Numba, Pygame, and pytest. On the first install, Numba downloads its LLVM dependency — that adds 30–60 seconds and ~70 MB. Subsequent installs are fast.

Verify with the sanity import:

```bash
python -c "import world; import numpy, numba, pygame; print('OK')"
```

You should see Pygame's startup banner and `OK`. If you see import errors, fix them now — they will not get easier later.

Run the test suite once to confirm everything compiles cleanly:

```bash
pytest
```

Expect 42 tests to pass in well under a second. Numba `@njit` functions compile on first use and cache to `world/__pycache__/`; the first test run pays a ~0.5 s compile tax that subsequent runs avoid.

---

## Part 2 — Your first window run

```bash
python -m world run
```

A 1024×1024 window opens. You should see roughly a thousand small dots scattered across the box, blue (even polarity) and red (odd polarity), drifting in straight lines. Watch for a minute. You will see a few yellow-orange dots appear and stop moving — those are electrons.

At default parameters you will see almost nothing else. The defaults are documentary, not productive. Read on.

Controls:

| Key | What it does |
|---|---|
| `Esc` | Quit |
| `Space` | Pause / resume the simulation. Rendering continues. |
| `R` | Reseed from `INITIAL_CONFIG`. The world starts over with fresh vibrations. |

The stats line at the top reads:

```
t = 0.50 s | FPS 60 | vibr 1000 | e- 3 | pair 0 | triad 0 | atom 0
```

`t` is simulated time. `vibr` is the count of free vibrations remaining. `e-`, `pair`, `triad`, `atom` are alive counts at each hierarchy level. With default seed 42 you should see `e-` rise into the low double digits over the first thirty seconds and then plateau. Pairs do not appear.

Quit with `Esc` and continue.

---

## Part 3 — Headless mode and the smoke test

Window mode is for watching. Headless mode is for actually getting work done — running for minutes or hours without the rendering tax, with periodic stats printed to stdout.

```bash
python -m world run --headless --duration 60 --snapshot-every 5
```

This runs 60 simulated seconds at `dt = 1/60` (so 3600 ticks), printing the stats line every 5 simulated seconds. You should see something like:

```
t =    5.00 | vibr   997 | e-    1 | pair    0 | triad    0 | atom    0
t =   10.00 | vibr   994 | e-    3 | pair    0 | triad    0 | atom    0
t =   15.00 | vibr   994 | e-    3 | pair    0 | triad    0 | atom    0
...
# done — 60.0 simulated s in 8.5 wall s (7.1× real-time)
t =   60.00 | vibr   962 | e-   19 | pair    0 | triad    0 | atom    0
```

7× real-time on a modern laptop is typical at the default world size. Larger or denser worlds run slower; we'll get there.

The dedicated smoke script does the same but asserts a minimum result:

```bash
python tests/calibration_smoke.py
```

You will see:

```
max counts: e- 19 | pair 0 | triad 0 | atom 0
FAIL: no pairs formed; no triads formed
```

This is the expected outcome at the defaults. The smoke script is calibrated to fail at the source spec's parameters precisely so it tells you when calibration has worked. Take this `FAIL` as your starting line, not a problem.

---

## Part 4 — The calibration loop

This is the actual research work. Calibration means finding parameter values that make the world productive — at minimum, that pairs and triads form regularly, and that at least one atom forms before the run ends. The plan is iterative: change one or two parameters, run for one or two minutes, observe, log, repeat.

### Why the defaults don't work

A 1000-vibration world in a 1000×1000 box has a vibration density of roughly one per 1000 unit² — typical neighbour distance ≈ 32 units. With `r_1 = 5`, two vibrations have to come unusually close to meet the binding distance. That gates how often electrons form. And electrons, once formed, do not move — so two electrons binding into a pair requires both to have formed within `r_2 = 10` of each other. At low electron density, that's a rare coincidence.

The levers are obvious in retrospect. Either raise the density (smaller box or more vibrations) or raise the binding radii. The 8 % frequency rule is unforgiving and shouldn't be touched first; widen `freq_tolerance` only after radii and density.

### Writing your first override

Calibration parameter changes go into a TOML file, not into source code. Create `calibration_v1.toml` at the repo root:

```toml
# calibration_v1.toml — first attempt at a productive world.

box_size = [500.0, 500.0]   # 4× the density of default
r_1 = 10.0                  # double the vibration→electron radius
r_2 = 20.0                  # double the electron→pair radius
freq_tolerance = 0.01       # widen the 8% window slightly
n_nodes_max = 4096          # default 1024 will run out at this density
```

Run with the override:

```bash
python -m world run --headless --duration 120 \
                   --snapshot-every 10 \
                   --config calibration_v1.toml
```

Two minutes simulated, stats every 10 seconds. The relevant TOML field names match the dataclass fields in `world/config.py` — anything not in the TOML keeps its default.

At these parameters you should see pairs start forming. Whether you also see triads and atoms in two minutes depends on luck and the specifics of the seed; bump duration to 300 if you want more confidence.

### Reading the output

A productive run, condensed:

```
t =   10.00 | vibr   843 | e-   78 | pair    0 | triad    0 | atom    0
t =   30.00 | vibr   612 | e-  186 | pair    1 | triad    0 | atom    0
t =   60.00 | vibr   447 | e-  211 | pair    8 | triad    1 | atom    0
t =  120.00 | vibr   289 | e-  195 | pair    7 | triad    2 | atom    0
```

Things to notice. `vibr` is dropping monotonically — vibrations get absorbed into electrons and don't come back. `e-` rises, plateaus, and may dip slightly as electrons get bound into pairs. `pair` and `triad` counts oscillate around an equilibrium between formation and decay. If you see `atom = 1` you've reached the goal of Phase 1's calibration work; everything from there is robustness.

A non-productive run looks like this:

```
t =   60.00 | vibr   962 | e-   19 | pair    0 | triad    0 | atom    0
```

`vibr` barely dropped, electrons plateau in the low twenties, no pairs. The world is too sparse for the binding chain to start. Adjust and try again.

### What to change, in what order

When the world isn't productive, the diagnostic is usually one of:

| Symptom | Likely cause | Try |
|---|---|---|
| Few electrons (< 50) at end of 60 s | `r_1` too small for vibration density | Raise `r_1` to 8 or 10, or shrink box to 500×500 |
| Many electrons but no pairs | Electrons too sparse for `r_2` | Raise `r_2` to 20–40, or further raise density |
| Pairs but no triads | Pairs decay before a third electron arrives | Raise `pair_decay_time` to 10 s |
| Triads but no atoms | Triads decay before a fourth electron arrives | Raise `triad_decay_time` to 60 s, or raise electron density further |
| Crashes with "Node capacity exhausted" | Pre-allocated arrays too small for this world | Raise `n_nodes_max` to 4096 or 8192 |
| Crashes with "Composition index capacity exhausted" | Same as above; CSR arrays sized 4× of `n_nodes_max` | Raise `n_nodes_max` |
| Whole run completes but no events at all | Probably a bug, not a parameter issue | Open `LOGBOOK.md` and write down everything you tried |

Make one change at a time. The temptation is to bump four parameters at once; resist it. You will not learn which lever moved the world.

### The LOGBOOK discipline

`LOGBOOK.md` is the most important file in this repo over the long run. Every calibration session is one entry. Each entry records:

- The date.
- Which TOML file you ran (commit it, or paste the contents into the entry).
- What you observed — the actual stats numbers, not paraphrases.
- Your hypothesis about what's blocking progress.
- The single change you made next.
- Whether it worked.

The format is whatever you can keep up. Plain prose works. The first session is already in the file; copy its shape.

There is no automation around the logbook. Notes you don't write down become notes you don't have. Three sessions in you will not remember whether `r_2 = 30` was the one that produced the first triad or the one that crashed; the LOGBOOK tells you.

Screenshots from the window mode go under `docs/logbook/`. The repo is set up to track them — `.gitignore` excludes `docs/logbook/*.png` by default but admits anything explicitly added (`!docs/logbook/.gitkeep`). To add a screenshot:

```bash
# take it however your OS does (Cmd-Shift-4 on macOS, Snipping Tool on Windows, etc.)
mv ~/Desktop/screenshot.png docs/logbook/2026-05-12-first-atom.png
git add -f docs/logbook/2026-05-12-first-atom.png
```

The `-f` overrides the gitignore for that one file.

---

## Part 5 — Reading the natural laws in code

Once you've watched the simulation a few times, you will want to know exactly how each rule is implemented. Here's where each one lives.

### Motion

`world/physics.py:9`. `move_vibrations` is a `@njit` function that takes the position array, velocity array, alive mask, box dimensions, and `dt`. For each alive vibration it advances position by `velocity * dt`, then wraps modulo `box`. Periodic boundaries are pure `% box[0]` and `% box[1]`. Velocity is never modified — there is no friction.

### The first binding (vibration → electron)

`world/physics.py:24` (`bind_vibrations_to_electrons`). The function builds a spatial grid keyed on cells of size `r_1`, then for each alive vibration scans its 9 neighbouring cells (3×3 with periodic wrap) for a binding partner. The three conditions — distance, polarity, frequency — are checked in that order, cheapest first. On a match, `world.allocate_node` records the new electron, both source vibrations are marked dead, and the locked-this-tick flag prevents either from binding again in the same scan.

The polarity of the new electron is **randomly assigned** at formation: `bool(world.rng.random() < 0.5)`. This is the keystone of the design's parity puzzle (see the design spec §2.2). It is what allows higher-level binding to keep working — both polarities have to coexist at every level, and inheriting from constituents would collapse to a single polarity at each level.

### Higher binding (electron → pair, pair → triad, triad → atom)

`world/physics.py:90` (`bind_nodes_upward`). Same shape as the vibration-level binding but on the node arrays, with `r_2` instead of `r_1` and one extra rule: the two partners must be in the same frequency decade. The decade of a frequency is `floor(log10(freq))` — so 500 Hz and 540 Hz are both in decade 2 and can bind, but 9500 Hz and 10260 Hz are in decades 3 and 4 and cannot. The decade rule prevents the hierarchy from collapsing across orders of magnitude.

The four upgrade paths are encoded in a small dict at the top of the function:

```python
_UPGRADE_TARGET = {
    (1, 1): 2,   # electron + electron → pair
    (1, 2): 3,   # electron + pair → triad
    (2, 1): 3,   # symmetric
    (1, 3): 4,   # electron + triad → atom
    (3, 1): 4,   # symmetric
}
```

Atoms (level 4) have no entry, so they cannot upgrade further. Pairs cannot upgrade with pairs (no `(2,2)` entry), triads cannot upgrade with triads or pairs.

### Decay

`world/physics.py:142` (`decay_unstable_nodes`). For each alive level-2 or level-3 node, draw a uniform random number; if it's below `dt / decay_time`, dissolve the node and revive its constituents. Atoms (level 4) and electrons (level 1) are skipped — atoms are permanent by design, electrons are stable in this iteration (their decay back into vibrations is deferred to a future spec).

The decay time is the **mean** of the exponential distribution of node lifetimes. So `pair_decay_time = 5` means a pair lives, on average, 5 simulated seconds — but individual pairs vary, some decay much sooner, some last a minute.

### The full tick

`world/physics.py:165` (`tick`). One simulation step:

```python
def tick(world, dt):
    move_vibrations(...)         # 1
    bind_vibrations_to_electrons(world)   # 2
    bind_nodes_upward(world)              # 3
    decay_unstable_nodes(world, dt)       # 4
    world.t += dt                         # 5
```

Order matters. Bind first, then decay — a pair that just gained a third electron should become a triad in the same tick, not first roll for decay. Move first because vibrations need to have moved into binding range before the binding scan runs.

---

## Part 6 — Writing your own parameter studies

Calibration with single TOML files works for one-off tweaks. For systematic exploration — sweeping `r_2` from 10 to 50 in steps of 5, for example — write a Python script that constructs `WorldConfig` programmatically and reports counts.

A starter script:

```python
# studies/r2_sweep.py
from dataclasses import replace
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick

base = WorldConfig(
    box_size=(500.0, 500.0),
    r_1=10.0,
    freq_tolerance=0.01,
    n_nodes_max=4096,
    rng_seed=42,
)
duration = 120.0

print(f"{'r_2':>6}  {'e-':>5}  {'pair':>5}  {'triad':>5}  {'atom':>5}")
for r2 in (10, 15, 20, 25, 30, 40):
    cfg = replace(base, r_2=float(r2))
    w = World(cfg)
    n_ticks = int(duration / cfg.dt)
    seen = {1: 0, 2: 0, 3: 0, 4: 0}
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        for level in (1, 2, 3, 4):
            seen[level] = max(seen[level],
                              int(np.sum((w.k_level[:w.k_count] == level) &
                                         w.k_alive[:w.k_count])))
    print(f"{r2:>6}  {seen[1]:5d}  {seen[2]:5d}  {seen[3]:5d}  {seen[4]:5d}")
```

Save it under a `studies/` directory (the project doesn't ship one — make it). Run with `python studies/r2_sweep.py`. The output is a table you can paste into the LOGBOOK.

This pattern generalises. Vary one parameter, hold the rest fixed, run for a fixed duration, record max-counts. Single-variable sweeps are the most informative; two-variable grids are more expensive and rarely change the diagnosis.

---

## Part 7 — Saving and inspecting state

For long runs you want to save the final state so you can inspect it without re-running:

```bash
python -m world run --headless --duration 300 --save final_v1.npz
```

The `.npz` file contains every NumPy array in the `World`. Load and inspect:

```python
import numpy as np
data = np.load("final_v1.npz")

print("vibrations alive:", int(data["s_alive"].sum()))
print("electrons:", int(((data["k_level"] == 1) & data["k_alive"]).sum()))
print("pairs:", int(((data["k_level"] == 2) & data["k_alive"]).sum()))
print("triads:", int(((data["k_level"] == 3) & data["k_alive"]).sum()))
print("atoms:", int(((data["k_level"] == 4) & data["k_alive"]).sum()))

# Atoms with their constituent triad and electron indices:
for i in np.where((data["k_level"] == 4) & data["k_alive"])[0]:
    start = data["k_comp_offset"][i]
    end = data["k_comp_offset"][i + 1]
    constituents = data["k_comp_indices"][start:end]
    print(f"atom {i} at {data['k_pos'][i]}, freq {data['k_freq'][i]:.1f}, "
          f"made of nodes {constituents.tolist()}")
```

There is no `--load` flag yet — saving is one-way for now. If you want to resume from a saved state, that's a follow-up project.

---

## Part 8 — Common pitfalls

A few things that have caught us:

**Numba's first compile is slow.** The first time you run `python -m world run` or `pytest`, Numba compiles three or four `@njit` functions on the fly. That's a 0.5–2 second pause before anything happens. Subsequent runs use the cache and start instantly. If you ever see suspicious behaviour right after editing a `physics.py` function, delete `world/__pycache__/` to force a fresh compile.

**`World.compact()` refuses to run when nodes exist.** This is by design, not a bug. Vibration compaction renames vibration indices; the CSR composition arrays for electrons hold the old indices and would silently corrupt. Until node compaction lands (a future spec), `compact()` is only safe on a freshly seeded world before any electrons have formed. The function raises `RuntimeError` rather than corrupting silently — read the message and you'll know what to do.

**The `R` reset key reseeds with the same RNG seed.** If you set `rng_seed = 42` and press `R`, the new world is **identical** to the old world. To get a different starting state, change the seed in the config or quit and rerun with `--seed N`.

**Headless duration is in simulated seconds, not wall seconds.** A `--duration 300` headless run finishes in about 40 wall seconds at 7× real-time. A `--duration 300` *window* run actually takes 300 wall seconds (the renderer rate-limits to 60 fps). For calibration you want headless every time.

**Pygame on macOS sometimes opens the window behind your editor.** Cmd-Tab to find it.

---

## Part 9 — Where to go after Phase 1

Once your calibrated world reliably produces atoms over a 60-second run, Phase 1 is materially complete. The next steps, in order from the long-term plan in `files/SKILL.md`:

1. **Skip-list parameters into the spec.** Whatever calibration TOML produces atoms reliably becomes the new defaults in `world/config.py`. Update `INITIAL_CONFIG` and the smoke test will pass at default parameters. This is the moment Phase 1 actually closes.

2. **Phase 2 — molecules and structural patterns.** Atoms binding to atoms with the same general rules. Look for *recurring* molecular shapes. The interesting question is which combinations of atom frequencies produce stable molecules, and how that depends on the polarity-randomisation rule that this iteration encodes.

3. **Phase 3 — membrane-like structures.** Closed rings of atoms or molecules separating an inside from an outside. May or may not emerge spontaneously; if not, hand-construct them and observe.

4. **Phases 4–8.** Neurons, synapses, networks, attention, and beyond. Each gets its own design spec and implementation plan, in the same shape as this one. The phase plan in `files/SKILL.md` is the source of truth.

The spec for this iteration is at `docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md`. The implementation plan is at `docs/superpowers/plans/2026-05-05-world-of-vibrations.md`. Both are under git; new specs and plans go in the same directories and get committed.

---

## A note on this not being a product

Everything in this codebase is research scaffolding. The defaults are documentary. The smoke test fails out of the box. The renderer has no zoom or pan. There is no save/load round trip. The CSR composition arrays are sized for Phase 1, not Phase 2. None of this is by mistake — these are the corners we deliberately did not cut, in favour of building something that is calibratable, observable, deterministic, and fast enough to actually run for hours.

If you came here expecting a polished simulation tool, you came to the wrong repo. If you came here to do research on emergent structure in a small, well-specified physical world, the substrate works. The rest is up to you.
