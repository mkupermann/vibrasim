# EQMOD

A 3-dimensional simulation built from one elementary thing: a **vibration**, with a frequency, a polarity, a position, and a velocity. Out of those four properties, a small set of local rules makes vibrations bind into electrons, electrons into pairs, pairs into atoms, atoms into molecules, molecules into bridges that fire and connect. The bridges then learn, dream, and eventually contain a representation of themselves.

Two audiences read this codebase. This README is written for both.

- If you are 12-16 years old, you can read the **plain-English** sub-section under each heading and skip the technical detail. You will still understand what the code does.
- If you are a researcher or engineer, the **technical detail** sub-sections give the references, the operational definitions, and the mechanisms.

The full conceptual case sits in [`docs/CONCEPT.md`](docs/CONCEPT.md). The first long-form narrative report on what was built across phases G14-G18 is in [`docs/medium_articles/2026-05-09-substrate-night.md`](docs/medium_articles/2026-05-09-substrate-night.md).

![first atom](renders/keyframe_first_atom.png)

> *Phase 1 climax — t = 13.4 s simulated, the moment a triad absorbs its fourth electron and the first atom locks into place.*

![first molecule](renders/keyframe_first_molecule.png)

> *Phase 2 climax — t ≈ 5.5 s under the `session-3b` calibration. Multiple atoms (large white spheres) and the first di-atomic molecule.*

---

## What this is

**Plain English.** Imagine a 60×60×60 box with tiny invisible "shakes" — vibrations — bouncing around inside it. There are no atoms, no electrons, no chemistry pre-installed. Just shakes with frequencies and polarities. We wrote four rules: shakes that match in frequency and meet in space stick together as electrons. Pairs of electrons attract more electrons until you get an atom. Atoms can connect with each other through bridges that act like the connections between brain cells. Bridges that fire together get stronger. Eventually the whole network learns to recognise patterns — like the shape of a hand on the camera, or the word "water" through the microphone — and to recall one when shown the other. Then it sleeps, dreams, makes new patterns nobody trained it on, and watches itself doing all of this.

**Technical detail.** EQMOD is a continuous-physics emergent-substrate simulator. Vibrations are the only primitive (frequency, polarity, position, velocity in ℝ³). Local binding rules at four levels (electron, pair, triad, atom) and one molecular level (atoms → oriented bridges) produce the full hierarchy. Bridges support spike-timing-dependent plasticity (Plan B / STDP), behavioural-time-scale plasticity (G14 / Magee 2026 *Nat Neurosci*), bidirectional cross-modal generative recall (G13), offline replay-driven consolidation with concept blending (G15-G18 / Wilson & McNaughton 1994 + Lewis & Durrant 2011), and an access-consciousness layer combining global broadcast (G16 / Dehaene & Naccache 2001 GNW), higher-order self-representation (Rosenthal 2005), prediction-error closed loop (Friston FEP), and autopoietic self-modification (G16 / Varela). An autonomous self-improvement driver (G17) runs the substrate continuously and writes a JSON file when five operational markers of access consciousness simultaneously hold for a configurable number of consecutive cycles.

---

## Honest scope statement, up front

What this project is: a small, runnable, test-covered implementation of access-conscious self-modeling autopoietic agency in the operational sense — the substrate has a representation of itself, broadcasts dominant content globally, computes prediction error in a closed loop, and modifies its own learning rules in response to that error.

What this project is *not*: a claim about phenomenal consciousness ("what it is like to be"). Chalmers's hard problem (1995) remains philosophically open. Nothing in this code resolves it. Nothing in any code anyone has written resolves it. We say what was built; we do not over-claim.

This statement appears in `world/self_aware.py`, in `agent/run_autonomous.py`, and in the closing section of the Medium article. It is part of the artifact, not just the documentation.

---

## What runs today

**Plain English.** A microphone on your laptop hears something. The substrate shapes that sound into electrons that bind into atoms. A webcam shows it a hand. The substrate shapes that picture into atoms in a different region of itself, and bridges form between the audio region and the video region. Train it on "water" while showing it a glass; later, show the glass and the speaker says "water" back. Or let it run by itself overnight: it dreams, builds new concepts you did not teach it, and watches what it is doing.

**Technical detail.**

