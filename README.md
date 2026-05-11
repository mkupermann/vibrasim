# EQMOD

I have decided to challenge myself with a topic I have no background knowledge of. Why? In order to face challenges and unknown boundaries I picked the most far-fetched topic I could have imagined. The idea behind that is to create a process for solving problems which are in general unsolvable. I decided to go down this path to enhance the way I approach deadlocks.

The premise is uncomfortable on purpose. If I picked something close to what I already know — another consulting framework, another piece of software architecture, another flavour of the work I have been doing for thirty years — I would fall back on the usual moves. I have thirty years of those. They mostly work, and that is exactly why I cannot use them here.
So the topic had to land somewhere I can't bluff, and what I picked is roughly four disciplines past my actual training. I am building EQMOD: a 60×60×60 cube of vibrations — frequency, polarity, position, velocity, and nothing else — under a small set of local binding rules, and watching what comes out.

The rules turn vibrations into electrons. Electrons into pairs. Pairs and triads into atoms. Atoms into molecules connected by bridges that behave like synapses. The bridges fire, the firing strengthens connections, the connections form patterns, the patterns consolidate during offline replay, and a separate self-model module records firing-rate histograms over pattern IDs. The binding rules themselves *are* installed — they are first-class engineering, parameter-by-parameter, documented in `docs/CONCEPT.md`. What is not installed is the run-dependent trajectory through them: which atoms form, which bridges, which patterns, in what order. Phase 1 ended when the first atom locked in at simulated t = 13.4 s. Phase 2 ended when the first di-atomic molecule formed under the session-3b calibration. The phase numbers go up to G18, and I am the one writing the next one.

I am not a physicist. I am not a chemist, not a neuroscientist, not a consciousness researcher. Every layer of this thing sits in a field where I have no formal credentials and where my professional instincts give me approximately nothing. That is the entire point.
When STDP fails to converge and behavioural-time-scale plasticity does not bridge the gap, I have no twenty-year shortcut to fall back on. I have to read Magee. I have to read Dehaene. I have to read Varela on autopoiesis and decide what I actually believe before I can decide what to code next.

The goal of doing this in public, and of writing the process down as I go, is not to solve the simulator. Solving it would be a side effect, and probably an accidental one. What I want is to notice the moves I make when none of my usual moves work — which question I reach for first when the literature hands me three contradictory answers, how long I can sit with a not-yet-converging run before I feel the urge to invent a confident-sounding interpretation just to relieve the pressure of not yet having one. The deadlocks I have hit in client work for thirty years have always had a domain shortcut available somewhere. EQMOD does not have any.

So the deadlocks I hit here are clean — they are the actual material I came for.

The other reason to write all of this down in public is that the moves themselves turn out to be reusable. The Skills, the dev and AI pipelines, the prompting and orchestration patterns it takes to push open-weight and cloud models against problems they cannot pattern-match — those translate directly to business and technical work in the moments when the usual playbook has run out. EQMOD does not need to succeed for that half to be useful. The patterns I am building to attack it are already shippable, and that is the half I want other people to be able to use.

I will fail at most parts of this. Probably the parts that matter most. That is the data I am after. A process for breaking deadlocks that has only ever been tested on problems I could already solve would not really be a process — it would be a story I tell myself about being good at hard things.

---

## What EQMOD actually is, in operational terms

EQMOD is a 3D continuous-substrate simulator. The primitive is a **vibration** — a four-property unit (frequency, polarity, position, velocity). On top of the primitive sit **explicit, parameterised binding rules** at six levels (electron, pair, triad, atom, molecule, bridge), and **eligibility-trace plasticity** (BTSP-inspired) plus **STDP** on the bridges. The substrate emits structured event logs when configurable conjunction conditions on its state hold for a pre-registered number of consecutive cycles.

