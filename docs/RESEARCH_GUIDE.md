# Research Continuation Guide

How to pick up vibrasim from session 4 and keep the research moving forward. This document is the comprehensive operational guide — it assumes nothing about the reader's familiarity with the project.

Read sections 0, 1, 2 before doing anything else. Sections 3–11 are reference material you come back to as needed.

---

## Part 0 — Read this first

### What this project is

A simulated 3D physical world built from a single primitive (the *vibration*). Through a small set of natural laws, vibrations bind into electrons, then atoms, then molecules. Higher phases of the research programme add membranes, neurons, synapses, networks, and attention. The full conceptual case is in `docs/CONCEPT.md` (v2 incorporates peer-review feedback). The eight-phase plan is in `files/SKILL.md`.

The project is **research code**, not a product. The defaults are deliberately documentary; the calibrated configurations live in `renders/calibration_*.toml`. Read `LOGBOOK.md` end-to-end before touching anything — it records the entire empirical history including the recent five-agent research session.

### What "done" means here

A phase is **scaffolded** when the spec, construction tools, detection tools, measurement tools, and tests exist. Scaffolded ≠ working. A phase is **closed** when the substrate produces the phase's signature behaviour empirically (e.g., atoms reliably forming, ≥5 molecule species, neurons firing under stimulation). The two are separate milestones.

| Phase | Scaffolded | Closed | Closing requires |
|---|---|---|---|
| 1 | yes | **yes** | atom forms reproducibly across rng_seeds at the calibrated TOML |
| 2 | yes | **yes** | ≥5 species at `renders/calibration_phase2_acceptance.toml` |
| 3 | yes | no | substrate amendment OR much higher molecule density |
| 4 | yes | no | substrate amendment (charge + threshold + refractory rules) |
| 5 | yes | no | substrate amendment (4 rules — see Part 5) |
| 6 | yes | no | downstream of Phase 5 |
| 7 | yes | no | downstream of Phase 6 + a global carrier mechanism |
| 8 | n/a | n/a | open research, not planned in advance |

### What's *not* in scope right now

- GPU / CUDA work. Phases 4+ would need it eventually (per CONCEPT.md v2 §10.6) but the substrate amendments below all run on CPU.
- Real-time animation polish. The renderer works; calibration matters more.
- Cross-platform packaging. The repo runs on macOS arm64 with Python 3.13. Linux likely works; Windows untested.

---

## Part 1 — Setting up your environment

This must be done in order. Don't skip steps.

### 1.1 Clone the repo

```bash
git clone https://github.com/mkupermann/vibrasim.git
cd vibrasim
```

If you're already in a working clone, `git fetch && git status` first to check for upstream changes.

### 1.2 Confirm Python and Blender versions

```bash
python3.13 --version    # must be 3.13.x — Numba 0.65 has no 3.14 wheel yet
blender --version       # any 5.x; 5.1.1 was used in the original calibration
```

If `python3.13` isn't available: `brew install python@3.13` on macOS, or install via your distro's package manager. **Don't use 3.14** — Numba breaks.

If Blender isn't installed: `brew install --cask blender` on macOS. The research doesn't strictly require Blender (only the high-quality renders do) but `tools/render_blender.py` and `tools/render_animation.py` won't work without it.

### 1.3 Create the virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

The `-e` (editable) install matters — it lets you modify `world/` and re-run tests without reinstalling.

The optional `[dev]` brings in `pytest` and `matplotlib`. They're required for tests and histograms.

### 1.4 Verify the install

Activate the venv (`source .venv/bin/activate`) for everything below.

```bash
pytest
```

You should see `148 passed` (or higher if more tests have landed). If anything fails, **stop and fix** — don't try to do research on a broken baseline. Common causes:

- Numba cache from a previous Python version: `rm -rf world/__pycache__/ tools/__pycache__/`
- Missing optional deps: `pip install matplotlib pyvista optuna`
- Open3D/PyVista version mismatch: the codebase uses PyVista 0.48; Open3D was the original choice but doesn't ship a 3.13 wheel.

### 1.5 Reproduce the two closed-phase results

These are the floor — if either one doesn't reproduce, your environment differs from the reference and conclusions about new work can't be trusted.

**Phase 1 — first atom at t = 13.4 s simulated:**

```bash
python -c "
from pathlib import Path
import time
from world.config import load_config
from world.state import World
from world.physics import tick

cfg = load_config(Path('renders/calibration_session3.toml'))
w = World(cfg)
n_ticks = int(20.0 / cfg.dt)
import math
t_first_atom = math.inf
start = time.time()
for k in range(n_ticks):
    tick(w, cfg.dt)
    if math.isinf(t_first_atom) and ((w.k_level == 4) & w.k_alive).any():
        t_first_atom = w.t
        break
print(f'first atom at t = {t_first_atom:.2f}s, wall = {time.time()-start:.0f}s')
"
```

Expected: `first atom at t = 13.40s` (or very close — exact reproducibility requires the same NumPy + Numba versions). If you get a different time but an atom *does* form within 60s simulated, the calibration is reproducing. If no atom forms, something is wrong.

**Phase 2 — ≥5 species at t = 60 s simulated:**

