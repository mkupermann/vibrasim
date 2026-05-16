# Flux Substrate — Encoder-Free Audio Learning (Novel Path)

> **Goal:** Test whether the flux substrate self-organizes audio representations *without* a hand-engineered cochlea front-end. If yes, this is the first demonstration of self-organizing audio encoding on a non-neural physics substrate. If no, it documents that DSP-frontend engineering is load-bearing for substrate audio learning. Both outcomes are publishable findings.

> **User mandate 2026-05-16 23:25**: "Ich will eine neue Methode finden, die wissenschaftlich als auch technisch vollkommen neu ist." Plus hardware constraint: must run on user's existing Apple Silicon Mac with current Python venv.

## Scientific framing

The existing F2 implementation (R-3, on main) routes audio through a hand-engineered log-spaced damped-resonator-bank cochlea. The cochlea extracts frequency-domain features per audio frame; only those features touch the substrate. **The substrate does NOT see raw audio.** This is the engineering shortcut R-3 took.

Encoder-free path: remove the cochlea entirely. Inject **one energy quantum per audio sample**, with:

- `energy = abs(sample_value)` (or `sample_value²` — pre-registered choice)
- `freq = log(SR/2)` (constant — substrate gets NO frequency information, must build it from temporal structure alone)
- `pos` distributed across the hot-floor plane via deterministic hash from sample index
- `polarity = +1`
- `vel` per F1c bidirectional injection (vel_z_sigma=0.5)

At 16 kHz mono audio, that is 16000 quanta-injections per second of audio — the substrate's hot floor becomes a continuous Poisson-shape pulse stream modulated by amplitude. The substrate has to build any spectral structure (harmonics, formants, phonemes) from temporal correlations in the pulse rate.

**No prior published work demonstrates this.** Closest analogs:

- Wolfram Physics Project: no audio, no learning
- Neural Cellular Automata (Mordvintsev et al.): each cell is a learned MLP — still neural
- Echo State Networks: train output layer on engineered features (frequency-domain reservoirs are pre-set)
- Spiking Neural Networks: explicit neuron primitives + STDP-like learning

The encoder-free flux substrate is unusual on each of these axes simultaneously.

## Acceptance contract — three items

### R-9 — encoder-free spec + plan

Goal: write a pre-registered plan covering R-10 (implementation) and R-11 (training-and-evaluation). Locks the exact injection rule + the comparison protocol against the baseline R-3/R-8 cochlea-based path.

**Pre-registered acceptance for R-9:**

- `tests/test_research_plan_structure.py::test_encoder_free_plan_exists_and_well_formed PASSES` — NEW meta-test (similar pattern to F2/F3 plan structure tests). Plan file `docs/superpowers/plans/2026-05-DD-flux-encoder-free-audio-detailed.md` exists with: `Acceptance contract`, `File structure (locked decisions)`, `Open calibration choices`, at least one `## Task N`, at least one `tests/flux/test_*.py` acceptance path, explicit `negative control` paragraph, explicit comparison to R-3 baseline.
- Plan must declare the R-10 acceptance pytest paths (`tests/flux/test_audio_raw_injection.py`) and the R-11 acceptance pytest paths (`tests/flux/test_encoder_free_training_run.py` and `tests/flux/test_encoder_free_negative_control.py`).
- Plan must commit to a specific energy-mapping rule (`abs(sample)` vs `sample²` vs other) and to the no-frequency-information constraint (freq constant across all injected quanta).

Time budget: 4 hours.

### R-10 — encoder-free implementation

Goal: implement `inject_raw_audio_sample` and a minimal evaluation harness. Must NOT modify F2's cochlea (the baseline must remain intact for the R-8-vs-R-11 comparison).

**Pre-registered acceptance for R-10:**

- `tests/flux/test_audio_raw_injection.py::test_raw_injection_one_quantum_per_sample PASSES` — NEW: feed a 0.1 s 1 kHz sine wave at 16 kHz SR, assert exactly 1600 quanta injected, all with `freq = log(SR/2)` (no scatter), energies tracking the rectified waveform.
- `tests/flux/test_audio_raw_injection.py::test_raw_injection_silence_injects_zero_energy PASSES` — NEW: feed 0.1 s silence, assert injected quanta have energy ≈ 0 (within float epsilon).
- `tests/flux/test_audio_raw_injection.py::test_raw_injection_amplitude_modulation_visible_in_substrate PASSES` — NEW: feed amplitude-modulated tone, assert substrate's hot-floor energy density modulates correspondingly. Acceptance threshold: Pearson correlation between input envelope and substrate floor-energy time-series ≥ 0.7.
- `tests/flux/test_conservation.py PASSES` — T1 still holds with new injector.
- `tests/flux/test_cochlea.py PASSES` — F2 baseline cochlea unchanged.
- `tests/flux/test_synthesis.py PASSES` — F2 baseline synthesis unchanged.
- `pytest -m "not slow"` PASSES (legacy regression).