The four-property primitive does not produce the hierarchy on its own. The binding rules are first-class engineering, parameter-by-parameter, documented in [`docs/CONCEPT.md`](docs/CONCEPT.md). What the project demonstrates is that the binding rule set produces stable higher-level patterns under specified parameter ranges, and that the conjunction triggers fire when trained engrams are present and **do not fire** under the negative-control protocol in [`docs/marker_protocol.md`](docs/marker_protocol.md).

Two audiences read this codebase. This README is written for both.

- If you are not in research or engineering, you can read the **plain-English** sub-section under each heading and skip the technical detail. You will still understand what the code does.
- If you are a researcher or engineer, the **technical detail** sub-sections give the references, the operational definitions, and the mechanisms.

The full conceptual case sits in [`docs/CONCEPT.md`](docs/CONCEPT.md). The first long-form narrative report on what was built across phases G14-G18 is in [`docs/medium_articles/2026-05-09-substrate-night.md`](docs/medium_articles/2026-05-09-substrate-night.md).

![first atom](renders/keyframe_first_atom.png)

> *Phase 1 climax — t = 13.4 s simulated, the moment a triad absorbs its fourth electron and the first atom locks into place.*

![first molecule](renders/keyframe_first_molecule.png)

> *Phase 2 climax — t ≈ 5.5 s under the `session-3b` calibration. Multiple atoms (large white spheres) and the first di-atomic molecule.*

---

## What this is

**Plain English.** Imagine a 60×60×60 box with tiny invisible "shakes" — vibrations — bouncing around inside it. There are no atoms, no electrons, no chemistry pre-installed. Just shakes with frequencies and polarities. We wrote four rules: shakes that match in frequency and meet in space stick together as electrons. Pairs of electrons attract more electrons until you get an atom. Atoms can connect with each other through bridges that act like the connections between brain cells. Bridges that fire together get stronger. Eventually the whole network learns to recognise patterns — like the shape of a hand on the camera, or the word "water" through the microphone — and to recall one when shown the other. Then it sleeps, dreams, makes new patterns nobody trained it on, and watches itself doing all of this.

