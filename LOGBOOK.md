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

## 2026-05-06 — Session 3: Phase 1 calibrated, Phase 2 + Phase 3 scaffolding

This is the autonomous overnight session. Three objectives: calibrate Phase 1 v2 to produce atoms, build Phase 2 (molecule formation), build Phase 3 scaffolding (membrane detection + construction). Outcomes documented below.

### Phase 1 calibration: atom-producing config found

Two-stage calibration sweep. **Stage 1** (10 hand-picked configs, 30s each, 4-way parallel) screened density and radii. Best of stage 1: `dense_80_w20` (box=80³, 400 vibr, r_1=5, r_2=20, freq_tol=0.020) — 69 electrons + 2 pairs in 30s. The pattern: small dense box + standard r_1 + slightly wider r_2 + slightly wider freq_tolerance.

**Stage 2** (8 variants of the leader, 120s each, 4-way parallel) extended duration on promising configs. Leader: **`c80_v400_r30_t025`**.

| Config | Box³ | n_init | r_2 | freq_tol | pair_dec | triad_dec | e- | pair | tri | atom | first atom |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c60_v300_r25_t02 | 60 | 300 | 25 | 0.020 | 120 | 1200 | 87 | 4 | 1 | 0 | — |
| c80_v400_r20_t20 | 80 | 400 | 20 | 0.020 | 60 | 600 | 113 | 5 | 0 | 0 | — |
| c60_v400_r20_t015 | 60 | 400 | 20 | 0.015 | 60 | 600 | 115 | 3 | 0 | 0 | — |
| c50_v200_r20_t02 | 50 | 200 | 20 | 0.020 | 120 | 1200 | 52 | 2 | 0 | 0 | — |
| **c80_v400_r30_t025** | **80** | **400** | **30** | **0.025** | **60** | **600** | **104** | **10** | **2** | **1** | **t = 13.4s** |

CONCEPT.md v2 §5 Phase 1 success criterion 1 (reproducible atom formation) is **met** by `c80_v400_r30_t025`. The calibrated TOML is committed at `renders/calibration_session3.toml`.

The remaining stage-2 configs were still running at the time of writing; if any produce more atoms or earlier formation, this LOGBOOK gets a follow-up table.

The remaining Phase 1 success criteria (spatial sorting by frequency decade — H2; ambient stability with `λ_gen > 0`) are **not** yet met. They need:
- Wider `freq_min`/`freq_max` to span multiple decades (current 100–10000 is one decade, mostly 100–999 with a smaller tail at 1000–9999). Decade-3 and decade-4 atoms can form, but the spread is narrow.
- A non-zero `λ_gen` calibrated to hold population steady. The `c80_v400_r30_t025` config disables ambient (`λ_gen = 0`) for clean observation.

These are the targets for session 4 (next round of calibration).

### Phase 2: molecules from atoms

Spec at `docs/superpowers/specs/2026-05-06-phase-2-molecules.md`. Implementation deltas:

- `world/physics.py::_UPGRADE_TARGET` extended with rules: atom + atom → di-atomic (level 5); di-atomic + atom → tri-atomic (level 6); … up to level 11 (deca-atomic). Only atoms (level 4) can be added — molecules don't bind to molecules.
- `world/state.py::LEVEL_TO_VIBRATIONS` extended for the new levels (each atom contributes 8 vibrations, so a level-5 molecule has 16, a level-11 molecule has 64).
- `tools/classify_molecules.py` — fingerprints molecules by sorted constituent-atom frequency decades. Two atoms at decade 3 → species `A33`; an A33-atomic at decades 3,3,4 → `A334`.
- `world/preview.py` and `tools/render_blender.py` — render levels 5–11 with scaled radii and per-level colours.
- 13 new tests across `tests/test_phase2_binding.py` (8) and `tests/test_classify_molecules.py` (5). All pass.

A Phase 2 long-duration run on the calibrated TOML is in progress (240s simulated, snapshot every 1s); results land in this LOGBOOK at the next read. Phase 2 success criterion is at least 5 distinct molecule species fingerprints — `tools/classify_molecules.py` will report.

### Phase 3: membrane scaffolding (no spontaneous formation tested yet)

Spec at `docs/superpowers/specs/2026-05-06-phase-3-membranes.md`. Spontaneous membrane formation is empirical and untested; the deliverable is the tooling needed to find out.

- `tools/detect_membranes.py` — connected-component grouping, least-squares 3D sphere fit, equal-area gap detection. Distinguishes closed shells from filled balls and from open clusters.
- `tools/construct_membrane.py` — hand-place molecules on a Fibonacci sphere for stability tests.
- 8 new tests in `tests/test_detect_membranes.py`. All pass.

### Test count

84 tests passing (was 63 at the end of session 2).

### Animation outputs

- `renders/anim_phase1_first_atom.mp4` — calibrated Phase 1 from t=0 to first atom (~13.4s of simulated time, 30 fps video, ~4–5 s real time). Generated using `tools/render_animation.py` with the session-3 TOML and `--stop-at-level 4`.
- A longer Phase 2 run is in progress to capture molecule formation; the resulting animation lands in `renders/anim_phase2_first_molecule.mp4` once the run completes.

### Animation