```bash
mkdir -p /tmp/p2_check
python -c "
from pathlib import Path
import time
from world.config import load_config
from world.state import World
from world.physics import tick
from world.snapshot import save_snapshot, snapshot_filename

cfg = load_config(Path('renders/calibration_phase2_acceptance.toml'))
w = World(cfg)
n_ticks = int(60.0 / cfg.dt)
start = time.time()
for k in range(n_ticks):
    tick(w, cfg.dt)
save_snapshot(w, Path('/tmp/p2_check/snapshot_t000060.00.npz'))
print(f'wall: {time.time()-start:.0f}s')
"
python tools/classify_molecules.py /tmp/p2_check/snapshot_t000060.00.npz
```

Expected: `6 distinct species, 17 molecules total` (A33, A44, A3334, A444, A33334, A3344) and ~223 s wall time. If you see fewer species, either the environment differs or the calibration TOML was edited.

If both reproductions pass, your environment is sound and you can start research.

---

## Part 2 — Understanding the current state

Read these files in this order. Don't research before you've read them.

1. **`docs/CONCEPT.md`** — the conceptual case. v2 with peer-review-incorporated amendments.
2. **`files/SPECIFICATION.md`** — the substrate's natural laws. The 8% rule, decade isolation, polarity randomisation, etc.
3. **`files/SKILL.md`** — the eight-phase plan in operational form.
4. **`LOGBOOK.md`** — every session's empirical observations. The recent session-4 entry is the most current state-of-affairs.
5. **`docs/research_session4/`** — five teammate-agent reports from the most recent research session. Phase 2 / Phase 3 / Phase 4 / Phase 5 findings + the independent code review.
6. **`docs/CALIBRATION_GUIDE.md`** — practical recipe for parameter sweeps.
7. The seven phase specs in `docs/superpowers/specs/` — read whichever phase you're working on.

The implementation lives in `world/` (the substrate) and `tools/` (the analysis layer). Tests live in `tests/`. Renders / TOMLs / animations live in `renders/`.

### What changed in session 4 (read this if you're picking up cold)

- Phase 2 acceptance met by widening `freq_tolerance` from 0.030 to 0.200 (`renders/calibration_phase2_acceptance.toml`).
- Four critical bugs fixed (C2, C3, C6, I1). The most consequential was C6: `measure_synapse_plasticity` was silently returning the mean window start time instead of the actual slope. Any prior Hebbian-signal numbers in the LOGBOOK are wrong.
- Five teammate agents documented exactly what substrate amendments are needed for Phases 3, 4, 5. See Part 5.

### Test count

148 tests passing as of `e7ca5f6`. If you see fewer, you're behind; pull. If you see more, someone's been working — review their commits.

---

## Part 3 — The research workflow

This is the meta-process for a single research session. Follow it for every session. Skipping steps creates technical debt that kills the project.

### Step 1: Pick a research question

Choose **one** open acceptance criterion from Part 4 and **one** from these patterns:

- **Calibration question:** can the existing substrate produce X under different parameters?
- **Substrate-amendment question:** what minimal rule change unlocks X?
- **Tool question:** does our measurement of X actually capture what we think it does?

Don't pick more than one. Phase 5 and Phase 4 are tempting in parallel but they couple in non-obvious ways and the combined work is hard to attribute.

### Step 2: State the question precisely

Write the question down in the LOGBOOK as the start of a new session entry. Include:

- The exact acceptance criterion or hypothesis
- The current state ("baseline: with config X, we observe Y")
- The variable you'll change ("test: vary parameter P over range [a, b] and measure Z")
- What outcome would close the question vs. leave it open

If you can't state it precisely, you don't understand it well enough yet — keep reading the spec and code.

### Step 3: Decide: calibration or substrate amendment?

Calibration is cheaper but bounded. If the substrate doesn't have the mechanism for X, no calibration produces X. Re-read the relevant spec section.

- **Calibration if:** existing rules can plausibly produce X under different parameters (Phases 1, 2 fit here).
- **Substrate amendment if:** existing rules cannot produce X (Phases 3, 4, 5 currently fit here per session-4 findings).

If you're unsure, run a quick calibration sweep first. If it fails, you have evidence the substrate needs amending.

### Step 4: For calibration — design and run a sweep

See Part 6 for the detailed how-to. The short version:

1. Write a sweep script under `/tmp/sweep_<topic>.py` (don't pollute the repo with experiment scripts — the LOGBOOK records what you did).
2. Run it. Use `multiprocessing.Pool` for parallelism but be honest about CPU contention if other things are running.
3. Save the JSONL results to `/tmp/<topic>.jsonl`.
4. Inspect the leader. If it's a clear winner, save its TOML to `renders/calibration_<session_number>_<topic>.toml`.
5. Re-run the leader at a longer duration (60s → 300s) to verify it doesn't break.
6. Document in LOGBOOK.

### Step 5: For substrate amendment — spec first, code second

You **must** write the spec amendment in CONCEPT.md before changing code. The order matters because:
- Code without spec drift is documented as drift; code with spec amendment is documented as an amendment.
- The spec gives you a clear acceptance criterion ("this rule, with these tests").
- Future sessions can read the amendment and understand what changed.

The amendment workflow:

1. Open `docs/CONCEPT.md`.
2. Add a new subsection — typically a new §4.x or §6.x for substrate rules.
3. State the rule operationally (what changes per tick).
4. State the acceptance criterion (what observable property the amendment unlocks).
5. State the open question (what the empirical test will resolve).
6. Update the relevant phase entry in §5 to reference the amendment.
7. Commit the spec amendment alone. Don't bundle code.
8. Then implement: edit `world/physics.py` (or `world/state.py`, or wherever).
9. Add tests for the new rule. Tests must include both positive cases (rule fires when expected) and negative cases (rule doesn't fire when it shouldn't).
10. Run the full test suite. Nothing pre-existing should break.
11. Commit the implementation with a message that references the spec amendment commit.

### Step 6: Verify with a calibrated run

Run the simulation forward with the amended substrate, using the most relevant calibration TOML. Use the corresponding measurement tool (`tools/measure_*.py`) to extract the metric you care about. Document the result.

### Step 7: Update LOGBOOK and push

End the session entry with what you found. Mark which acceptance criteria moved from "pending" to "met" (or vice versa). Push.

If you stop working mid-session, write a "session paused at step N" note. Resume from there next time.

---

## Part 4 — Phase-by-phase next steps

The research questions, in priority order based on what's most informative.

### Phase 5 (synapse plasticity) — the highest-leverage open question

CONCEPT.md v2 §6.5 says this *might* fail. The Phase 5 calibration agent showed that without four substrate amendments, the §6.3 Hebbian mechanism cannot even be tested. The most informative single piece of work right now is implementing those four amendments and seeing if Hebbian plasticity emerges.

**Required amendments** (per `docs/research_session4/phase5_findings.md`):

1. **R1 — Vibration injection that doesn't no-op.** Either enlarge `n_vibrations_max` to ~16000 with a calibrated `lambda_gen`, or implement a "displace" injection that moves a far-field alive vibration to the target zone (preserves global count, creates local gradient).
2. **R2 — Decay channel for level-5+ nodes.** Add per-tick decay probability `lambda_dec_mol * dt` for level-5+, reviving constituent atoms. CONCEPT.md §4.7 amendment.
3. **R3 — Local capture / assembly rule.** When vibration density near a region exceeds a threshold, assemble a new level-5 store molecule there. CONCEPT.md §6.3 amendment — this is the "ambient capture" mechanism made explicit.
4. **R4 — Activity detector that sees synapse-region events.** Either track level-5 *count changes* near outlet/inlet, or shrink `n_vibrations_max` so vibrations accumulate locally.

Sequence: R5 (the C6 fix in `measure_synapse_plasticity`) is already done. Implement R1 first (it's a config change), then R2 (small physics addition), then R3 (the conceptually load-bearing amendment), then R4 (measurement update). Test each in isolation before combining.

If R1-R4 land and the §6.3 mechanism produces a positive Hebbian signal, Phase 5 closes and Phase 6 / 7 are unlocked. If it doesn't, the failure mode is precise enough to be a publishable negative result.

### Phase 4 (single-neuron firing)

Per `docs/research_session4/phase4_findings.md`, the substrate is missing four rules to produce neuron-like firing:

1. **`k_charge[K]` per-atom accumulator** with exponential decay (membrane time constant τ_m ≈ 10 ms simulated).
2. **Threshold rule in `tick()`** — when any inlet atom's charge ≥ θ, emit N_out vibrations at the outlet and reset charge.
3. **Refractory rule** — lock charge accumulation for T_r after each emission.
4. **Directional inlet geometry** — frequency-band inlet atoms to match injection frequencies.

Estimated 40-60 additive lines in `world/state.py` + `world/physics.py`. Each rule needs a test.

This work runs in parallel with Phase 5 if two researchers / sessions are available. They don't share state.

### Phase 3 (membrane formation)

The Phase 3 agent showed that constructed shells are stable indefinitely but molecule density never reaches the ≥12 threshold the detector requires. Two options:

1. **Add molecule-molecule binding.** Append `(5, 5)`, `(5, 6)`, etc. to `_UPGRADE_TARGET`. Spec amendment in §4.5. This unlocks a condensation pathway that doesn't require free-atom intermediaries.
2. **Re-run Experiment A with the Phase 2 acceptance config.** It produces 17 molecules — closer to the ≥12 threshold than session-3b's 2. Even if no spontaneous shell forms, getting closer is progress.

Try (2) first — it's a 30-minute experiment with no spec amendment. If it fails, do (1).

### Phase 2 (more species)

Acceptance is met (6 species). To go further: the C7_twodecade_wide variant in `docs/research_session4/phase2_findings.md` produced 10 species. Promote it as `renders/calibration_phase2_extended.toml` and document. This is a reproducibility check rather than new research.

### Phase 1 (reproducibility across seeds)

The session-3 verification showed atoms form reliably at seeds 42 and 100 but not 314 or 999 in 60 s. The Phase 2 acceptance config has wider tolerance — re-run the seed verification with it and document. If it now reproduces atoms across all seeds, that's a more robust Phase 1 closure.

### Phase 6, 7

Both downstream of Phase 5. Don't work on them until Phase 5 has at least the R1-R3 amendments.

### Code-review still-open items

From `docs/research_session4/code_review.md`:

- **C1** — `detect_synapses` axis alignment is silently disabled. Either implement axis inference from cluster morphology or amend Phase 5 spec §2.
- **C4** — `measure_neuron_activity`'s integration_lag uses wrong window logic. Sustained-input-window detector needed.
- **C5** — `detect_networks` end-to-end broken on constructed snapshots. Needs density-based clustering (DBSCAN-style); flagged in Phase 5 spec.
- **I3, I4, I6** — minor spec drift on resonance clipping, Hamming convention, phase grid resolution.

These are engineering fixes, not research. Tackle them between research sessions when you want lower-cognitive-load work.

---

## Part 5 — How to amend the substrate

This is the most consequential kind of change. Get it wrong and the entire research pivots on a buggy rule.

### Pre-flight checklist

- ✅ The amendment is documented in CONCEPT.md before any code is touched.
- ✅ The acceptance criterion for the amendment is clear and falsifiable.
- ✅ At least one negative test case is identified (a scenario where the rule should *not* fire).
- ✅ The amendment doesn't break any of the 148 existing tests.

If any of these is missing, stop and finish them.

### Step-by-step

1. **Write the amendment in CONCEPT.md.** Add a subsection (e.g., §4.8 ambient injection, §4.9 charge accumulation). State:
   - The new variable / rule mechanically
   - The new parameters introduced (with default values)
   - How the rule integrates with the tick order (before / after which existing step)
   - The expected observable consequence
   - The acceptance test

   Commit alone:

   ```bash
   git add docs/CONCEPT.md
   git commit -m "spec(amendment): §4.8 ambient injection mechanism

   [body explaining the rule]"
   ```

2. **Write the failing test.** Before adding the rule to the substrate, write a test in `tests/test_<rule_name>.py` that asserts the new behaviour. Run it and confirm it fails.

   ```bash
   pytest tests/test_<rule_name>.py -v
   ```

   Expected: failure (the rule doesn't exist yet). If it passes spuriously, your test is wrong.

3. **Implement the rule.**
   - Add new fields to `WorldConfig` if needed.
   - Add new arrays to `World` if needed (mind the SoA discipline — NumPy arrays, not Python objects).
   - Add the new function (or modify `tick`) in `world/physics.py`.
   - For new tick steps, decide where in the tick order they go (before or after motion / binding / decay / ambient).

4. **Re-run the test.** It should pass.

5. **Run the full test suite.** Nothing pre-existing should break.

   ```bash
   pytest
   ```

   If anything breaks, the amendment has unintended side effects. Investigate and either fix the test (if its expectation was tied to old behaviour) or fix the rule (if the new behaviour is wrong).

6. **Add a calibration check.** Run a 30 s simulation with the amended substrate using a known-productive TOML (`renders/calibration_phase2_acceptance.toml` is the current default). Confirm that:
   - The amendment doesn't kill productivity (atoms still form, molecules still form).
   - The amendment produces the new observable consequence.

7. **Document in LOGBOOK.** Session entry includes the amendment description, the test that verifies it, and the calibration check result.

8. **Commit the implementation.**

   ```bash
   git add world/ tests/
   git commit -m "feat(amendment): §4.8 ambient injection — implementation

   Implements the spec amendment from commit <SHA>. Adds:
   - WorldConfig.lambda_inject (default X)
   - World.s_pos[N] used by inject_at_region()
   - tick() step 8 calls inject_at_region after ambient_regeneration

   Test: tests/test_ambient_injection.py (3 tests, all passing).
   Full suite: 151 passing."
   ```

9. **Push.**

   ```bash
   git push
   ```

### Substrate amendment anti-patterns

Avoid these. They're the things I caught myself doing during session 4 and had to walk back:

- **Tweaking the rule until tests pass.** If the spec says X and the test expects X but the implementation does Y, fix the implementation, not the test.
- **Adding the rule without a default.** New WorldConfig fields must have defaults that don't change the behaviour of existing TOMLs. Otherwise old configs break.
- **Skipping the calibration check.** A new rule that passes unit tests can still kill productivity in a calibrated world. Run the 30s smoke before declaring done.
- **Bundling unrelated changes.** One amendment per commit. Bundling makes bisection impossible.

---

## Part 6 — How to run a calibration sweep

The standard workflow for parameter exploration.

### Step 1: Decide what's varying

Pick **one or two** parameters to vary. More than that is shotgun research — too many variables, too few observations per cell, no causal conclusions.

Common variables and what they do:

| Parameter | Range I've seen work | Effect |
|---|---|---|
| `box_size` | (40, 40, 40) — (1000, 1000, 1000) | smaller = denser = more encounters |
| `n_initial_vibrations` | 200 — 2000 | linear scaling of electron formation |
| `r_2` | 10 — 50 | wider = more node-pair encounters |
| `freq_tolerance` | 0.005 — 0.20 | wider = more pairs satisfy 8% rule |
| `freq_min` / `freq_max` | (100, 10000) default | narrower = atoms cluster in same decade |
| `pair_decay_time` | 5 — 600 (seconds) | longer = more time for triad formation |
| `triad_decay_time` | 30 — 1200 (seconds) | longer = more time for atom formation |
| `lambda_gen` | 0 — 1e-3 (per unit volume per second) | nonzero replenishes vibrations |
| `lambda_dec` | 0 — 0.01 (per node per second) | nonzero decays unstable nodes back |

### Step 2: Write the sweep script

Save under `/tmp/sweep_<topic>.py`. Don't put it in the repo unless it's a reusable harness.

Template:

```python
"""Sweep <topic>: vary <param> from <a> to <b>."""
from dataclasses import replace
import json
import math
import time
from multiprocessing import Pool
from world.config import WorldConfig
from world.state import World
from world.physics import tick

# Define the configs to test
CONFIGS = [
    # (label, param_value)
    ("low",    1.0),
    ("med",    5.0),
    ("high",  10.0),
    # ... etc
]

def run_one(args):
    label, param_value = args
    cfg = WorldConfig(
        # ... static params here
        # Vary the one parameter
        # freq_tolerance=param_value,  # for example
        rng_seed=42,
    )
    w = World(cfg)
    duration = 60.0
    n_ticks = int(duration / cfg.dt)
    seen = {l: 0 for l in range(1, 12)}
    first_seen = {l: math.inf for l in range(1, 12)}
    start = time.time()
    for k in range(n_ticks):
        tick(w, cfg.dt)
        for level in range(1, 12):
            n = int(((w.k_level == level) & w.k_alive).sum())
            seen[level] = max(seen[level], n)
            if n > 0 and math.isinf(first_seen[level]):
                first_seen[level] = w.t
    wall = time.time() - start
    return {
        "label": label,
        "param_value": param_value,
        "max_counts": seen,
        "first_seen": {k: (None if math.isinf(v) else round(v, 2)) for k, v in first_seen.items()},
        "wall_s": round(wall, 1),
    }


if __name__ == "__main__":
    print(f"{'label':12s} {'param':>6s} {'e':>4s} {'pair':>4s} {'tri':>3s} {'atom':>4s} {'mol5':>4s}  wall")
    print("-" * 70)
    with Pool(processes=4) as pool:
        for r in pool.imap_unordered(run_one, CONFIGS):
            m = r["max_counts"]
            print(f"{r['label']:12s} {r['param_value']:>6.3f} {m[1]:>4d} {m[2]:>4d} "
                  f"{m[3]:>3d} {m[4]:>4d} {m[5]:>4d}  {r['wall_s']:>4.0f}s",
                  flush=True)
            with open("/tmp/sweep_<topic>.jsonl", "a") as fp:
                fp.write(json.dumps(r) + "\n")
```

### Step 3: Run it

```bash
rm -f /tmp/sweep_<topic>.jsonl
source .venv/bin/activate
python /tmp/sweep_<topic>.py
```

For long sweeps, run in the background:

```bash
nohup python /tmp/sweep_<topic>.py > /tmp/sweep_<topic>.log 2>&1 &
```

Watch progress: `tail -f /tmp/sweep_<topic>.log`.

### Step 4: Inspect results

```bash
cat /tmp/sweep_<topic>.jsonl | python3 -c "
import json, sys
configs = sorted([json.loads(line) for line in sys.stdin],
                 key=lambda r: -r['max_counts'].get(4, 0))  # sort by max atoms
for r in configs[:5]:
    print(f\"{r['label']}: atoms={r['max_counts'][4]} mol5={r['max_counts'][5]}\")
"
```

### Step 5: Promote a winner

If one config dominates, save its TOML:

```bash
cat > renders/calibration_session<N>_<topic>.toml <<EOF
# Session <N> calibration — <topic>
# In <duration>s simulated with rng_seed=42:
#   - <atom count>
#   - <molecule species>
# ...

box_size = [60.0, 60.0, 60.0]
# ... full config here
EOF
```

Then verify the TOML matches what the script ran:

```bash
python -c "
from pathlib import Path
from world.config import load_config
cfg = load_config(Path('renders/calibration_session<N>_<topic>.toml'))
print(cfg)
"
```

### Step 6: LOGBOOK

A new session entry with the table of results. **Include the JSONL filename or paste the data inline.** Future-you will need to bisect when something stops reproducing.

---

## Part 7 — How to use each tool

Reference. Skim now; come back when you need each one.

### Substrate / state

| Tool | Purpose |
|---|---|
| `python -m world run --duration N --snapshot-every M --snapshot-dir <dir> --config <toml>` | Run the substrate forward, save snapshots |
| `python -m world run --preview --duration N --config <toml>` | Same but with PyVista live preview |

### Analysis (single snapshot)

| Tool | Purpose |
|---|---|
| `python tools/classify_molecules.py <snapshot.npz>` | Count distinct molecule species fingerprints |
| `python tools/detect_membranes.py <snapshot.npz>` | Find closed-shell candidates |
| `python tools/detect_neurons.py <snapshot.npz>` | Find compact neuron candidates |
| `python tools/detect_synapses.py <snapshot.npz>` | Find neuron pairs at synapse distance |
| `python tools/detect_networks.py <snapshot.npz>` | Find connected components ≥3 neurons |
| `python tools/histogram.py <snapshot.npz>` | Frequency-decade histograms |

### Analysis (snapshot sequence)

| Tool | Purpose |
|---|---|
| `python tools/measure_neuron_activity.py --snapshot-dir <dir> --centre X,Y,Z --axis 1,0,0 --radius 6` | Track input/output activity, detect firings |
| `python tools/measure_synapse_plasticity.py --snapshot-dir <dir> --pre-centre A --post-centre B --neuron-radius 6` | Track Hebbian signal |
| `python tools/measure_network_activity.py --snapshot-dir <dir> --neurons-json <file>` | Build firing matrix + correlation |
| `python tools/measure_attention_selectivity.py --firing-json <file> --carrier-frequency F` | Identify resonating subset |

### Construction (synthesis tools — no real binding)

| Tool | Purpose |
|---|---|
| `python tools/construct_membrane.py --output <npz> --centre X,Y,Z --radius R --n-molecules N` | Hand-place a Fibonacci shell |
| `python tools/construct_neuron.py --output <npz> --centre X,Y,Z --radius R --axis A` | Hand-place a candidate neuron cluster |
| `python tools/construct_synapse.py --output <npz> --pre-centre A --post-centre B` | Hand-place two neurons + cleft + store + receivers |
| `python tools/construct_network.py --output <npz> --topology <json>` | Place N neurons + M synapses |
| `python tools/synthesize_carrier_firing.py --output <json> --resonating-indices i,j,k` | Synthetic firing matrix for carrier tests |

### Calibration / sweeps

| Tool | Purpose |
|---|---|
| `python tools/sweep.py --backend grid --params-toml <file> --duration N --output <jsonl>` | Generic parameter sweep |

### Rendering

| Tool | Purpose |
|---|---|
| `blender -b -P tools/render_blender.py -- --snapshot <npz> --output <png> --quality {low,medium,high} --engine {cycles,eevee}` | Single-frame render |
| `python tools/render_animation.py --config <toml> --max-duration N --stop-at-level L --output <mp4>` | Sim + batch render + ffmpeg |

---

## Part 8 — How to commit and push findings

The git workflow that keeps this project debuggable.

### Single-amendment workflow

```bash
# Working in a clean tree
git status               # confirm clean
git pull                 # confirm up to date

# Make the spec amendment
$EDITOR docs/CONCEPT.md
git add docs/CONCEPT.md
git commit -m "spec(amendment): §X.Y <description>"

# Make the implementation
$EDITOR world/physics.py world/state.py world/config.py
$EDITOR tests/test_<rule>.py

# Verify
pytest

# Calibration smoke
python -c "..."  # 30s smoke

# Commit implementation
git add world/ tests/
git commit -m "feat(amendment): §X.Y <description> — implementation

[body referencing the spec commit]"

# Update LOGBOOK
$EDITOR LOGBOOK.md
git add LOGBOOK.md
git commit -m "docs(logbook): session <N> — <description>"

# Push
git push
```

### Calibration-only workflow (no substrate change)

```bash
# Run sweep
python /tmp/sweep_<topic>.py

# Promote winner (if any)
cp <winner-toml> renders/calibration_session<N>_<topic>.toml
git add renders/calibration_session<N>_<topic>.toml

# LOGBOOK
$EDITOR LOGBOOK.md
git add LOGBOOK.md

# Single commit
git commit -m "docs(calibration): session <N> — <topic>

Best config: <label>
Result: <metric>"

git push
```

### Things to never commit

- `.venv/` (in `.gitignore` already)
- `*.npz` snapshot files (in `.gitignore` already, except small reference ones)
- Massive snapshot directories (`renders/<topic>-work/snapshots/`)
- Word lock files (`~$*.docx`) — already in `.gitignore`

### Things to always commit

- LOGBOOK updates
- Calibration TOMLs
- Spec amendments
- Code changes + tests
- Animations and keyframes (under `renders/`)

### Branching

For substantive substrate amendments, use a feature branch:

```bash
git checkout -b feat/phase5-amendments-r1-r4
# work
git push -u origin feat/phase5-amendments-r1-r4
```

Open a PR if you want code review before merging to `main`. For simple calibration work, commit straight to `main`.

---

## Part 9 — Open questions and where to focus

If you're picking up this project and don't know where to start, here is the priority order. Each item lists the minimum work required to close or advance it.

### Highest priority: Phase 5 R1–R4

Substrate amendment for ambient injection, level-5+ decay, local capture, and activity detection. **This is the §6.5 question** — whether emergent Hebbian plasticity is achievable in the current substrate.

**Minimum work:** ~1 week for a single researcher.
**Output:** spec amendments in CONCEPT.md, code in `world/physics.py`, tests, LOGBOOK entry showing whether Hebbian signal is positive on co-activity.

### Second priority: Phase 4 charge + threshold + refractory rules

Substrate amendment for neuron firing.

**Minimum work:** ~3-5 days. The rules are well-spec'd in `docs/research_session4/phase4_findings.md`.
**Output:** can be done in parallel with Phase 5 if you have two sessions.

### Third priority: Phase 3 — molecule-molecule binding

A small substrate amendment (`(5,5)` etc. in `_UPGRADE_TARGET`) that may or may not enable spontaneous shells. Lower priority because the empirical answer might be "still doesn't form shells without higher density."

**Minimum work:** ~1-2 days.

### Background priorities: Phase 1 / Phase 2 reproducibility

Fold the seed-verification work in as a defensive check whenever a substrate amendment lands. Make sure atoms still form across at least seeds 42, 7, 100, 314, 999.

### Engineering priorities: code-review still-open items

C1, C4, C5, I3, I4, I6 from `docs/research_session4/code_review.md`. Tackle when you want lower-cognitive-load work between research sessions.

---

## Part 10 — Common pitfalls

These are things that cost me hours during sessions 1-4. Don't repeat them.

### Numba cache staleness

If you edit a `@njit` function and the test still passes (or fails differently from what you expected), delete the cache:

```bash
rm -rf world/__pycache__/ tools/__pycache__/
```

Numba caches compiled JIT functions to `__pycache__`. Editing the function doesn't always invalidate the cache.

### TOML overrides leak across sessions

The `renders/calibration_session3.toml` originally had `speed_min=5.0, speed_max=25.0` from an earlier animation config. Calibration sweeps used WorldConfig defaults (10/50). The TOML thus didn't reproduce the calibration sweep's atom-formation time. Lesson: every TOML override is suspect; verify the loaded config matches what you expected:

```bash
python -c "from world.config import load_config; from pathlib import Path; print(load_config(Path('renders/<file>.toml')))"
```

### Capacity exhaustion in tests

`World(WorldConfig(n_nodes_max=64))` looks generous until you try to construct a synapse (28+ nodes). Test fixtures should set capacity to ≥3× the constructed node count.

### Multiprocessing seed identity

`multiprocessing.Pool` workers don't share RNG state. If you seed your sweep but sub-runs don't get distinct seeds, two configs with otherwise-identical params produce identical results. Each worker must call `np.random.default_rng(seed)` from the workerwith a deterministic-but-distinct seed.

### Print buffering

`print(...)` from a worker process or from a long-running script is buffered until process exit on Linux/macOS. Use `print(..., flush=True)` when you need progress output.

### Snapshot directory bloat

A 60s simulated run with `--snapshot-every 0.1` produces 600 snapshots × ~200 KB each = ~120 MB. Don't commit these. Clean up:

```bash
find renders/ -name "snapshot_t*.npz" -delete
```

### Pytest test isolation

A test that calls `np.random.default_rng()` without a seed and one that does, run in the same pytest invocation, can interfere if global RNG state matters. Use seeded RNGs everywhere and prefer `np.random.default_rng(seed)` over the legacy global `np.random.seed`.

### CONCEPT.md amendments without spec acceptance criteria

It's tempting to just add a §4.x with the new rule and move on. But without an acceptance criterion ("the rule unlocks X observable"), you have no way to verify the amendment landed correctly. Always include the criterion.

### Confirmation bias in calibration

If you sweep `r_2 ∈ [10, 20, 30]` and the leader is `30` with 4 atoms vs `10` with 1 atom, the conclusion isn't "r_2 = 30 is right". It's "more r_2 helps, the optimum may be higher than 30, and we should test 50 and 100 next." Always extend the sweep beyond your initial range until the metric stops improving.

### Skipping the LOGBOOK

The LOGBOOK is the only thing that lets future-you reconstruct what session-N was thinking. Don't skip it. Even a one-paragraph entry beats nothing.

---

## Part 11 — When to call in teammate agents

You can dispatch subagents for parallel research the way I did in session 4. Useful patterns:

### Pattern A — Independent code review

When you've made non-trivial changes (substrate amendment + new tests + new tool), dispatch a `superpowers:code-reviewer` agent over the diff. They'll catch confirmation bias and silent bugs you confirmation-biased past. Worth it for any commit that adds ≥100 lines.

### Pattern B — Parallel calibration sweeps

When you have multiple acceptance criteria to chase and they don't share state, dispatch one `general-purpose` agent per criterion with explicit time budget and findings file path. Each runs ~60-90 minutes. Integrate findings centrally.

This works because:
- Calibration runs are CPU-bound and parallelisable
- Each agent is session-bounded (so no multi-day commitment)
- The merge step (you, integrating findings) is light

### Pattern C — Adversarial re-derivation

When you're not sure if a spec claim is well-founded, dispatch a `Plan` agent with just the spec text and ask it to re-derive the claim. They'll find weaknesses your model has confirmation-biased past.

### Pattern D — Background long-running render

When you want a high-quality animation, dispatch a separate agent (or run as a Bash background) for the Cycles render. It's CPU-heavy and shouldn't block your interactive work.

### Anti-patterns for teammates

- **Don't dispatch teammates for empirical research that needs human judgment.** A "computational neuroscientist persona" agent is theatrical; their analysis is plausible-sounding but not peer-review-grade.
- **Don't have multiple agents commit to the same branch.** Race conditions. Have them write findings to `/tmp/findings_<topic>.md`; you integrate centrally.
- **Don't overload.** With 4 agents running 4 calibration sweeps + 1 reviewer + a long render, CPU contention slows everyone down. Cap at 4-5 concurrent CPU-heavy agents.

### How to dispatch

In a Claude Code session:

```
Agent({
  description: "Phase X calibration: chase Y",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "You are running calibration experiments... [full prompt with working dir, time budget, findings file path]"
})
```

For independent code review:

```
Agent({
  subagent_type: "superpowers:code-reviewer",
  prompt: "Review the diff between SHA <a> and SHA <b>... [scope, what to assess, where to write findings]"
})
```

See `docs/research_session4/` for examples of what teammate output looks like and how to integrate it.

---

## Appendix A — File structure reference

```
EQMOD/
├── docs/
│   ├── CONCEPT.md                # The conceptual case (v2 with peer-review amendments)
│   ├── CALIBRATION_GUIDE.md      # Practical calibration recipe
│   ├── RESEARCH_GUIDE.md         # This document
│   ├── TUTORIAL.md               # Walkthrough from clone to first calibrated run
│   ├── Konzeptpapier.de.md       # German original of the concept paper
│   ├── Konzeptpapier.docx        # Original Word doc
│   ├── logbook/                  # Screenshots from research sessions
│   ├── research_session4/        # Five teammate-agent reports
│   │   ├── code_review.md
│   │   ├── phase2_findings.md
│   │   ├── phase3_findings.md
│   │   ├── phase4_findings.md
│   │   └── phase5_findings.md
│   └── superpowers/
│       ├── specs/                # Per-phase design specs
│       └── plans/                # Per-phase implementation plans
├── files/
│   ├── README.md                 # Source onboarding (English)
│   ├── README.de.md              # German original
│   ├── SPECIFICATION.md          # The substrate's natural laws (English)
│   ├── SPEZIFIKATION.de.md       # German original
│   ├── SKILL.md                  # The eight-phase plan (English)
│   └── SKILL.de.md               # German original
├── world/                        # The substrate
│   ├── config.py                 # WorldConfig dataclass + TOML loader
│   ├── state.py                  # World class — SoA NumPy arrays
│   ├── spatial.py                # 3D periodic-wrap grid
│   ├── physics.py                # @njit hot loops + tick()
│   ├── snapshot.py               # NPZ save/load
│   ├── preview.py                # PyVista live preview
│   ├── render.py                 # (deleted; PyVista replaces Pygame)
│   └── run.py                    # CLI: python -m world run
├── tools/                        # The analysis layer (no @njit; pure Python + NumPy)
│   ├── classify_molecules.py     # Phase 2: species fingerprinting
│   ├── detect_membranes.py       # Phase 3: closed-shell detection
│   ├── construct_membrane.py     # Phase 3: hand-place Fibonacci shell
│   ├── construct_neuron.py       # Phase 4: hand-place neuron cluster
│   ├── detect_neurons.py         # Phase 4: compact-cluster detection
│   ├── measure_neuron_activity.py # Phase 4: firing/integration/refractory
│   ├── construct_synapse.py      # Phase 5: hand-place synapse
│   ├── detect_synapses.py        # Phase 5: neuron-pair detection
│   ├── measure_synapse_plasticity.py # Phase 5: Hebbian signal
│   ├── construct_network.py      # Phase 6: hand-place network
│   ├── detect_networks.py        # Phase 6: connected-component networks
│   ├── measure_network_activity.py # Phase 6: firing matrix + correlation + pattern score
│   ├── synthesize_carrier_firing.py # Phase 7: synthetic firing data
│   ├── measure_attention_selectivity.py # Phase 7: resonance + selectivity
│   ├── histogram.py              # Snapshot frequency-decade histograms
│   ├── sweep.py                  # Generic parameter sweep harness
│   ├── render_blender.py         # Headless Blender Cycles renderer
│   └── render_animation.py       # Sim + batch render + ffmpeg
├── tests/                        # 148 tests across all of the above
├── renders/                      # Calibration TOMLs + animations + keyframes
│   ├── calibration_session3.toml             # First atom-producing config
│   ├── calibration_session3b_molecules.toml  # First molecule-producing config (2 species)
│   ├── calibration_phase2_acceptance.toml    # ≥5 species (current Phase 2 result)
│   ├── animation_config.toml                  # Older animation buildup config
│   ├── anim_phase1_first_atom.mp4             # Eevee animation
│   ├── anim_phase1_first_atom_hq.mp4          # Cycles HQ
│   ├── anim_phase2_first_molecule.mp4         # Phase 2 buildup → first molecule
│   ├── anim_first_emergence.mp4               # Earlier wave-only buildup
│   ├── keyframe_first_atom.png
│   ├── keyframe_first_molecule.png
│   └── v2-acceptance.png
├── pyproject.toml                # Build config + deps
├── .gitignore
├── README.md                     # Public face on GitHub
└── LOGBOOK.md                    # Research diary
```

---

## Appendix B — Standard commit message format

```
<type>(<scope>): <short summary>

<body — what changed and why>

<footer — Co-Authored-By if applicable, or links to spec commits>
```

`<type>`: one of `feat`, `fix`, `spec`, `docs`, `test`, `chore`, `refactor`.
`<scope>`: a short tag like `phase4`, `physics`, `calibration`, `logbook`.

Examples:

```
spec(amendment): §4.8 ambient injection mechanism
feat(physics): inject_at_region — implementation of §4.8
fix(measure_synapse): C6 — slope collection bug
docs(logbook): session 5 — Phase 5 R1 implementation
chore(calibration): promote session-5 R1 TOML
```

---

## Appendix C — When to write a session paused note

Stop and write a `LOGBOOK.md` "session paused" entry when:

- You're at a stopping point and need to come back later
- You're blocked and need help / external input
- You've run a long-running experiment and need to wait for it to finish
- You've made non-trivial uncommitted changes and the session is about to end

Format:

```markdown
## 2026-MM-DD — Session paused

**At:** Step N of workflow on Phase X amendment R1.

**Last commit:** <SHA>.

**Working tree state:** clean / has uncommitted changes in <files>.

**What's running:** <process description, output paths>.

**What's next when I resume:** <concrete first action>.
```

---

## End of guide

If something in this document is wrong or out of date, fix it. The guide is the documentation contract; staleness here costs hours.