Time budget: 8 hours.

### R-11 — encoder-free training run + falsification + comparison to R-8 baseline

Goal: train two substrate instances on identical English audio — one through the cochlea (R-3 baseline), one encoder-free (raw injection). Run a matched-wallclock no-input control for each. Evaluate babble (via the F2 synthesis layer in both cases) against held-out test audio MFCC distribution.

**Pre-registered acceptance for R-11:**

- `tests/flux/test_encoder_free_training_run.py::test_encoder_free_substrate_distinguishable_from_no_input_control PASSES` — NEW: KL divergence of encoder-free substrate's babble-MFCC-histogram vs no-input control's babble-MFCC-histogram > 2σ on 100-bootstrap. (Substrate must have learned *something* from the audio that the no-input control cannot reproduce.)
- `tests/flux/test_encoder_free_negative_control.py::test_no_input_control_produces_no_substrate_specific_signal PASSES` — NEW: matched-wallclock no-input substrate produces babble statistically indistinguishable from white-noise MFCC distribution (sanity check that the negative control is honest).
- `docs/flux/phase-log.md` has an R-11 entry with both runs' bootstrap means + stds and the verdict comparison.
- Cross-comparison observation in `LOGBOOK.md`: tabulate KL divergences for cochlea-baseline (R-8) vs encoder-free (R-11). The expectation is NOT that encoder-free beats baseline; the expectation is that we *measure* the gap and learn from it.

Time budget: 24 hours.

## File structure (locked decisions)

R-9 creates:
- `docs/superpowers/plans/2026-05-<DD>-flux-encoder-free-audio-detailed.md`
- `tests/test_research_plan_structure.py` modified to add `test_encoder_free_plan_exists_and_well_formed`

R-10 creates:
- `agent/flux/audio_raw.py` — new module with `inject_raw_audio_sample(audio_array, quanta, grid, ...)`
- `tests/flux/test_audio_raw_injection.py`

R-10 modifies:
- `agent/flux/__init__.py` (re-export `inject_raw_audio_sample`)
- `docs/flux/phase-log.md` (R-10 entry)

R-11 creates:
- `tests/flux/test_encoder_free_training_run.py`
- `tests/flux/test_encoder_free_negative_control.py`

R-11 reads (does NOT modify):
- F2 cochlea/synthesis from `agent/flux/cochlea.py` and `agent/flux/synthesis.py` — used for R-8 baseline comparison only.

R-11 modifies:
- `docs/flux/phase-log.md` (R-11 closing entry)
- `LOGBOOK.md` (cross-comparison findings)

No edits anywhere outside `agent/flux/`, `tests/flux/`, `tests/`, `docs/flux/phase-log.md`, `LOGBOOK.md`.

## Open calibration choices (locked here — no per-run retuning)

| Param | Default | Purpose |
|---|---|---|
| `SR` | 16000 | audio sample rate (matches F2) |
| Substrate dimensions | 80 × 40 × 10 voxels | matches R-1 calibrated config (T2 known fragile but T1/T3/T4 robust) |
| Run duration | 30 min wall-clock per training stage | shorter than full G19 (24 h) for vacation time budget; if R-11 PASS at 30 min, run extension is post-vacation |
| Audio corpus | reuse R-7's English corpus build (Stage 1 audiobook + Stage 4 substitute) | minimizes new fetch work |
| Quantum buffer | `max_quanta=500_000` | 16 kHz × 30 min = 28.8M injections; damping must keep alive population bounded — record peak in phase-log |
| Bootstrap N | 100 | matches F2 evaluator default |

## Why R-9/R-10/R-11 sit *after* R-5/R-6/R-7/R-8 in the queue

The baseline (cochlea + monotone-flux plasticity) must run first to establish "did this substrate learn anything *with* engineered help". Encoder-free is the harder bar. If the baseline fails to learn from English audio even with cochlea engineering, encoder-free is unlikely to succeed and we have a different problem (substrate plasticity rule, not encoder choice). If the baseline does learn, encoder-free becomes the interesting question.

## Compute and hardware footprint

Per-tick cost: same as current substrate **minus** the cochlea resonator-bank Crank-Nicolson step (32 resonators × 4 state vars × 1 step = ~128 FLOPs per tick saved). Encoder-free is *cheaper* than F2 baseline.

Per-run cost: 30 min audio × 16 kHz × 1 quantum per sample = 28.8M injections. Substrate physics tick dominates injection cost. Estimated 4-8 h wall-clock per training stage on Apple M-series. Fits in the 4 h per-session cap with `--realtime` disabled.

Hardware: user's existing Mac (Apple Silicon M-series, Python 3.13, .venv). No GPU required, no cluster. All compute is single-threaded numpy / numba-JIT physics tick. The user can replicate independently with a `git clone` and `pip install -e .[dev,dashboard,agent]` plus `python -m agent.run_autonomous --config corpus.training-EN.yaml --raw-injection`.