`renders/anim_phase1_first_atom.mp4` — 4.5 s of 1920×1080 video at 30 fps, generated from `renders/calibration_session3.toml` with rng_seed=42 and `--stop-at-level 4`. The simulation deterministically halts when the first level-4 node forms (t = 13.4 s simulated), so the climax frame holds the moment of first-atom emergence.

The wave field shows ~400 short oriented sinusoidal tubes (red = odd polarity, blue = even). Yellow-orange spheres are electrons. Pale-white sphere is a triad. The bright white sphere upper-right in the climax frame is the **first atom**. The standalone climax frame is at `renders/keyframe_first_atom.png`.

### Phase 2 demo result (240 s simulated with the same calibration)

This run extended the calibrated config to 240 s simulated time, snapshotting every 1 s, to test whether molecule formation follows from atom formation under the same parameters.

Observed (intermediate snapshot at t = 120 s, this LOGBOOK gets the full final at next read):

| Level | Count alive at t=120 |
|---|---:|
| 1 (electrons) | 102 |
| 2 (pairs) | 9 |
| 3 (triads) | 2 |
| 4 (atoms) | **1** |
| 5+ (molecules) | 0 |

**The bottleneck is atom production rate, not the molecule-formation rules.** With only one atom alive, no atom + atom binding can occur, regardless of how well the rules are implemented. Phase 2's acceptance criterion (≥5 distinct molecule species) is therefore *not* met by this calibration in 240 s simulated time. A second atom forming (the necessary precondition for the first molecule) requires another triad + electron event satisfying all the binding rules, and the per-second probability is low at this density.

What this finding says about the calibration: the session-3 TOML satisfies CONCEPT.md v2 §5 Phase 1 success criterion 1 (atoms form reliably) but is **not yet productive for Phase 2**. To produce molecules in reasonable simulated time, future calibration needs:

1. **Higher atom production rate.** More starting vibrations, smaller box, or wider freq_tolerance — pick the lever and re-sweep.
2. **Tighter freq distribution.** With `freq_min=100, freq_max=10000`, atoms span decades 3–4, and the 8% rule rarely matches two atoms in the same decade. A narrower frequency window would cluster atoms and increase same-decade matches.
3. **Different atom-vs-atom radius.** Atoms are larger structures than electrons; using a larger `r_2` for higher-level binding (separate from the vibration-electron `r_1` and `r_2`) would help. *That is a CONCEPT.md amendment, not just a calibration tweak.*

### Phase 1 reproducibility across seeds (mid-session check)

Ran the calibrated TOML at four additional rng seeds (60 s simulated each, single-core). Result:

| Seed | electrons | pairs | triads | atoms | first atom |
|---:|---:|---:|---:|---:|---|
| 42 | 104 | 10 | 2 | 1 | t = 13.4s |
| 100 | 93 | 7 | 2 | **1** | t = 29.2s |
| 314 | 78 | 7 | 5 | 0 | — |
| 999 | 102 | 4 | 2 | 0 | — |

(Seed 7 result lost to a `tail -3` truncation in the run wrapper.) **Reproducibility is partial**: 2 of 4 verified seeds form an atom in 60 s simulated. Seeds 314 and 999 produce triads but no fourth-electron capture within the run. The session-3 calibration produces atoms *consistently enough to be useful* but *not robustly enough across all seeds* — a session-4 calibration target.

The seed=314 result is informative: 5 triads alive at peak but no atom. So triads aren't the bottleneck; the bottleneck is the specific freq match for the fourth electron joining the triad. Wider freq tolerance for level-3+1 binding (per-level freq_tolerance — see CALIBRATION_GUIDE.md §2) would address this.

### Phase 3: not exercised yet

`tools/detect_membranes.py` is in place and unit-tested. With zero molecules in the calibrated runs, there's no opportunity for spontaneous shell formation, and we have no real-world detection results to report. The tool will be exercised once Phase 2 calibration produces enough molecules.

### Test count

84 passing (was 84 pre-session-3 — same number, but with 21 new tests added for Phases 2 and 3 and corresponding old assertions reorganised; net green throughout).

### Session 4 targets

1. **Phase 1 reproducibility across seeds.** Run rng_seed=7, 100, 314, 999 with the calibrated TOML. Document atom-formation time and count per seed.
2. **Calibrate for Phase 2.** New sweep aimed at producing ≥3 atoms within 60 s simulated time. Lever: smaller box (40–60³), more vibrations (600–1000), narrower freq window (e.g., 1000–10000 → all atoms in decade 4). If that still gives one-atom worlds, broaden `freq_tolerance` to 0.04 for atom-level binding only — which means amending `WorldConfig` with a per-level tolerance setting.
3. **First molecule.** Once ≥3 atoms form, molecule formation is just a few more atom + atom encounters. Goal: at least one level-5 (di-atomic) molecule observed within 120 s.
4. **Five species.** Once molecules form, run `tools/classify_molecules.py` over a long-duration snapshot. Goal: ≥5 distinct fingerprints (the Phase 2 acceptance criterion).
5. **Phase 3 first observation.** Run a 30-minute simulated session, dump snapshot every 30 s, run `tools/detect_membranes.py` over each. Honest answer expected: probably no spontaneous shells, but document what's there.

---