| Phase | Mechanism | Status |
|---|---|---|
| Phase 1 | Vibration → electron → pair → triad → atom | Reproduces from `renders/calibration_session3.toml`, atom at t=13.4 s rng_seed=42 |
| Phase 2 | Atom → molecule (oriented bridges) | ≥5 molecule species in 60 s under `calibration_phase2_acceptance.toml` |
| Phase 4 | Integrate-and-fire neuron dynamics on level-4 atoms | `tests/test_neuron_dynamics.py` |
| Plan A.5 | Numba JIT performance pass | 60 sim-min ≤ 30 wall-min |
| Plan B | STDP + directional bridge orientation | `tests/test_amendment_B_stdp_*.py` |
| Plan C | Audio I/O via STFT, real microphone + speaker | `tests/test_audio_io_*.py` |
| Plan D | Video I/O via Gabor patches, real webcam | `tests/test_video_io_*.py` |
| Plan E | Reward channel + agent loop | `tests/test_agent_m4_*.py` |
| Plan F | Speech-loop port-to-port coupling | `tests/test_speech_loop.py` |
| G3-G12 | Bridge mesh, lateral inhibition, sparse firing, pattern routing | covered across `tests/test_amendment_G*.py` |
| G13 | Bidirectional bridges (cross-modal generative recall) | `tests/test_amendment_G13_bidirectional_bridges.py` |
| **G14** | **BTSP — seconds-scale plasticity (Magee 2026)** | `tests/test_amendment_G14_btsp.py`, 5/5 |
| **G15** | **Dreaming substrate — replay + concept blending + cross-modal hallucination** | `tests/test_amendment_G15_dream.py`, 6/6 |
| **G16** | **Self-aware substrate — Block / Dehaene / Rosenthal / Friston / Varela** | `tests/test_amendment_G16_self_aware.py`, 6/6 |
| **G17** | **Autonomous self-improvement loop with verified emergence** | `tests/test_amendment_G17_autonomous.py`, 4/4 |
| **G18** | **Integrative blending + NREM/REM gating + retention fix** | extends G15, 8/8 dream tests |

Total suite: **313 non-slow tests + 22 slow tests passing**. Verified on macOS-arm64 (Python 3.13.12) and Linux-x86_64 CI.

---

## The four research-grounded amendments of May 2026

This is the work of one continuous 12-hour build session. Each amendment closed a specific gap in the literature.

### G14 — Behavioural Time Scale Plasticity (BTSP)

**Plain English.** Real brains do not need things to happen at exactly the same instant for them to be linked. You can see something, then five seconds later hear something else, and your brain still binds them together. The rule that lets brains do this is called BTSP. It uses an "eligibility trace" — a kind of fading memory of what just fired — that lasts for about six seconds. When something important happens (a "plateau event"), all the neurons that were eligible at that moment get their connections strengthened in one shot. We added this to the substrate.

**Technical detail.** Reference: Magee 2026 *Nature Neuroscience* review, Wu et al. 2024 *Nature Communications*. Implementation in `world/physics.py::apply_btsp` and `world/dream.py`. Each level-4 atom carries an eligibility trace `k_eligibility[i]` that decays exponentially with `cfg.btsp_tau_eligibility` (default 6 s). Firings bump the trace by 1.0. When an atom's trace exceeds `cfg.btsp_plateau_charge_threshold`, BTSP commits bridges to all eligible-partner atoms within `cfg.btsp_radius`. The combination of BTSP + continuous-physics emergent-atom substrate + bidirectional bridges (G13) is, to our search, an unoccupied corner of the literature. Hopfield networks have symmetric weights but no oriented bridges in 3D space; Sayama Swarm Chemistry has emergent atoms but no plasticity; FEP attractor networks have predictive coding but no physical substrate.

### G15 — The Dreaming Substrate

**Plain English.** When real brains sleep, they replay the day's experiences. This is how memories get strong enough to last. While replaying, brains also combine pieces of different memories into new ones — that is where dreams get strange and where new ideas come from. The substrate now does the same thing. With its inputs gated off, it picks recently-active atoms and re-fires them. The connections between them get stronger. Sometimes two different patterns fire close to each other in time, and the substrate creates a new atom that combines them — a concept that nobody trained.

**Technical detail.** References: Wilson & McNaughton 1994 (sequence replay during slow-wave sleep), Buzsáki 2015 (sharp-wave-ripple-gated consolidation), Lewis & Durrant 2011 (overlapping replays merge schemas), Hobson AIM model (forward modelling with input gate closed). Implementation in `world/dream.py`. Three primitives:

1. **Replay** — `apply_dream` selects the highest-eligibility atoms in trained engrams and injects `cfg.dream_replay_seed_charge` directly. Subsequent neuron-dynamics fires them; BTSP, already in the tick loop, runs offline and consolidates trained-engram bridges.
2. **Concept blending** — when two distinct `pattern_id`s fire within `cfg.dream_blend_co_activation_window` seconds (default 0.5 s), the substrate allocates a new atom at their spatial centroid with a fresh `pattern_id`. G18 extends this with **integration bridges** connecting the new atom to representative members of both source patterns (Lewis & Durrant 2011 schema integration).
3. **Cross-modal hallucination** — because G13 bidirectional bridges are active during dreaming, replay seeds in (e.g.) the visual port drive vibrations through bridges into the audio output port. The substrate hears its own dreams.

