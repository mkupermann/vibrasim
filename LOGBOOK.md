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
