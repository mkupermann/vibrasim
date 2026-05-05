# Calibration Guide

Practical notes for continuing where session 3 left off. The goal of each session is to find a `WorldConfig` that satisfies one or more CONCEPT.md v2 success criteria. This document records what's been learned and the next levers to pull.

---

## Current state (end of session 3)

- **Phase 1 §5.1** (atoms reliably form) — **met** by `renders/calibration_session3.toml`. With rng_seed=42, first atom at t=13.4 simulated seconds.
- **Phase 1 §5.2** (spatial sorting H2 — atoms cluster by frequency decade under `§4.6` repulsion) — **untested**. The current calibration produces ~1 atom per run, all in a single decade (decade 3 at the test seed). Multi-decade behaviour requires either a wider initial frequency window or many more atoms.
- **Phase 1 §5.3** (ambient stability with `λ_gen > 0`) — **untested**. The current calibration uses `λ_gen = 0` for clean observation.
- **Phase 2 §6 Phase 2** (≥5 distinct molecule species reproducible) — **not met**. The current calibration produces only one atom per run; without ≥2 atoms, no atom-atom binding can occur and no molecules form.
- **Phase 3** (membrane formation) — **not yet exercised**. The detection tooling is in place; spontaneous shells require Phase 2 first.

---

## Calibration loop

1. Pick a target (e.g. "produce ≥3 atoms in 60 s simulated"). Be specific.
2. Identify the lever to vary (one or two parameters at most).
3. Write a sweep script under `/tmp/` that runs 4–8 configs in parallel via `multiprocessing.Pool`. Each worker constructs a `World` from a `WorldConfig`, ticks for the target duration, records `max counts per level` and `time of first level-N node`.
4. Output to a JSONL file so the run is resumable / diffable.
5. Pick the leader and either commit a new TOML at `renders/calibration_sessionN.toml` or run a longer-duration verification before locking it in.
6. Update `LOGBOOK.md` with the table of results and the chosen leader.

The existing tools `tools/sweep.py` (with grid/random/Optuna backends) cover this workflow once you've defined an objective function. For exploratory sweeps with a few hand-picked configs, a single-purpose script in `/tmp/` is faster and just as good.

---

## Levers that mattered in session 3

| Lever | What it controls | Direction that helps |
|---|---|---|
| `box_size` (smaller) | Vibration density | Smaller box → higher density → more encounters → faster electron formation |
| `r_2` (larger) | Higher-level binding range | Larger `r_2` → more node-pair encounters per unit time |
| `freq_tolerance` (wider) | Frequency-rule strictness | Wider tolerance → more pairs satisfy the 8% rule |
| `pair_decay_time`, `triad_decay_time` (longer) | Lifetime of unstable nodes | Longer lifetime → more time for the next-level partner to find them |
| `n_initial_vibrations` (more) | Initial population | More vibrations → linear scaling of electron formation |
| `lambda_gen` (zero) | Ambient regeneration | Zero → constant population, easier to interpret |

Levers that didn't help much:
- Switching `freq_distribution` from log to uniform — minimal observable difference at session-3 scales
- Touching `r_1` away from 5.0 — the vibration-electron rate is rarely the bottleneck once density is right

---

## Recommended next experiments

In rough priority order:

### 1. Multi-atom regime

The session-3 winner produces 1 atom in 120 s. To exercise Phase 2 we need 3+ atoms in roughly the same time. Try in parallel:

| Variant | Why it might work |
|---|---|
| Smaller box (50³ or 60³) at the same `n_init` | Higher density → more triad-formation events → more atoms |
| Wider `freq_tolerance` (0.030–0.040) | Each atom-formation event is rarer than electron-formation; widening tolerance helps the higher levels disproportionately |
| Higher `n_init` (800–1500) at box=80³ | Linear scaling of atom production |
| Narrower `freq_min`/`freq_max` (e.g. 1000–10000) | Concentrates atoms in fewer decades; same-decade matches more likely for atom-atom binding |

### 2. Per-level freq_tolerance (config-amendment)

`WorldConfig` currently has a single `freq_tolerance`. Because higher-level nodes have larger frequencies, the 8% rule becomes harder to satisfy at higher levels (small relative tolerance becomes a small absolute window in a large frequency range). Adding `freq_tolerance_atom` and `freq_tolerance_molecule` fields would let calibration loosen the rule selectively for the slow steps.

This is a real spec amendment. Update CONCEPT.md §4.4–§4.5 to acknowledge the per-level relaxation, and add the fields to `WorldConfig`. Mention it explicitly in LOGBOOK so the change is auditable.

### 3. Reproducibility across seeds

Once a calibration produces atoms, run it under rng_seed=7, 100, 314, 999 and confirm atoms form within ~30 s simulated in each. Document the per-seed first-atom time. If the variance is too large (e.g. one seed never produces an atom in 60 s), the calibration isn't robust enough yet.

### 4. Ambient stability

Set `λ_gen > 0` and find the value that holds population steady within ±20 % over 60 s. Start sweeping in `[1e-10, 1e-7]` per-volume per-second. The default `1e-4` saturated capacity in seconds; the right value is several orders of magnitude lower.

### 5. Phase 2 first molecule

Once Phase 1 produces 3+ atoms, the first molecule should follow within 60–120 s. Run for 240+ s and use `tools/classify_molecules.py` to count species fingerprints. Goal: ≥5 distinct fingerprints.

### 6. Phase 3 first observation

Run a 30-minute simulated session. Snapshot every 30 s. Run `tools/detect_membranes.py` over each snapshot. Honest expectation: zero candidates with the current natural laws — but document what's there.

---

## Useful one-liners

```bash
# Start a clean sweep
rm -f /tmp/sweep.jsonl
python tools/sweep.py --backend grid \
  --params-toml /tmp/sweep_ranges.toml \
  --duration 60 --workers 4 \
  --output /tmp/sweep.jsonl

# Inspect the latest snapshot from a long run
latest=$(ls renders/anim-work/snapshots | tail -1)
python tools/classify_molecules.py renders/anim-work/snapshots/$latest

# Render a specific snapshot
blender -b -P tools/render_blender.py -- \
  --snapshot renders/anim-work/snapshots/$latest \
  --output /tmp/keyframe.png \
  --quality medium --engine cycles

# Build an animation from a calibrated TOML to first atom
python tools/render_animation.py \
  --config renders/calibration_session3.toml \
  --max-duration 30 --snapshot-stride 6 --stop-at-level 4 \
  --quality low --engine eevee --fps 30 \
  --output renders/my_animation.mp4

# Detect membranes (returns empty until Phase 2 produces molecules)
python tools/detect_membranes.py snapshot.npz
```

---

## What's not negotiable

- **The natural laws** in CONCEPT.md v2 §4 don't change without a documented amendment. If a calibration "would work if r_2 were per-level" or "if 8% became 12% at higher levels", that's a SPEC change, not a knob — write the amendment to CONCEPT.md, log it, then proceed.
- **Phase order** (1 → 2 → 3 → …) is preserved. Phase 2 calibration doesn't begin until Phase 1 produces atoms reliably across seeds.
- **rng_seed in any TOML.** Reproducibility is the floor; non-deterministic results don't count.