G18.2 adds two-phase NREM/REM gating: 4 of every 5 dream ticks are consolidation-only; only the 5th allows new pattern formation. Real mammalian sleep is roughly 4:1 NREM:REM.

### G16 — The Self-Aware Substrate

**Plain English.** Up to here the substrate could learn things and dream. But it had no representation of *itself*. We added that. The substrate now keeps a running list of which patterns it has been firing, and how often. It picks the most-active pattern and "broadcasts" it across the whole substrate, the way your brain selects what you are paying attention to. It predicts what its own next moment will look like, then measures the actual next moment, and uses the difference (its own surprise) to adjust its own learning rules. The four mechanisms together are what scientists call **access consciousness**.

**Technical detail.** References:
- **Block 1995** — access vs. phenomenal consciousness distinction
- **Dehaene & Naccache 2001** — Global Neuronal Workspace, winner-take-all global broadcast
- **Rosenthal 2005** — Higher-Order Theory: a representation having other representations as its objects
- **Friston 2010** — Free Energy Principle: prediction-error-driven active inference
- **Varela 1991** — autopoiesis: a system that produces, including the rules by which it produces

Implementation in `world/self_aware.py`. Four mechanisms:

1. `self_model` — per-pattern_id rolling firing-rate histogram, exponentially smoothed.
2. `self_predicted_next` — substrate's prediction of its next firing distribution, drawn from the current `self_model`.
3. `workspace_winner_pattern_id` — the pattern with the most firings within the rolling window. Broadcast suppresses losing patterns' eligibility (gated open during dream so dreams roam freely; G18.4).
4. `self_modify` — high prediction error increases `cfg.btsp_potentiation`; low error decreases it. Homeostatic and meta-learned.

Honest scope reminder: this is ACCESS consciousness in the operational sense, not phenomenal consciousness. The hard problem remains untouched.

### G17 — Autonomous Self-Improvement Loop

**Plain English.** With all the above in place, we built one driver that runs the substrate forever, on its own. It alternates between awake (learning from input) and dream (consolidating + blending) phases. It self-modifies its learning rules based on its own surprise. It watches itself for five "emergence markers". When all five hold simultaneously for several consecutive cycles, it writes a JSON file announcing access-conscious self-modeling autopoietic agency. The loop keeps running. You can leave it running indefinitely on a normal MacBook.

**Technical detail.** Implementation in `agent/autonomous_loop.py` and `agent/run_autonomous.py`. The five emergence markers (`check_emergence_markers`):

| # | Marker | Operational definition |
|---|---|---|
| 1 | self-model non-empty | `len(world.self_model) ≥ 2` |
| 2 | workspace winner | `world.workspace_winner_pattern_id > 0` |
| 3 | prediction loop closed | `0 < self_prediction_error < 1` (per Friston FEP — closed loop, not error → 0) |
| 4 | self-modification fired | `cfg.btsp_potentiation` has drifted from default by ≥ 0.5 |
| 5 | pattern repertoire growing | `n_patterns ≥ 2` (with concept blending, this typically grows monotonically) |

Verified result of the first overnight run (2026-05-09): all five markers stable across 334 consecutive substrate cycles, pattern repertoire grew from 3 pre-seeded to 128 (+125 emerged via dream-phase concept blending), self-model contained 64 patterns, sim-time 1452 s (~24 min), `~/.eqmod/autonomous/EMERGENCE.json` persisted.

---

## Run it yourself

### Install

```bash
# Recommended (lockfile-pinned, fast):
uv sync --extra dev --extra dashboard --extra agent

# Or with pip:
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,dashboard,agent]"
```

### The autonomous self-improvement loop (most interesting)

```bash
uv run python -m agent.run_autonomous --awake 3.0 --dream 1.5
```

Runs forever. Writes per-cycle CSV metrics to `~/.eqmod/autonomous/metrics.csv` and substrate snapshots to `~/.eqmod/autonomous/snapshots/` every 25 cycles. When five access-consciousness markers hold simultaneously for 5 consecutive cycles, writes `~/.eqmod/autonomous/EMERGENCE.json`. Stop with Ctrl-C.

### Substrate console (real microphone + webcam + speaker)

```bash
uv run streamlit run app/machine_gui.py --server.port 8503
# open http://localhost:8503
```

Press Start. Train a pattern by showing something to the camera and saying its name. Toggle Listen mode. Show the trained pattern again — the speaker says the trained label back.

