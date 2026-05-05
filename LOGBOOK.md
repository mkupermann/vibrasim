# World of Vibrations — Logbook

Research diary. Each session is one entry. Document what you ran, what you observed, what you adjusted, what you learned. Screenshots go under `docs/logbook/`.

---

## 2026-05-05 — Session 1: First runs and initial calibration sweep

### Phase 1 build: shipped

All 16 plan tasks completed. Full `pytest` suite: 40 passed, 1 skipped. Branch `feat/world-of-vibrations-phase-1`. Numba `@njit` paths compile and cache. Pygame renderer smoke-tests clean under `SDL_VIDEODRIVER=dummy`. CLI works for both window and headless modes.

### First smoke run with `INITIAL_CONFIG`

```bash
python tests/calibration_smoke.py
```

Result: `max counts: e- 19 | pair 0 | triad 0 | atom 0` — **smoke FAILS as expected**.

This is the world the source spec describes: 1000 vibrations in a 1000×1000 box with `r_1 = 5`, `r_2 = 10`, `freq_tolerance = 0.005`. The smoke test correctly flags that the world is not productive at these parameters.

### Calibration sweep round 1 (60 s each)

| config | e- | pair | triad | atom |
|---|---:|---:|---:|---:|
| default (`r_1=5, r_2=10`) | 19 | 0 | 0 | 0 |
| `r_1=10, r_2=20` | 50 | 0 | 0 | 0 |
| `r_1=20, r_2=40` | 86 | 0 | 0 | 0 |
| `r_1=10, r_2=80` | 50 | 0 | 0 | 0 |
| `freq_tolerance=0.01` (`r_1=10, r_2=20`) | 84 | 0 | 0 | 0 |
| `freq_tolerance=0.02` | 130 | 0 | 0 | 0 |

Loosening the radii and the 8 % tolerance increases electron formation by ~7×, but pairs still don't form. The diagnosis: **electrons are stationary by design** (`s_pos` fixed at the binding midpoint). Two electrons can only bind into a pair if they happen to form within `r_2` of each other in the first place. At default density (1 vibration per ~1000 unit²), electrons are too sparse for that to happen.

### Calibration sweep round 2 (120 s each, denser worlds)

| config | e- | pair | triad | atom |
|---|---:|---:|---:|---:|
| `box=500×500, r_1=10, r_2=20, ftol=0.01` | 283 | **1** | 0 | 0 |
| `box=300×300, r_1=10, r_2=20, ftol=0.01` | 350 | 0 | 0 | 0 |
| `n_initial=3000, r_2=30` | crashed (node capacity) | — | — | — |

A 500×500 box (4× the density of default) finally produced a pair. Smaller box (300×300) didn't help — likely because `r_1` is now relatively large compared to box, vibrations re-encounter each other before the 8 % rule has time to filter, and the binding scan becomes contention-limited rather than density-limited.

### Implementation findings to act on

1. **Node capacity** (`n_nodes_max = 1024`) is too small for 3000-vibration worlds. With ~3 vibrations forming each electron, plus higher-order nodes, we need roughly `n_initial_vibrations / 2` capacity. Action: in calibration TOMLs, scale `n_nodes_max` with `n_initial_vibrations`. Long-term: implement node compaction (deferred to a future spec).

2. **The 8 % rule is the binding bottleneck at higher levels.** Electron frequencies cluster around 2× the median vibration frequency, with low variance, so two electrons differing by exactly 8 % is rare. Calibration could try widening `freq_tolerance` to 0.015 or 0.02 *for higher-level binding only* — but that would require splitting the tolerance into two parameters (one per level). Worth considering before changing the TOML approach.

3. **Stationary electrons are the design choice.** The source spec is explicit (`Es bleibt an der Stelle`). The right calibration lever is density and radii, not electron mobility. Don't fight the spec.

### Hypotheses to test next session

- **Box 500×500, `r_2=30`, `freq_tolerance=0.015`, duration 300 s.** Goal: reach ≥ 5 pairs and at least one triad.
- **n_nodes_max bumped to 4096** so we don't crash on dense worlds.
- Once pairs form regularly, observe whether triads start appearing without further tuning. If not, adjust `pair_decay_time` upward (current 5 s may be too short for a triad-forming partner to find the pair).

### Next

Pre-calibration TOML drafted at `docs/logbook/.calibration_v1.toml` would document each session's settings. Not yet committed — first need session 2 data to confirm the hypothesis above.

---

## 2026-05-05 — Session 2: Phase 1 v2 shipped (3D substrate, repulsion, ambient regeneration)

### What got built

Following the peer-review feedback on the Konzeptpapier, four substantive changes landed in CONCEPT.md v2 and the corresponding code:

1. Substrate migrated from 2D to 3D (periodic on all three axes).
2. Scale separation through repulsion (§4.6) promoted from deferred to foundational; implemented in `world/physics.py::apply_scale_repulsion`.
3. Ambient regeneration (§4.7, new): `lambda_gen` injects free vibrations volumetrically; `lambda_dec` decays bound nodes at a slow rate. Closes the "matter from vacuum" gap of v1.
4. Realtime de-prioritised. Physics is headless and writes NPZ snapshots; PyVista handles live preview; headless Blender Cycles renders publication-grade keyframes from snapshots.

Plus the calibration tooling that v1 didn't have: `tools/sweep.py` (grid/random parameter sweeps with optional Optuna backend), `tools/histogram.py` (frequency-decade histograms over snapshots), `tools/render_blender.py` (Cycles keyframe pipeline).

Pygame is gone. Open3D was the originally-planned preview library; Python 3.13 doesn't have an Open3D wheel yet, so PyVista 0.48 (VTK-based, full 3D-native, modern Python) takes its place. Documented in the build commit.

### Test count

63 passing, 0 skipped (was 40 passed + 1 skip in v1). Six new test files cover the new functionality: `test_ambient.py`, `test_repulsion.py`, `test_snapshot.py`, `test_sweep.py`, `test_histogram.py`, plus updates to `test_decay.py` and `test_tick.py` for the 3D substrate.

### First v2 smoke

```
python -m world run --duration 30 --snapshot-every 5 --snapshot-dir snapshots/v2-acceptance/
```

Output (every 5 s):
```
t = 30.00 | total_v 4100 | ambient 4.0960e-06 | vibr 4096 | e- 2 | pair 0 | triad 0 | atom 0
```

Three observations from this:

- **The world is faster than light at filling.** The default `lambda_gen = 0.0001` per unit volume per unit time, applied to a `1000³` box, generates ~10 000 new vibrations per second. The physics tick saturates `n_vibrations_max = 4096` within the first second and stays pinned there. Calibration target: shrink `lambda_gen` by ~3 orders of magnitude (toward `1e-7`), or commensurately expand `n_vibrations_max`.
- **Sparse binding**. With the box at full volume but only `r_1 = 5`, two free vibrations almost never come within binding distance. After 30 s only 2 electrons form — half of v1's 19. The 3D volume is 1000× the 2D area at the same density, so the encounter rate drops 1000-fold per the back-of-envelope in CONCEPT.md v2 §10.6 line 2.
- **Wall time at default**. 30 simulated seconds in 44.8 wall seconds = 0.7× real-time. Slower than v1's 7× (3D 27-cell hash + repulsion + ambient regen). Acceptable per the relaxed realtime priority. Calibrating `lambda_gen` down should also speed this up substantially because the inner loops stop processing 4096 saturated vibrations.

### First v2 sweep

```
tools/sweep.py --backend grid --params-toml /tmp/v2-sweep.toml --duration 5 --output sweeps/v2-r2-sweep.jsonl
```

`r_2 ∈ {10, 20, 30}`, all three trials saturated identically — 4096 vibrations, 2 electrons, 0 pairs. The sweep runs end-to-end (~7.7 s wall per trial); the harness produces the right JSONL. The sweep being uninformative is the *world* not yet being calibrated, not the *tool* not working.

### First v2 Blender keyframe

```
blender -b -P tools/render_blender.py -- --snapshot snapshots/v2-acceptance/snapshot_t000030.00.npz --output renders/v2-acceptance.png --quality low
```

Rendered in 7 s (low quality, 64 samples) on Blender 5.1.1. 1.6 MB PNG, 1920×1080. The pipeline works; the scene is sparse because the world is sparse. At medium/high/paper quality the same scene takes proportionally longer. Image at `renders/v2-acceptance.png`.

### Calibration plan for next session

The v2 substrate is correct; the defaults are not. Three targets, in order:

1. **`lambda_gen` calibration.** Find the value that holds `total_v ≈ n_initial_vibrations` over a 60-second run. Probably `lambda_gen ∈ [1e-8, 1e-6]` for the default 1000³ box. Sweep over a logarithmic range.
2. **Density vs binding rate.** Once `lambda_gen` is calibrated, drop the box to `300³` to recover encounter density (volume falls 37×, binding rate rises proportionally). The 3D 27-cell hash performance should still hold.
3. **First atom.** With density restored, the same calibration logic from session 1 applies: bump `r_2`, `freq_tolerance`, `triad_decay_time`. Goal for session 3: at least one atom in 60 simulated seconds with the calibrated TOML.

Once session 3 produces atoms reliably, the calibrated TOML becomes the new `INITIAL_CONFIG` defaults and CONCEPT.md v2 §5 Phase 1 success criterion 1 is met. Criterion 2 (spatial sorting by frequency decade — H2 testability) needs the repulsion to actually do work, which requires nodes spanning multiple decades; that's a follow-up to test once atoms form.

---