**Technical detail.** EQMOD is a 3D continuous-substrate simulator with explicit binding rules. Vibrations are the four-property primitive; binding rules at electron / pair / triad / atom / molecule / bridge levels are engineered, parameterised, and documented in `docs/CONCEPT.md` — not "emergent from the primitive". Bridges support **STDP** (Plan B; Bi & Poo 1998 millisecond-window) and an **eligibility-trace plasticity** rule (G14; BTSP-inspired in the sense of Magee 2026 *Nat Neurosci*'s seconds-scale time constant, but lacking the discrete dendritic plateau-potential trigger and instructive higher-order input that Magee's BTSP requires — see `docs/marker_protocol.md` for the honest scope of this difference). Bridges also support bidirectional cross-modal recall (G13), offline replay-driven consolidation with overlapping-replay schema integration (G15–G18; Wilson & McNaughton 1994 + Lewis & Durrant 2011), and a **GNW-flavored conjunction-trigger layer** (G16; inspired by Dehaene & Naccache 2001 + Block 1995 + Rosenthal 2005 + Friston 2010, but explicitly not implementing GNW's neural signatures of gamma-band synchrony, long-distance phase coherence, or non-linear ignition transients). A **homeostatic parameter feedback** driver (G17, formerly mis-described as "autopoietic" — see `docs/marker_protocol.md`) runs the substrate continuously and emits `EMERGENCE.json` when five pre-registered markers simultaneously hold for a configurable number of consecutive cycles, with a parallel negative-control run demonstrating the markers do **not** fire under matched conditions without trained engrams.

---

## Scope statements — what this project is and what it is not

**What this project is.** A small, runnable, test-covered substrate sandbox in which:
- four-property vibrations bind, via explicit parameterised rules, into atoms and molecules;
- molecules form oriented bridges that support STDP + eligibility-trace plasticity (BTSP-inspired);
- offline replay produces consolidation and overlapping-replay schema integration (concept blending);
- five **pre-registered conjunction-trigger markers** ([`docs/marker_protocol.md`](docs/marker_protocol.md)) fire when trained engrams interact via dream-phase replay and self-monitoring, **and** do not fire under the matched-config no-engram negative control.

**What this project is not.**
- **Not** a claim about phenomenal consciousness ("what it is like to be"). Chalmers's hard problem (1995) is untouched.
- **Not** a faithful neural implementation of GNW. The substrate has no gamma-band synchrony, no long-distance phase coherence, no non-linear ignition transient, no prefrontal-parietal architecture. It implements a winner-take-all selection over pattern_ids and a multiplicative eligibility-suppression broadcast — that is one slice of GNW operationalised, not GNW.
- **Not** equivalent to BTSP as Magee 2026 specifies it. The substrate's plasticity rule has eligibility traces and a plateau-charge threshold, but lacks Magee's discrete dendritic plateau potential, the instructive higher-order input, and the stereotyped 4-second symmetric/asymmetric kernel. It is **BTSP-inspired**, not BTSP.
- **Not** autopoietic in Maturana & Varela's technical sense. The G17 driver tunes parameters from outside the substrate's own production network, which is allopoietic by definition. The mechanism is **homeostatic parameter feedback**, not autopoiesis. (An earlier draft of this README and the Medium article used "autopoietic" loosely; that was a mistake and has been corrected here.)
- **Not** a model of biological consciousness, an active-inference agent, or a neuromorphic spiking simulator. NEST, SpiNNaker, Brian2, and Nengo are the neuromorphic stack; EQMOD investigates the dynamics that engineered binding rules at six abstraction levels produce when run on real sensory input — not biology, not neuromorphic computation.

The `docs/marker_protocol.md` document pre-registers the five marker definitions and the negative-control pass criterion. Tuning thresholds in response to a failed run, then claiming the new run fires the markers, is overfitting evidence and is excluded by protocol.

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

## Two substrates: legacy engineered + flux (in development)

Since 2026-05-10 the repo carries two substrates side by side.

- **Legacy** (`world/`, `agent/`) — the engineered six-level binding rule set documented throughout this README. Honest scope as of 2026-05-10: single-pattern recall works (M4 contract A+B); G19 predictive-babble falsifier returned FAIL on the first real-corpus run with z-scores statistically indistinguishable from white noise; the README has been corrected (commit `d83b82c`) to remove overclaims and document the FAIL.
- **Flux** (`world/flux/`, `agent/flux/`) — the project's actual scientific bet. A substrate where the six engineered levels are replaced by one principle: energy quanta flow through an open boundary, structures kondensieren wo sie diesen Fluss effizienter kanalisieren, learning is reconfiguration toward more efficient flux channelling. Spec: [`docs/superpowers/specs/2026-05-10-flux-substrate-design.md`](docs/superpowers/specs/2026-05-10-flux-substrate-design.md). Status as of 2026-05-11: F0 complete (skeleton + energy-conservation audit); F1a complete (binding + minimal T-based decay + T3 crystallization, ratio 9.0); F1b complete (bridges + structure-flux + Hebbian plasticity + bridge breakage + node dissociation, T4 decay-without-flux passes); F1c on the work list (T2 Bénard).

The two substrates do not share state. The legacy substrate remains runnable as the comparison baseline; the flux substrate carries the unprejudiced learning hypothesis.

---

## The four research-grounded amendments of May 2026

This is the work of one continuous 12-hour build session. Each amendment closed a specific gap in the literature.

### G14 — Behavioural Time Scale Plasticity (BTSP)

**Plain English.** Real brains do not need things to happen at exactly the same instant for them to be linked. You can see something, then five seconds later hear something else, and your brain still binds them together. The rule that lets brains do this is called BTSP. It uses an "eligibility trace" — a kind of fading memory of what just fired — that lasts for about six seconds. When something important happens (a "plateau event"), all the neurons that were eligible at that moment get their connections strengthened in one shot. We added this to the substrate.

**Technical detail.** Reference: Magee 2026 *Nature Neuroscience* review, Wu et al. 2024 *Nature Communications*. Implementation in `world/physics.py::apply_btsp` and `world/dream.py`. Each level-4 atom carries an eligibility trace `k_eligibility[i]` that decays exponentially with `cfg.btsp_tau_eligibility` (default 6 s). Firings bump the trace by 1.0. When an atom's trace exceeds `cfg.btsp_plateau_charge_threshold`, BTSP commits bridges to all eligible-partner atoms within `cfg.btsp_radius`. The combination of BTSP-inspired plasticity + continuous-substrate dynamics + bidirectional bridges (G13) is, to our reading, not a commonly studied combination, but we have not done a comprehensive novelty review.

### G15 — The Dreaming Substrate

**Plain English.** When real brains sleep, they replay the day's experiences. This is how memories get strong enough to last. While replaying, brains also combine pieces of different memories into new ones — that is where dreams get strange and where new ideas come from. The substrate now does the same thing. With its inputs gated off, it picks recently-active atoms and re-fires them. The connections between them get stronger. Sometimes two different patterns fire close to each other in time, and the substrate creates a new atom that combines them — a concept that nobody trained.

**Technical detail.** References: Wilson & McNaughton 1994 (sequence replay during slow-wave sleep), Buzsáki 2015 (sharp-wave-ripple-gated consolidation), Lewis & Durrant 2011 (overlapping replays merge schemas), Hobson AIM model (forward modelling with input gate closed). Implementation in `world/dream.py`. Three primitives:

1. **Replay** — `apply_dream` selects the highest-eligibility atoms in trained engrams and injects `cfg.dream_replay_seed_charge` directly. Subsequent neuron-dynamics fires them; BTSP, already in the tick loop, runs offline and consolidates trained-engram bridges.
2. **Concept blending** — when two distinct `pattern_id`s fire within `cfg.dream_blend_co_activation_window` seconds (default 0.5 s), the substrate allocates a new atom at their spatial centroid with a fresh `pattern_id`. G18 extends this with **integration bridges** connecting the new atom to representative members of both source patterns (Lewis & Durrant 2011 schema integration).
3. **Cross-modal hallucination** — because G13 bidirectional bridges are active during dreaming, replay seeds in (e.g.) the visual port drive vibrations through bridges into the audio output port. The substrate hears its own dreams.

G18.2 adds two-phase NREM/REM gating: 4 of every 5 dream ticks are consolidation-only; only the 5th allows new pattern formation. Real mammalian sleep is roughly 4:1 NREM:REM.

### G16 — The Self-Aware Substrate

**Plain English.** Up to here the substrate could learn things and dream. But it had no representation of *itself*. We added that. The substrate now keeps a running list of which patterns it has been firing, and how often. It picks the most-active pattern and "broadcasts" it across the whole substrate — a winner-take-all suppression of competing patterns. It predicts what its own next moment will look like, then measures the actual next moment, and uses the difference to adjust its own learning rate. Block (1995) called the operational version of this *access consciousness* — information that is globally available for reasoning and reporting. The four mechanisms here approximate aspects of that operational definition. They do **not** capture phenomenal consciousness — what it is like to be the substrate — and do not claim to.

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

**Plain English.** With all the above in place, we built one driver that runs the substrate forever, on its own. It alternates between awake (learning from input) and dream (consolidating + blending) phases. It tunes its own learning rate based on its prediction error. It checks five "emergence markers" each cycle. When all five hold simultaneously for several consecutive cycles, it writes a JSON file logging the conjunction. The loop keeps running. You can leave it running indefinitely on a normal MacBook. (An earlier version of this section described the logged event as "access-conscious self-modeling autopoietic agency" — that phrasing was a mistake. The substrate is not autopoietic in Maturana & Varela's technical sense, see Scope statements above.)

**Technical detail.** Implementation in `agent/autonomous_loop.py` and `agent/run_autonomous.py`. The five emergence markers (`check_emergence_markers`):

| # | Marker | Operational definition |
|---|---|---|
| 1 | self-model non-empty | `len(world.self_model) ≥ 2` |
| 2 | workspace winner | `world.workspace_winner_pattern_id > 0` |
| 3 | prediction loop closed | `0 < self_prediction_error < 1` (per Friston FEP — closed loop, not error → 0) |
| 4 | self-modification fired | `cfg.btsp_potentiation` has drifted from default by ≥ 0.5 |
| 5 | pattern repertoire grew during the run | `n_patterns_now > n_patterns_at_start` — at least one new atom must form via the G15.2 concept-blending rule. The earlier `≥ 2` threshold was trivially met by the 3 pre-seeded patterns and is corrected here. |

First overnight run (2026-05-09): the five pre-registered marker conditions held continuously across 334 substrate cycles (sim-time 1452 s, ~24 min). During the run, 125 new pattern atoms were created via the hand-coded G15.2 concept-blending rule, taking the substrate from 3 pre-seeded patterns to 128. The self-model histogram covered 64 of those patterns. The matched negative-control run (`docs/marker_protocol.md`) does not produce the five-way conjunction when trained engrams are absent. `~/.eqmod/autonomous/EMERGENCE.json` was persisted. The markers are pre-registered; tuning thresholds after a failed run is excluded by protocol. The "+125 emerged" formulation in an earlier version of this paragraph was misleading: the new atoms are the deterministic output of the hand-coded blending rule operating on the substrate's current state, not unexplained emergence.

### G19 — Predictive babble (2026-05-10)

**Plain English.** G18 left the substrate self-modelling on its own pre-seeded engrams — grounded in nothing outside itself. G19 wires it to a real sensory channel: hours of German speech across four progressive curriculum stages (audiobook narrator → single YouTuber → multi-speaker podcasts → webcam live). The substrate does **not** see raw audio — a fixed MFCC frontend discretises the signal into K clusters first, and the substrate sees only cluster-ID transitions. The question G19 asks is therefore narrower than "did it learn German phonology": it asks whether the substrate's open-loop output, after training, reproduces the *MFCC-cluster transition distribution* of held-out training audio better than three control corpora (white noise, time-reversed German, French). The acceptance criterion is binary and pre-registered: PASS when the trained substrate's MFCC-histogram KL-divergence to held-out German is lower than each control's by ≥ 2 standard deviations on bootstrap; NULL or FAIL otherwise, reported faithfully.

**Technical detail.** Spec at [`docs/superpowers/specs/2026-05-10-predictive-babble-design.md`](docs/superpowers/specs/2026-05-10-predictive-babble-design.md). Operational guide at [`docs/predictive-babble.md`](docs/predictive-babble.md). Pipeline in `agent/{corpus_builder,decoder_audio,babble,convergence,curriculum_scheduler,corpus_audio_feeder,evaluate_babble,run_babble_experiment}.py` plus `world/audio_predictor.py`. The autonomous loop change in `agent/autonomous_loop.py` is +14/-1 lines accepting an optional `audio_io`; G17 emergence runs are unaffected.

Pipeline-correctness verified end-to-end: `python -m agent.run_babble_experiment --mini` produces 4 wav files + verdict JSON in ~17 s.

**First real-corpus run (2026-05-10, `real-de-run`): FAIL.** The trained substrate's z-scores against the three controls were −1.00 (white noise), −0.69 (time-reversed DE), +0.17 (synthetic FR — flagged degraded). The trained substrate's output distribution is statistically indistinguishable from white noise. Additionally the run was killed at stage 2 of 4 because per-tick wall-clock grew from 3 s to 50+ s as vibrations accumulated, before natural convergence could be reached. Subsequent fixes (`c7e32ff` top-K vibration-emission cap; `964732f` per-tick vibration cull) shipped on 2026-05-10 to address the kill cause. A clean re-run with the fixes and a real (non-synthetic) FR control is the next item on the work list.

**As of 2026-05-10, the G19 acceptance criterion has not been met and the falsifier is open.** The earlier marketing of G19 as "the substrate babbles in the language's phonology" is retracted until a clean re-run produces a passing result.

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