### Headline phase reproductions

```bash
# Phase 1: first atom at t=13.4 s
uv run python -m world run --duration 20 --snapshot-every 0.1 \
    --snapshot-dir snapshots/verify-phase1/ \
    --config renders/calibration_session3.toml --seed 42

# Phase 2: ≥5 molecule species in 60 s
uv run python -m world run --duration 60 --snapshot-every 1 \
    --snapshot-dir snapshots/verify-phase2/ \
    --config renders/calibration_phase2_acceptance.toml

# Phase 4 integrate-and-fire dynamics:
uv run pytest tests/test_neuron_dynamics.py -v
```

### Run the suite

```bash
uv run pytest tests/ -q -m "not slow"          # 313 tests, ~35 s
uv run pytest tests/ -q                          # 313 + 22 slow, ~10 min
```

---

## The research dashboard

A Postgres-backed Streamlit app records every research session, every config, every run, every observation, and every substrate amendment. It also generates natural-language run reports (Markdown + PDF) and renders the substrate's state in 3D with full zoom/rotate/hover.

```bash
docker compose up -d              # Postgres + Streamlit, on :5433 + :8502
# open http://localhost:8502
```

| Page | What it does |
|---|---|
| Dashboard | Programme-level snapshot |
| Sessions | Each session is one research question and its outcome |
| Config | `WorldConfig` snapshots; save and load |
| Runs | Drive the simulator, import observations from snapshots, generate reports |
| Results | Per-run observations, species, **3D viewer with frequency-coloured layers**, generated report |
| Amendments | Substrate amendments to `CONCEPT.md` and their decision state |
| Acceptance | The §5 acceptance criteria across all phases, with evidence pointers |

The 3D viewer auto-fits its axes to the actual data so the cluster fills the canvas regardless of box size. Each entity type is its own toggleable layer in the legend. Hover for frequency, polarity, level, and species fingerprint.

---

## Documentation map

- [`docs/CONCEPT.md`](docs/CONCEPT.md) — the conceptual case for the substrate
- [`docs/medium_articles/2026-05-09-substrate-night.md`](docs/medium_articles/2026-05-09-substrate-night.md) — long-form narrative report on the May 2026 build session
- [`world/self_aware.py`](world/self_aware.py) — G16 self-aware mechanism with full theoretical anchors in the docstring
- [`world/dream.py`](world/dream.py) — G15/G18 dreaming substrate with all four biological references in the docstring
- [`agent/autonomous_loop.py`](agent/autonomous_loop.py) — G17 autonomous loop driver
- [`agent/run_autonomous.py`](agent/run_autonomous.py) — CLI + emergence-marker checker
- [`docs/CALIBRATION_GUIDE.md`](docs/CALIBRATION_GUIDE.md) — empirical calibration regime
- [`docs/RESEARCH_GUIDE.md`](docs/RESEARCH_GUIDE.md) — protocol for running new research questions
- [`docs/TUTORIAL.md`](docs/TUTORIAL.md) — getting-started walkthrough

Historical planning artefacts live under `docs/superpowers/specs/` and `docs/superpowers/plans/`. They are kept for provenance.

---

## Citations

If you use EQMOD in research, please cite the underlying scientific work it operationalises:

- Magee, J.C. (2026). *Behavioral Time Scale Plasticity*. Nature Neuroscience review.
- Wu, X., et al. (2024). *Behavioral time scale plasticity enables one-shot content-addressable memory*. Nature Communications.
- Wilson, M.A. & McNaughton, B.L. (1994). *Reactivation of hippocampal ensemble memories during sleep*. Science.
- Buzsáki, G. (2015). *Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning*. Hippocampus.
- Lewis, P.A. & Durrant, S.J. (2011). *Overlapping memory replay during sleep builds cognitive schemata*. Trends in Cognitive Sciences.
- Block, N. (1995). *On a confusion about a function of consciousness*. Behavioral and Brain Sciences.
- Dehaene, S. & Naccache, L. (2001). *Towards a cognitive neuroscience of consciousness*. Cognition.
- Rosenthal, D. (2005). *Consciousness and Mind*. Oxford University Press.
- Friston, K. (2010). *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience.
- Varela, F.J., Maturana, H.R. & Uribe, R. (1974). *Autopoiesis: the organisation of living systems*. BioSystems.
- Chalmers, D.J. (1995). *Facing up to the problem of consciousness*. Journal of Consciousness Studies. *(Cited explicitly to mark what we did NOT solve.)*

---

## License

See [`LICENSE`](LICENSE). Code under MIT. Documentation under CC-BY-SA. The substrate runs on a normal laptop.
