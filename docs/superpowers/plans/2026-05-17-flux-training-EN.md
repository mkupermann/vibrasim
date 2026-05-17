# Flux Substrate Training — English Audio Corpus

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal.** Take the F2 cochlea + F3 plasticity stack out of the synthetic-tone regime and into a real English-language audio corpus. Pre-register one binary acceptance: after a long exposure to real speech (Stages 1+2 mandatory, Stage 4 substitute mandatory, Stage 3 deferred), the substrate's surviving bridge topology must be **statistically closer to the corpus's own log-power spectrum** than a matched-wallclock substrate driven by spectrally-flat gaussian noise through the SAME cochlea. If both pass the metric, the metric is a state detector — verdict NULL per the autopilot charter's negative-control rule.

Training closes when:

- Trained substrate (English corpus) reaches `corpus_alignment_index >= alignment_thresh_train` (`tests/flux/test_training_run.py`)
- Matched-wallclock white-noise control substrate stays below `alignment_thresh_control` AND the trained-minus-control margin reaches `margin_min` (`tests/flux/test_training_negative_control.py`)
- T1 conservation, T2 Bénard, T3 crystallization, T4 decay all still pass
- F2 cochlea + synthesis baselines still pass (the corpus pipeline is additive; the substrate must not regress)

**Honest pre-registration of R-5 fail-shut.** R-5 (F3 learning structure-level falsification) returned NULL on its first attempt — the slow acceptance test ran for 6.5 h before SIGTERM (postflight had no timeout). The implementation code (`agent/flux/learning_run.py`, `agent/flux/learning_metric.py`, both negative-control and training tests) is preserved on `main`. The thresholds in `docs/superpowers/plans/2026-05-16-flux-substrate-F3.md` remain locked. **This training plan does not depend on R-5 having reached PASS** — the F3 learning rule (spec §5.5) is *already live in the substrate code* (it has been since F1b's `world/flux/plasticity.py`). What R-5 failed to demonstrate within its acceptance protocol is that the rule produces a measurable structure-level signal on the synthetic 1 kHz tone-burst probe within the budget allotted. R-8 (the training run) is the next-larger probe of the same rule, on real speech, with budget and instrumentation sized for that scale. If R-8 also NULLs, that result feeds the post-vacation decision on whether the binding rule itself needs reconsidering (spec §11). The training corpus is a worthwhile experiment to run regardless — a NULL training run is itself a finding.

**The F3 learning rule, by name, and how this corpus exercises it.** The rule is the **spec §5.5 monotone-flux bridge plasticity** rule (also referred to as `apply_plasticity` in `world/flux/plasticity.py`, integrated by R-4's plan as the F3 learning mechanism):

```
w(t+1) = w(t) + γ · flux_through(t) − λ · max(0, flux_min − flux_through(t))
```

The rule has two terms. The first integrates flux along an edge as a state variable: every quantum that traverses a bridge strengthens it. The second decays bridges whose flux stays below `flux_min`. Under sustained patterned input, bridges along the input's flux paths accumulate weight and survive pruning; bridges off the input's flux paths stay below `flux_min` and die. The rule is **not** STDP (no pre-/post-synaptic spike timing), **not** Hebbian co-activation (a bridge's flux is one number per edge, not a coincidence on its endpoints), **not** BTSP (no eligibility trace, no global plateau signal). It is path-monotone integration of flux along an edge, with a deficit-decay term.

The English corpus exercises this rule by sustained, structured cochlear input. English speech is broadband but *not* uniform: it concentrates energy in the 80–400 Hz fundamental band (F0) and the 250–3400 Hz formant band, with characteristic temporal envelope statistics (syllable rate ≈ 5 Hz, phoneme rate ≈ 15 Hz, formant transitions on 30–80 ms scales). The cochlea bank (F2, 64 log-spaced resonators 50–8000 Hz) channels this input into floor-injected quanta whose frequency tracks the corpus's spectrum. Bridges that form between substrate nodes whose endpoint frequencies fall in speech-relevant bands will see sustained flux above `flux_min` and survive; bridges between substrate nodes whose endpoint frequencies fall in speech-irrelevant bands (e.g. >5 kHz noise floor, near-Nyquist) will see flux below `flux_min` and decay. The metric is the **corpus-alignment index**: the divergence (Jensen-Shannon) between the substrate's surviving-bridge-endpoint frequency distribution and the corpus's log-power spectrum. The negative control runs the SAME substrate for the SAME wallclock through the SAME cochlea, but driven by spectrally-flat gaussian white noise (RMS-matched per-stage). A substrate that has truly been reconfigured by the corpus must align with the corpus more than a substrate that has been reconfigured by structureless noise.

**What this plan is NOT.** Not a re-training of the cochlea (fixed per spec §5.6). Not an output-side acceptance — R-8 measures bridge topology, not synthesised babble. Not the Tier-1 LLR test from spec §9 row F3 (that is its own scope item if R-8 PASSes; for vacation it is out of scope). Not a new plasticity rule (the rule is §5.5, already live in `world/flux/plasticity.py`).

**Tech stack:** Python 3.13, numpy, pytest. `soundfile` for wav I/O (carried from F2). `yt-dlp` + `ffmpeg` for Stage 2 fetch (carried from G19 corpus_builder). `requests` for LibriVox/Internet-Archive fetch. No torch, no librosa, no transformers, no learned embeddings — those are forbidden per `CLAUDE.md`.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — §5.5 (plasticity rule), §5.6 (fixed cochlea), §5.7 (synthesis — not used here, R-8 is input-side only), §9 row F3 (Tier-1 LLR — explicitly out of vacation scope), §11 (pre-registration discipline). Also the F3 plan: `docs/superpowers/plans/2026-05-16-flux-substrate-F3.md` for the inherited threshold philosophy.

**Estimated wallclock:** R-7 corpus build ≤ 4 h (network + ffmpeg). R-8 training + control runs: ≤ 24 h wallclock each (configurable via `n_ticks_train` upper bound `120_000`), parallel-safe — so 24 h wallclock if run sequentially in autopilot, less if the postflight runs them concurrently against the 4 h per-session ceiling. R-6 (this plan): ≤ 4 h.

---

## Acceptance contract (binary)

- `uv run pytest tests/flux/test_training_run.py -v` PASSES — covers: (a) the corpus manifest from R-7 is loadable and the audio files are on disk, (b) the substrate run completes `n_ticks_train_min` ticks without raising or violating T1, (c) `n_bridges_alive >= n_bridges_min_alive_train` at end of run, (d) `corpus_alignment_index >= alignment_thresh_train`
- `uv run pytest tests/flux/test_training_negative_control.py -v` PASSES — covers: (a) the matched-wallclock control run with RMS-matched gaussian-white input through the SAME cochlea completes the SAME `n_ticks_train` and SAME RNG seed, (b) `n_bridges_alive >= n_bridges_min_alive_control`, (c) `corpus_alignment_index_control < alignment_thresh_control`, (d) `corpus_alignment_index_train − corpus_alignment_index_control >= margin_min`
- `uv run pytest tests/flux/test_conservation.py -v` still PASSES (T1: corpus-driven injection reuses the F2 auditor hook; no new energy paths)
- `uv run pytest tests/flux/test_benard.py -v` still PASSES (T2: cochlea is OFF in T2; corpus pipeline is not invoked)
- `uv run pytest tests/flux/test_crystallization.py -v` still PASSES (T3)
- `uv run pytest tests/flux/test_decay.py -v` still PASSES (T4)
- `uv run pytest tests/flux/test_cochlea.py -v` still PASSES (F2 cochlea unaffected — the corpus pipeline is an upstream waveform source, not a cochlea change)
- `uv run pytest tests/flux/test_synthesis.py -v` still PASSES (F2 synthesis unaffected — R-8 is input-side only)
- `uv run pytest -m "not slow"` still PASSES (legacy regression baseline holds)

These pytest paths — `tests/flux/test_training_run.py` and `tests/flux/test_training_negative_control.py` — are the pre-registered R-8 acceptance targets. R-8 implements against this contract. R-7 implements the corpus pipeline against `tests/flux/test_training_corpus_valid.py` and `tests/flux/test_training_corpus_manifest.py` (its own preregistered_acceptance block in `.eqmod/autopilot/QUEUE.yaml`).

---

## Pre-registered numeric thresholds (locked at this plan's commit time; no post-hoc retuning)

| Symbol | Value | Meaning |
|---|---|---|
| `language` | `"en"` | English. NOT German, NOT French (per user instruction 2026-05-13). The cochlea is language-agnostic but the corpus selection is committed. |
| `sample_rate_hz` | `16000` | Carried from F2. Cochlea bank `[50, 8000]` log-spaced fits comfortably below Nyquist. |
| `n_ticks_train_min` | `60_000` | Minimum substrate ticks per run (training and control). At F2's default 16 audio samples / tick, 60 000 ticks ≈ 60 s of audio = the lower bound that exercises plasticity beyond F3's 10 000-tick synthetic-probe regime. |
| `n_ticks_train_max` | `120_000` | Hard upper bound. R-8 may sweep `n_ticks_train` within `[60_000, 120_000]`. Going above 120 000 ticks is a protocol breach. |
| `alignment_thresh_train` | `0.50` | Trained substrate must reach `corpus_alignment_index >= 0.50`. Calibration justification: alignment = `1 − JS_divergence(p_bridge_freqs, p_corpus_log_power_spectrum)` where both distributions are quantised to the cochlea bank's 64 log-spaced bins. `JS_divergence` ranges [0, ln 2]; normalising gives `alignment ∈ [0, 1]`. A flat (white-noise) bridge distribution against an English-speech corpus gives `alignment ≈ 0.35` analytically (mass over the 50–8000 Hz log-band, integrated against the F0+formant peaks). A perfectly corpus-matched substrate gives `alignment = 1.0`. `0.50` is the midpoint between the "flat-bridge" baseline and the "perfect-match" ceiling — the minimum at which we claim the substrate is channelling structure, not noise. |
| `alignment_thresh_control` | `0.40` | White-noise control must stay BELOW `alignment_thresh_control = 0.40`. Calibration justification: a substrate driven by RMS-matched flat-spectrum noise through the same cochlea should produce bridges whose endpoint-frequency distribution approaches the cochlea's own log-spaced bin density, *not* the corpus's spectrum. `0.40` sits just above the analytical flat-bridge baseline `≈ 0.35` to allow for cochlea-quantisation drift, but stays well below `alignment_thresh_train = 0.50`. |
| `margin_min` | `0.10` | Trained − Control must be `>= 0.10`. Two-gate design (inherited from F3): trained crosses an absolute floor AND beats control by a margin. This rules out the "control accidentally drifted close to the corpus spectrum so trained looks high in comparison" failure mode. |
| `n_bridges_min_alive_train` | `50` | Trained substrate must end with ≥ 50 alive bridges. Below this, the alignment-index histogram is too sparse to be meaningful. Higher than F3's `30` because the broader-band input should produce more surviving bridges. |
| `n_bridges_min_alive_control` | `20` | Control substrate must end with ≥ 20 alive bridges. Below this, the control failed to function (silent-pass risk) — verdict NULL not PASS. Asymmetric floor (50 vs 20) reflects that structured input should produce more surviving bridges than flat noise; both floors are nonzero so the metric is always defined. |
| `seed_train` | `74747` | Locked RNG seed for the trained run. |
| `seed_control` | `74747` | SAME locked RNG seed for the control run — only the input waveform source differs. |
| `seed_whitenoise` | `99999` | Locked seed for the gaussian-white-noise generator inside the control's waveform builder. |
| `corpus_stage1_seconds_min` | `3600` | Stage 1 audiobook total ≥ 60 min (= 3 600 s). |
| `corpus_stage2_seconds_min` | `7200` | Stage 2 YouTuber total ≥ 120 min (= 7 200 s). |
| `corpus_stage4_seconds_min` | `1800` | Stage 4 substitute ≥ 30 min (per acceptance bullet). |
| `corpus_total_seconds_min` | `12600` | All-stage total ≥ 3 600 + 7 200 + 1 800 = 12 600 s ≈ 3.5 h of audio. |
| `js_normaliser` | `ln(2)` | JS-divergence normalising constant. `alignment = 1 − JS / ln(2)`. JS is computed on the cochlea-bank-quantised log-power spectrum vs the bridge-endpoint-frequency histogram with the same 64-bin quantisation. |
| `n_freq_bins` | `64` | Number of bins for the alignment histogram. Equals `cfg.cochlea_cfg.n_cochlea` so bridge frequencies and corpus spectrum live on the same support. |

These thresholds are pre-registered now and must NOT be moved post-hoc to make a failed R-8 run pass. If R-8 cannot meet them with a fair attempt within `n_ticks_train_max`, the verdict is NULL with a postmortem — exactly as `marker_protocol.md` requires.

---

## The corpus — single-language English, three stages, public-domain or CC-licensed

| Stage | Source class | Required total | Speaker count | Recording style |
|---|---|---|---|---|
| Stage 1 | LibriVox audiobook (public-domain), single narrator | ≥ 60 min | 1 | Studio narration, literary register, scripted prose |
| Stage 2 | Single YouTuber channel, single speaker, CC-licensed or fair-use educational | ≥ 120 min | 1 | Casual / conversational register, room acoustics, vocal variety |
| Stage 3 | **DEFERRED — multi-speaker out of vacation scope** | — | — | — |
| Stage 4 SUBSTITUTE | MIT OpenCourseWare audio lecture (CC-BY-NC-SA) — single speaker, distinct from Stage 1 and Stage 2 narrators | ≥ 30 min | 1 | Didactic / instructional register, classroom acoustics, technical vocabulary, frequent pause-and-question structure |

**Stage 1 — concrete commitment.** A single-narrator LibriVox recording of a public-domain English work. Default recommendation for R-7: any narrator with ≥ 60 min of contiguous work in the LibriVox top-50 by listen-count (e.g. Karen Savage, Mark F. Smith, Ruth Golding). LibriVox recordings are released to the public domain (LibriVox dedication, equivalent to CC0). Per-narrator solo selection avoids the multi-speaker confound that Stage 3 was intended for.

**Stage 2 — concrete commitment.** A single CC-licensed YouTube channel of a single speaker. Default recommendation for R-7: any CC-licensed (or LICENSE-checked fair-use educational) channel where one speaker dominates ≥ 90 % of audio. The G19 corpus_builder pipeline (`agent/corpus_builder.py` on main, used in 2026-05-10 babble run) demonstrates the fetch path; R-7 may reuse it directly. yt-dlp licence filter: prefer channels with explicit CC-BY in their channel metadata.

**Stage 4 substitute — concrete commitment + acoustic-difference paragraph.** A **single-speaker MIT OpenCourseWare audio lecture** of at least 30 min, licensed CC-BY-NC-SA, distinct speaker from Stages 1 and 2. MIT OCW lectures are publicly downloadable and the licence is compatible with EQMOD's research-non-commercial use. Default fetch URL list lives in R-7's `corpus.training-EN.yaml`; R-7 picks one lecture from a curated short-list (e.g. 6.001 SICP, 18.06 Linear Algebra, 8.01 Classical Mechanics audio tracks — each is a single male professor recorded in a classroom, the classroom acoustics are characteristic). The substitute is justified as follows:

> **Acoustic / distributional difference paragraph.** The Stage 4 substitute introduces a recording-condition and prosodic class not present in Stages 1 and 2. Stage 1 (LibriVox audiobook) is studio narration: tightly compressed dynamic range, no room reverberation, scripted literary register with even pacing and conventionalised sentence intonation. Stage 2 (YouTuber) is casual conversational speech: home-studio or room-acoustic recording, broad dynamic range, frequent vocal-fry / creaky-voice transitions, casual sentence-fragment cadence with frequent disfluencies. The Stage 4 substitute (MIT OCW lecture) is classroom-recorded didactic speech: distinct room reverberation (large lecture-hall RT60 ≈ 1.5–2.5 s), instructional register with frequent question-pause-answer prosody, technical vocabulary that pushes higher-formant energy density (consonant clusters from "polynomial", "eigenvector", "Hamiltonian") above the lyrical / conversational baseline. The distributional difference shows up in three measurable spectral / temporal features: (1) higher reverb tail energy in the 1–4 kHz band (classroom decay vs studio dryness), (2) higher consonant density per second from technical vocabulary (≈ 22 consonants/s in OCW vs ≈ 15 in studio narration and ≈ 18 in conversational YouTube speech), (3) characteristic pause-cluster statistics (long 0.5–2.0 s pauses at sentence boundaries, interspersed with very-short < 0.1 s pauses during whiteboard work). These three features push the corpus's spectral and temporal statistics into a region not covered by Stages 1 and 2 — without them, the substrate is hearing three audiobook narrators (one literary, one casual, one didactic) but all in similar acoustic conditions, which weakens R-8's claim that the substrate has aligned to *speech in general* rather than to *one studio-recording style*. The MIT OCW substitute provides the missing acoustic-condition variation while staying within the single-language English commitment.

**Fallback if the primary Stage 4 substitute source is unreachable.** R-7's `corpus.training-EN.yaml` lists three MIT OCW lecture candidates in priority order. If the network fetch fails for the first, R-7 falls back to the next; if all three fail, R-7 falls back to a LibriVox non-fiction recording (CC0 equivalent) by a distinct narrator from Stages 1 and 2 — a non-fiction LibriVox reading exhibits a different prosodic register from fictional narration (technical / didactic prose vs literary prose) and meets the "distinct distributional class" requirement, though it loses the classroom-acoustics feature.

**Licensing note.** All sources are public-domain (LibriVox), CC-BY / CC-BY-SA / CC-BY-NC-SA (MIT OCW, CC-licensed YouTube), or — for any CC-NC source — used for research-only / non-commercial work consistent with EQMOD's MIT-code / CC-BY-SA-docs licence and the user's research-use context (academic research, no public model release). R-7's manifest records the licence string per source.

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `agent/flux/training_run.py` | `TrainingRunConfig` dataclass (carrying corpus-manifest path, F2 cochlea cfg, F1b plasticity/decay/binding/thermal cfgs, the thresholds above) + `make_corpus_waveform(cfg) -> np.ndarray` (concatenates the manifest's per-stage audio into one float32 16 kHz mono signal, RMS-normalised per stage) + `make_control_waveform(cfg, n_samples) -> np.ndarray` (gaussian white noise, RMS-matched to the corpus signal, seeded `cfg.seed_whitenoise`) + `run_training_session(cfg, input_kind: Literal["train","control"]) -> TrainingRunResult`. Reuses `agent/flux/learning_run.py::run_learning_session` infrastructure where it overlaps; the F3 run-loop body is copy-paste-modified (substituting the corpus waveform for the tone-burst generator) rather than refactored mid-vacation. |
| `agent/flux/training_metric.py` | `corpus_alignment_index(bridges, nodes, corpus_log_power_spectrum, n_freq_bins) -> float` — pure function over substrate state. Returns `alignment ∈ [0, 1]`. Definition: bin alive-bridge endpoint frequencies into `n_freq_bins` log-spaced bins matching the cochlea bank; normalise to a probability distribution `p_bridge`; the corpus's log-power spectrum is pre-computed and quantised to the same `n_freq_bins`; compute Jensen-Shannon divergence `JS(p_bridge || p_corpus)`; return `1 - JS / ln(2)`. If no alive bridges, return `0.0`. |
| `agent/flux/corpus_spectrum.py` | `compute_corpus_log_power_spectrum(corpus_waveform, sample_rate_hz, n_freq_bins, freq_band_hz) -> np.ndarray` — pure function. Welch periodogram on the corpus waveform, log-magnitude, quantised to the `n_freq_bins` log-spaced bins of the F2 cochlea bank, normalised to sum to 1.0. Cached to `~/.eqmod/training/EN/spectrum.npy` so R-8's two runs do not recompute. |
| `tests/flux/test_training_corpus_valid.py` | R-7 acceptance: parses `corpus.training-EN.yaml`, asserts every listed audio file exists on disk, asserts per-stage durations meet the `corpus_stage{1,2,4}_seconds_min` floors, asserts sample-rate is 16 kHz mono. |
| `tests/flux/test_training_corpus_manifest.py` | R-7 acceptance: opens `~/.eqmod/training/EN/manifest.json`, asserts the schema (per-stage durations, source URLs, sha256 of each file). |
| `tests/flux/test_training_run.py` | R-8 trained-run acceptance: builds a `TrainingRunConfig` pointing at the R-7 manifest, runs `run_training_session(cfg, "train")`, asserts `n_bridges_alive >= n_bridges_min_alive_train` and `corpus_alignment_index >= alignment_thresh_train`. Also asserts T1 inline (energy conservation during the run). |
| `tests/flux/test_training_negative_control.py` | R-8 negative-control acceptance: builds the SAME `TrainingRunConfig`, runs `run_training_session(cfg, "control")`, asserts `n_bridges_alive >= n_bridges_min_alive_control`, `corpus_alignment_index < alignment_thresh_control`, AND `index_train − index_control >= margin_min`. The trained result is recomputed inside this test (not imported from `test_training_run.py`) so the test is hermetic — uses the SAME locked seed `seed_train=74747` so the trained run is byte-identical. |

Modified files:

| Path | What changes |
|---|---|
| `agent/flux/__init__.py` | Re-export `TrainingRunConfig`, `TrainingRunResult`, `run_training_session`, `corpus_alignment_index`, `compute_corpus_log_power_spectrum`. |
| `docs/flux/phase-log.md` | R-7-start, R-8-start, per-sweep, R-8-close entries. |
| `README.md` | One-line status update on training phase. |
| `corpus.training-EN.yaml` | NEW (sits at repo root with the other top-level configs). YAML manifest of stage sources: per-stage URL list, expected duration range, expected licence string, fallback URL list for Stage 4. |

**Files explicitly NOT touched:**
- `world/flux/*` — no substrate physics changes. R-8 is run-orchestration + metric, not a substrate extension.
- `world/flux/plasticity.py` — the §5.5 monotone-flux bridge plasticity rule is THE learning rule under test; R-8 does not modify it.
- `agent/flux/cochlea.py` — the cochlea is FIXED per spec §5.6 and F2.
- `agent/flux/synthesis.py` — R-8 is input-side only; synthesis is not invoked during training or control.
- `agent/flux/learning_run.py` and `agent/flux/learning_metric.py` — the R-5 F3 implementation is preserved on `main` and not modified by R-8 (R-8 is the larger-scale corpus probe, not a re-attempt of the F3 synthetic-tone probe).
- `docs/marker_protocol.md` and `docs/marker_protocol_G20-G23_addendum.md` — frozen by autopilot charter.

**Conservation accounting note:** the F2 cochlea injection auditor hook is reused unchanged. R-8 adds no new energy paths. Audit assertions inside `run_training_session` are inherited from `dynamics.tick`. The trained and control runs both balance their books through the same `audit.record_injection` / `audit.record_decay_heat` / `audit.record_binding_heat` channels.

---

## Open calibration choices

These are the knobs R-8's implementation session may sweep within the pre-registered ranges. Defaults below are the starting point; any move requires a phase-log entry naming the swept variable, the old value, the new value, and which threshold (if any) it pushed against.

| Param | Default | Range | Purpose |
|---|---|---|---|
| `n_ticks_train` | `60_000` | `[60_000, 120_000]` | Substrate ticks per run. Upper bound is the pre-registered ceiling — going above 120_000 is a protocol breach. |
| `corpus_stage_order` | `[stage1, stage2, stage4_substitute]` | locked order, no shuffle | Pre-register the curriculum order. Shuffling would change the substrate-state trajectory and is post-hoc retuning. |
| `corpus_repeat_to_fill_ticks` | `True` | `{True, False}` | If `n_ticks_train * n_audio_samples_per_tick` exceeds the corpus length, loop the corpus. Default True so the trained substrate sees the whole corpus at least once. |
| `binding_alpha` | F1b-locked | F1b-locked | Pred-coherence gain. R-8 does NOT retune binding. |
| `binding_beta` | F1b-locked | F1b-locked | Temperature-gate gain. R-8 does NOT retune. |
| `T_crit` | F1b-locked | F1b-locked | Binding T-cap. R-8 inherits. |
| `plasticity_gamma` | F1b-locked | F1b-locked | Flux-strengthen rate (the γ in the §5.5 rule). R-8 inherits. |
| `plasticity_lam` | F1b-locked | F1b-locked | Deficit-decay rate (the λ in the §5.5 rule). R-8 inherits. |
| `plasticity_flux_min` | F1b-locked | F1b-locked | Bridge-flux deficit threshold (the `flux_min` in the §5.5 rule). R-8 inherits. |
| `cochlea_inject_gain` | F2-locked (`1.0`) | F2-locked | Cochlea→injection mapping. R-8 inherits F2's tuned value. |
| `cochlea_peak_floor` | F2-locked (`2.0`) | F2-locked | Cochlea peak noise-floor subtraction. R-8 inherits. |
| `grid_dims` | F1b-locked | F1b-locked | Grid geometry. R-8 uses the same grid the F1b/F1c/F2/F3 tests use. |

**Calibration discipline.** R-8 may sweep `n_ticks_train` (and only `n_ticks_train`) within the pre-registered range up to **3 sweeps** before escalating. Order of sweeps:

1. `n_ticks_train` `60_000 → 90_000`
2. `n_ticks_train` `90_000 → 120_000`
3. If still NULL: STOP, write postmortem to LOGBOOK, mark R-8 NULL.

**Do NOT sweep:** binding, plasticity, decay, thermal, cochlea — those are F1b/F1c/F2-locked. **Do NOT sweep the corpus** — adding more audio after seeing a NULL is post-hoc retuning. **Do NOT sweep the metric** — changing from JS to KL or from 64 bins to 128 after seeing results is post-hoc retuning. Sweeping any of these is exactly what the pre-registration discipline forbids.

---

## Task 1: R-6 plan close — phase-log entry + queue handoff

**Files:** Modify `docs/flux/phase-log.md`.

- [ ] Append the training-EN-plan-close block describing: scope (real English corpus, three stages with Stage 4 substituted and Stage 3 deferred), the locked thresholds table (copy from this plan's "Pre-registered numeric thresholds" section), the deferred items (Stage 3, Tier-1 LLR), and the locked pytest acceptance paths (`tests/flux/test_training_run.py`, `tests/flux/test_training_negative_control.py`, `tests/flux/test_training_corpus_valid.py`, `tests/flux/test_training_corpus_manifest.py`). Reference this plan file by full path.
- [ ] Commit: `flux training EN plan: R-6 close`.

---

## Task 2: corpus.training-EN.yaml manifest (R-7 input file)

**Files:**
- Create: `corpus.training-EN.yaml`

R-6 commits the manifest *schema* and the *source-class commitments* (Stage 1 = LibriVox single narrator; Stage 2 = single CC-licensed YouTuber; Stage 4 substitute = MIT OCW lecture). R-7 *fills in the URLs and the fallback URLs*. R-6 writes the empty-schema YAML so R-7 has a target to populate.

- [ ] **Step 1: Author the YAML schema.**

```yaml
# corpus.training-EN.yaml — pre-registered training corpus, single-language English.
language: en
sample_rate_hz: 16000
channels: 1   # mono
stages:
  stage1:
    source_class: librivox_single_narrator_public_domain
    duration_seconds_min: 3600
    licence: "public domain (LibriVox dedication, CC0-equivalent)"
    primary_urls: []   # R-7 fills in 1+ LibriVox MP3 / OGG URLs for one narrator
    fallback_urls: []  # R-7 fills in second-choice narrator if primary unreachable
  stage2:
    source_class: cc_youtuber_single_speaker
    duration_seconds_min: 7200
    licence: "CC-BY or CC-BY-SA (channel-declared)"
    primary_urls: []   # R-7 fills in 1+ youtube.com URLs from one CC-licensed channel
    fallback_urls: []  # R-7 fills in second-choice channel if primary unreachable
  stage3:
    source_class: deferred_multi_speaker_out_of_vacation_scope
    duration_seconds_min: 0
    licence: "n/a — deferred"
    primary_urls: []
    fallback_urls: []
  stage4_substitute:
    source_class: mit_ocw_single_lecture
    duration_seconds_min: 1800
    licence: "CC-BY-NC-SA (MIT OpenCourseWare)"
    distinct_from_stages: [stage1, stage2]   # speaker must not overlap Stages 1 and 2
    acoustic_class: "didactic / classroom-recorded / instructional prosody / technical vocabulary"
    primary_urls: []   # R-7 fills in 1 MIT OCW audio-lecture URL
    fallback_urls: []  # R-7 fills in 2 more in priority order; final fallback is a LibriVox non-fiction reading by a distinct narrator
```

- [ ] **Step 2: Commit** `flux training EN: corpus manifest schema (R-7 to populate URLs)`.

---

## Task 3: corpus-spectrum precomputation (R-7 helper, lifted into R-6 because it's part of the acceptance instrument)

**Files:**
- Create: `agent/flux/corpus_spectrum.py`

The corpus log-power spectrum is one half of the alignment metric. R-7 fetches the audio; R-8 runs the substrate; the spectrum compute lives in `agent/flux/corpus_spectrum.py` so the metric module can import it cleanly. The function is pure (waveform in, normalised distribution out), so R-6 can stub it now.

- [ ] **Step 1: Write the spectrum-compute function.**

```python
"""Compute the corpus log-power spectrum, quantised to the cochlea bank.

Used by tests/flux/test_training_*.py to produce the corpus-side
distribution that the bridge-endpoint distribution is compared against.
Cached at ~/.eqmod/training/EN/spectrum.npy.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from scipy.signal import welch


CACHE = Path.home() / ".eqmod" / "training" / "EN" / "spectrum.npy"


def compute_corpus_log_power_spectrum(
    corpus_waveform: np.ndarray,
    sample_rate_hz: int,
    n_freq_bins: int = 64,
    freq_band_hz: tuple[float, float] = (50.0, 8000.0),
    use_cache: bool = True,
) -> np.ndarray:
    """Return a length-`n_freq_bins` probability distribution.

    Steps:
      1. Welch periodogram over the entire corpus waveform.
      2. Take log10 of the power (with a floor to avoid log(0)).
      3. Quantise to `n_freq_bins` log-spaced bins between `freq_band_hz`.
      4. Re-normalise to sum to 1.0.
    """
    if use_cache and CACHE.exists():
        cached = np.load(CACHE)
        if cached.shape == (n_freq_bins,):
            return cached
    f, p = welch(corpus_waveform, fs=sample_rate_hz, nperseg=4096)
    p_log = np.log10(np.maximum(p, 1e-12))
    bin_edges = np.geomspace(freq_band_hz[0], freq_band_hz[1], n_freq_bins + 1)
    binned = np.zeros(n_freq_bins, dtype=np.float64)
    for i in range(n_freq_bins):
        mask = (f >= bin_edges[i]) & (f < bin_edges[i + 1])
        if mask.any():
            binned[i] = float(p_log[mask].mean())
    # Shift so all bins are positive (so we can normalise as a probability).
    binned -= binned.min()
    total = binned.sum()
    if total > 0:
        binned /= total
    else:
        binned[:] = 1.0 / n_freq_bins
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.save(CACHE, binned)
    return binned
```

- [ ] **Step 2: Add a smoke test in `tests/flux/test_training_run.py`** (the file is created in Task 6; R-6 stubs only the metric-side tests in Task 4).

- [ ] **Step 3: Commit** `flux training EN: corpus_spectrum helper`.

---

## Task 4: corpus-alignment metric (pure function over substrate state)

**Files:**
- Create: `agent/flux/training_metric.py`
- Create: `tests/flux/test_training_run.py` (alignment-metric section only — the full-run acceptance test lands in Task 6)

The metric is purely topology-side on the substrate input, and pure-function on the corpus side. Reuses the F3 plan's design: alive-bridges' endpoint frequencies → log-spaced histogram → Jensen-Shannon vs corpus spectrum → `1 − JS/ln(2)`.

- [ ] **Step 1: Tests first (alignment-metric only).**

```python
"""R-8 corpus-alignment metric unit tests (R-6 stubs the fast cases here;
the full substrate-run test lands in Task 6 marked @pytest.mark.slow)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.bridges import Bridges
from world.flux.structures import Nodes
from agent.flux.training_metric import corpus_alignment_index


def test_alignment_zero_when_no_bridges():
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    p_corpus = np.ones(64) / 64
    assert corpus_alignment_index(b, n, p_corpus, n_freq_bins=64) == 0.0


def test_alignment_high_when_bridge_dist_matches_corpus():
    """If all bridges sit in the bin that holds most of the corpus mass,
    alignment is close to 1 (perfectly matched)."""
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    # Place two nodes at log(1000) frequency (1 kHz).
    log_1k = float(np.log(1000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    # Corpus also concentrates at log(1000) — the bin containing 1 kHz.
    p_corpus = np.zeros(64)
    bin_edges = np.geomspace(50.0, 8000.0, 65)
    target_bin = int(np.searchsorted(bin_edges, 1000.0) - 1)
    p_corpus[target_bin] = 1.0
    alignment = corpus_alignment_index(b, n, p_corpus, n_freq_bins=64)
    assert alignment > 0.95


def test_alignment_low_when_bridge_dist_disjoint_from_corpus():
    """If all bridges sit in a bin with zero corpus mass, alignment is low."""
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    log_6k = float(np.log(6000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_6k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_6k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    # Corpus concentrates at 1 kHz; bridges live at 6 kHz.
    p_corpus = np.zeros(64)
    bin_edges = np.geomspace(50.0, 8000.0, 65)
    target_bin = int(np.searchsorted(bin_edges, 1000.0) - 1)
    p_corpus[target_bin] = 1.0
    alignment = corpus_alignment_index(b, n, p_corpus, n_freq_bins=64)
    assert alignment < 0.20


def test_alignment_in_unit_interval():
    """Property check: alignment ∈ [0, 1] for any non-empty bridge set."""
    n = Nodes(max_nodes=4)
    b = Bridges(max_bridges=4)
    log_1k = float(np.log(1000.0))
    n.add(pos=(0, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    n.add(pos=(1, 0, 0), energy=1.0, freq=log_1k, born_tick=0)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    p_corpus = np.random.default_rng(42).dirichlet(np.ones(64))
    alignment = corpus_alignment_index(b, n, p_corpus, n_freq_bins=64)
    assert 0.0 <= alignment <= 1.0
```

- [ ] **Step 2: Implement `agent/flux/training_metric.py`.**

```python
"""R-8 corpus-alignment index — pure function over substrate state.

alignment = 1 − JS_divergence(p_bridge_freqs, p_corpus_log_power_spectrum) / ln(2)

Where:
  - p_bridge_freqs is the histogram of alive-bridge endpoint frequencies
    quantised to n_freq_bins log-spaced bins matching the cochlea bank.
  - p_corpus_log_power_spectrum is precomputed by agent.flux.corpus_spectrum.
"""
from __future__ import annotations
import numpy as np

LN_2 = float(np.log(2.0))


def _bridge_endpoint_histogram(bridges, nodes, n_freq_bins, freq_band_hz):
    alive = bridges.alive[: bridges.n]
    if not alive.any():
        return None
    bin_edges = np.geomspace(freq_band_hz[0], freq_band_hz[1], n_freq_bins + 1)
    log_bin_edges = np.log(bin_edges)
    hist = np.zeros(n_freq_bins, dtype=np.float64)
    src_idx = bridges.src[: bridges.n][alive]
    dst_idx = bridges.dst[: bridges.n][alive]
    freqs = np.concatenate([nodes.frequency[src_idx], nodes.frequency[dst_idx]])
    # nodes.frequency is already log-Hz per spec §5.2.
    for i in range(n_freq_bins):
        in_bin = (freqs >= log_bin_edges[i]) & (freqs < log_bin_edges[i + 1])
        hist[i] = int(in_bin.sum())
    total = hist.sum()
    if total > 0:
        hist /= total
    else:
        return None
    return hist


def corpus_alignment_index(
    bridges, nodes, p_corpus, n_freq_bins=64, freq_band_hz=(50.0, 8000.0)
):
    p_bridge = _bridge_endpoint_histogram(bridges, nodes, n_freq_bins, freq_band_hz)
    if p_bridge is None:
        return 0.0
    p_corpus = np.asarray(p_corpus, dtype=np.float64)
    # Defensive: re-normalise both.
    p_bridge = p_bridge / max(p_bridge.sum(), 1e-12)
    p_corpus = p_corpus / max(p_corpus.sum(), 1e-12)
    m = 0.5 * (p_bridge + p_corpus)
    # KL(p || m) with safe log handling
    def kl(p, q):
        mask = p > 0
        return float(np.sum(p[mask] * (np.log(p[mask]) - np.log(q[mask] + 1e-12))))
    js = 0.5 * kl(p_bridge, m) + 0.5 * kl(p_corpus, m)
    alignment = 1.0 - js / LN_2
    return float(max(0.0, min(1.0, alignment)))
```

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_training_run.py -v -k alignment`. Expect 4/4 pass.

- [ ] **Step 4: Commit** `flux training EN: corpus-alignment metric`.

---

## Task 5: training_run.py skeleton (R-7-consumer + R-8-target)

**Files:**
- Create: `agent/flux/training_run.py` (TrainingRunConfig + waveform factories + run_training_session SKELETON — the substrate-loop body remains R-8's Task)

R-6 lands the dataclass and the function signatures so R-7's corpus tests and R-8's run tests can both import a stable surface. R-6 does NOT land the substrate-loop body (that is R-8's Task per the loop discipline) — it stubs `run_training_session` to raise `NotImplementedError` for R-8 to fill in.

- [ ] **Step 1: Write the dataclass and signatures.**

```python
"""R-8 training-run orchestrator — skeleton only at R-6 time.

R-6 (this plan) lands the dataclass, the waveform factory signatures, and
the run_training_session signature so downstream tests have a stable
import surface. R-8 fills in run_training_session's substrate-tick-loop
body, mirroring agent/flux/learning_run.py::run_learning_session.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import json

import numpy as np
import soundfile as sf

from agent.flux.cochlea import CochleaConfig


@dataclass
class TrainingRunConfig:
    # Corpus
    corpus_manifest_path: Path = Path("corpus.training-EN.yaml")
    corpus_audio_root: Path = Path.home() / ".eqmod" / "training" / "EN"
    language: str = "en"
    sample_rate_hz: int = 16000

    # Substrate runtime
    n_ticks_train: int = 60_000
    seed_train: int = 74747
    seed_control: int = 74747
    seed_whitenoise: int = 99999

    # Pre-registered thresholds (locked at R-6 commit time)
    alignment_thresh_train: float = 0.50
    alignment_thresh_control: float = 0.40
    margin_min: float = 0.10
    n_bridges_min_alive_train: int = 50
    n_bridges_min_alive_control: int = 20
    n_freq_bins: int = 64
    freq_band_hz: tuple[float, float] = (50.0, 8000.0)

    # F2-locked cochlea config (inherited)
    cochlea_cfg: CochleaConfig = field(default_factory=CochleaConfig)

    # Audit tolerance
    audit_tol: float = 1e-9


@dataclass
class TrainingRunResult:
    quanta: object
    nodes: object
    bridges: object
    grid: object
    tick_index: int
    audit: object
    cfg: TrainingRunConfig


def load_corpus_audio_from_manifest(cfg: TrainingRunConfig) -> np.ndarray:
    """Concatenate the manifest's per-stage audio into one float32 16-kHz mono signal.

    Stages 1, 2, and 4-substitute are loaded in order. RMS-normalised per stage
    so loud stages don't dominate the substrate's bridge formation.

    R-7 populates the manifest with audio files; this function is the
    consumer. If a file is missing, raises FileNotFoundError (caller decides
    whether to NULL or hard-fail).
    """
    manifest_path = cfg.corpus_audio_root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"R-7 corpus manifest not found at {manifest_path}; "
            f"run R-7 first to populate the corpus"
        )
    manifest = json.loads(manifest_path.read_text())
    chunks: list[np.ndarray] = []
    for stage_name in ["stage1", "stage2", "stage4_substitute"]:
        for entry in manifest["stages"].get(stage_name, {}).get("files", []):
            audio_path = Path(entry["path"])
            audio, sr = sf.read(audio_path, dtype="float32", always_2d=False)
            if sr != cfg.sample_rate_hz:
                raise ValueError(
                    f"{audio_path}: expected sample_rate={cfg.sample_rate_hz}, got {sr}"
                )
            # Per-stage RMS normalisation
            rms = float(np.sqrt(np.mean(audio**2)))
            if rms > 1e-9:
                audio = audio / rms * 0.1   # target RMS = 0.1
            chunks.append(audio)
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)


def make_corpus_waveform(cfg: TrainingRunConfig, n_samples: int) -> np.ndarray:
    """Take the loaded corpus, loop-to-fill n_samples if necessary, return."""
    base = load_corpus_audio_from_manifest(cfg)
    if base.size == 0:
        raise ValueError("Corpus is empty — cannot build training waveform")
    if base.size >= n_samples:
        return base[:n_samples]
    reps = (n_samples + base.size - 1) // base.size
    looped = np.tile(base, reps)[:n_samples]
    return looped


def make_control_waveform(cfg: TrainingRunConfig, n_samples: int) -> np.ndarray:
    """RMS-matched gaussian white noise. Locked seed cfg.seed_whitenoise."""
    rng = np.random.default_rng(cfg.seed_whitenoise)
    # Match the corpus's per-stage-normalised target RMS = 0.1
    return (rng.standard_normal(n_samples).astype(np.float32) * 0.1)


def run_training_session(
    cfg: TrainingRunConfig, input_kind: Literal["train", "control"]
) -> TrainingRunResult:
    """Orchestrate a training or control run.

    R-6 (this plan) lands the SIGNATURE only — R-8 fills in the substrate
    tick-loop body. Copy-paste the loop from agent/flux/learning_run.py's
    run_learning_session, swapping the waveform source for make_corpus_waveform
    / make_control_waveform per input_kind.
    """
    raise NotImplementedError(
        "R-8 implements the run_training_session tick loop. "
        "Copy the loop body from agent/flux/learning_run.py::run_learning_session, "
        "substituting make_corpus_waveform / make_control_waveform for the "
        "tone-burst / white-noise generators."
    )
```

- [ ] **Step 2: Add a stub-existence test in `tests/flux/test_training_run.py`** that imports the module and asserts the dataclass + functions are importable. Do NOT call `run_training_session` (it raises NotImplementedError at R-6 time).

```python
def test_training_run_module_imports():
    from agent.flux.training_run import (
        TrainingRunConfig, TrainingRunResult,
        load_corpus_audio_from_manifest, make_corpus_waveform,
        make_control_waveform, run_training_session,
    )
    cfg = TrainingRunConfig()
    assert cfg.language == "en"
    assert cfg.sample_rate_hz == 16000
    assert cfg.n_ticks_train == 60_000
    assert cfg.alignment_thresh_train == 0.50
    assert cfg.alignment_thresh_control == 0.40
    assert cfg.margin_min == 0.10
```

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_training_run.py -v -k imports`. Expect 1/1 pass.

- [ ] **Step 4: Commit** `flux training EN: training_run skeleton (R-8 to fill loop)`.

---

## Task 6: R-8 trained-run acceptance test (the slow integration)

**Files:**
- Modify: `tests/flux/test_training_run.py` (add the full-length trained-run acceptance test, marked `@pytest.mark.slow`)

This is the pre-registered substantive proof of the training phase. R-8 lands the substrate-loop body in `run_training_session`; R-6 (this plan) lands the test that will exercise it.

- [ ] **Step 1: Add the acceptance test.**

```python
@pytest.mark.slow
def test_training_substrate_aligns_with_corpus_spectrum():
    """Pre-registered R-8 acceptance: substrate exposed to the English corpus
    develops bridge topology whose endpoint-frequency distribution is
    measurably closer to the corpus log-power spectrum than a matched-wallclock
    white-noise control. Locked thresholds — DO NOT retune."""
    from agent.flux.training_run import (
        TrainingRunConfig, run_training_session, make_corpus_waveform,
    )
    from agent.flux.training_metric import corpus_alignment_index
    from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum

    cfg = TrainingRunConfig()
    result = run_training_session(cfg, input_kind="train")
    n_alive = int(result.bridges.alive.sum())
    assert n_alive >= cfg.n_bridges_min_alive_train, (
        f"trained run produced only {n_alive} alive bridges, need "
        f">= {cfg.n_bridges_min_alive_train} for alignment to be meaningful — "
        f"verdict NULL not PASS"
    )
    waveform = make_corpus_waveform(
        cfg, n_samples=cfg.n_ticks_train * cfg.cochlea_cfg.n_audio_samples_per_tick
    )
    p_corpus = compute_corpus_log_power_spectrum(
        waveform, sample_rate_hz=cfg.sample_rate_hz, n_freq_bins=cfg.n_freq_bins,
        freq_band_hz=cfg.freq_band_hz,
    )
    alignment = corpus_alignment_index(
        result.bridges, result.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )
    assert alignment >= cfg.alignment_thresh_train, (
        f"trained substrate alignment = {alignment:.3f}, "
        f"pre-registered threshold {cfg.alignment_thresh_train:.3f} — "
        f"verdict NULL not PASS. Bridges alive: {n_alive}. "
        f"Do NOT retune thresholds; they are locked by R-6 plan."
    )
```

- [ ] **Step 2: Do NOT run the slow test at R-6 time** — R-7 (corpus) and R-8 (substrate-loop body) are not yet in place. The slow test will be exercised by R-8's postflight under a separately-budgeted item.

- [ ] **Step 3: Commit** `flux training EN: trained-run acceptance test (slow, R-8 will exercise)`.

---

## Task 7: R-8 negative-control acceptance test

**Files:**
- Create: `tests/flux/test_training_negative_control.py`

The hermetic negative-control test. Recomputes BOTH the trained and control results inside the test (using locked seeds) so it can assert the relative `margin_min` gate without depending on test ordering.

- [ ] **Step 1: Write the negative-control test.**

```python
"""R-8 negative-control acceptance.

Pre-registered by R-6 (plan docs/superpowers/plans/2026-05-17-flux-training-EN.md):

The same substrate, run for the same wallclock with the same RNG, driven
by RMS-matched gaussian white noise through the SAME cochlea, must NOT
reach the corpus-alignment threshold that the trained run reaches.
If it does, the trained-run signal is a state detector, not a learning
finding — and the training phase NULLs per the charter's negative-control rule.
"""
from __future__ import annotations
import numpy as np
import pytest

from agent.flux.training_run import (
    TrainingRunConfig, run_training_session, make_corpus_waveform,
)
from agent.flux.training_metric import corpus_alignment_index
from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum


@pytest.mark.slow
def test_control_substrate_does_not_align_with_corpus_spectrum():
    cfg = TrainingRunConfig()

    # Precompute the corpus spectrum once.
    waveform_train = make_corpus_waveform(
        cfg, n_samples=cfg.n_ticks_train * cfg.cochlea_cfg.n_audio_samples_per_tick
    )
    p_corpus = compute_corpus_log_power_spectrum(
        waveform_train, sample_rate_hz=cfg.sample_rate_hz,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )

    # Trained run
    trained = run_training_session(cfg, input_kind="train")
    n_alive_train = int(trained.bridges.alive.sum())
    assert n_alive_train >= cfg.n_bridges_min_alive_train, (
        f"trained baseline produced only {n_alive_train} alive bridges; "
        f"cannot evaluate the negative control if the trained substrate "
        f"itself failed to form structure — verdict NULL"
    )
    alignment_train = corpus_alignment_index(
        trained.bridges, trained.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )

    # Negative control (matched wallclock, white noise, same seed)
    control = run_training_session(cfg, input_kind="control")
    n_alive_control = int(control.bridges.alive.sum())
    assert n_alive_control >= cfg.n_bridges_min_alive_control, (
        f"control run produced only {n_alive_control} alive bridges — "
        f"control failed to function as a control (silent-pass risk) — "
        f"verdict NULL not PASS"
    )
    alignment_control = corpus_alignment_index(
        control.bridges, control.nodes, p_corpus,
        n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
    )

    # Pre-registered absolute upper bound on control's alignment
    assert alignment_control < cfg.alignment_thresh_control, (
        f"control substrate alignment = {alignment_control:.3f} >= "
        f"{cfg.alignment_thresh_control:.3f}. The substrate aligns "
        f"with the corpus spectrum even from flat-spectrum input — "
        f"the trained-run metric is a state detector, not a learning "
        f"signal. Verdict NULL per autopilot charter."
    )
    # Pre-registered relative margin
    margin = alignment_train - alignment_control
    assert margin >= cfg.margin_min, (
        f"trained − control margin = {margin:.3f} < "
        f"{cfg.margin_min:.3f}. Trained may have crossed its floor only "
        f"because control drifted close to it; the separation is not "
        f"significant. Verdict NULL."
    )
```

- [ ] **Step 2: Do NOT run the slow test at R-6 time** — R-7 + R-8 must complete first.

- [ ] **Step 3: Commit** `flux training EN: negative-control acceptance test (slow, R-8 will exercise)`.

---

## Task 8: Verify the meta-test `test_research_plan_structure.py` passes

The plan-shape meta-test in `tests/test_research_plan_structure.py::test_training_EN_plan_exists_and_well_formed` is the R-6 acceptance gate. R-6's session must run it and confirm green before commit.

- [ ] **Step 1: Run** `uv run pytest tests/test_research_plan_structure.py::test_training_EN_plan_exists_and_well_formed -v -m slow`. Expect 1/1 pass.

- [ ] **Step 2: Run** `uv run pytest -m "not slow"` to confirm no regression in the fast slice.

- [ ] **Step 3: Commit (if any fixups)** `flux training EN plan: meta-test gate green`.

---

## Task 9: README + phase-log + queue handoff

**Files:**
- Modify: `README.md` (one-line status update)
- Modify: `docs/flux/phase-log.md` (R-6-close entry naming the locked thresholds + the R-7/R-8 acceptance handoff)

- [ ] **Step 1: README status line:**

```
Status as of 2026-05-17: F0 + F1a + F1b + F1c + F2 complete; F3 R-5 NULL (synthetic-tone probe within budget did not produce structure-level signal — implementation preserved on main). Training-EN plan (R-6) pre-registers Stages 1+2 + Stage 4 substitute (MIT OCW) + matched-wallclock white-noise control + corpus-alignment-index metric. R-7 corpus-build and R-8 run-and-falsify are next in the queue.
```

- [ ] **Step 2: Phase-log R-6-close entry:** task summary, locked threshold table, the four pre-registered pytest paths, the deferred items (Stage 3, Tier-1 LLR).

- [ ] **Step 3: Commit** `flux training EN plan: R-6 close (README + phase-log)`.

---

## Notes for autonomous execution

- **R-5 NULLed, and R-8 may also NULL — that is the intended fail-shut behavior.** The QUEUE.yaml header comment for items R-6/R-7/R-8 says so explicitly: "Training phase: only meaningful if R-5 (F3 learning) actually passed. If F3 NULLed, these items will themselves NULL (their pytest targets depend on the learning layer being live). That is the intended fail-shut behavior." This plan does NOT attempt to retune R-5's failure away. It runs the next-larger probe (real speech, more ticks, broadband metric) on the same §5.5 plasticity rule and lets the rule succeed or NULL on its own. A NULL R-8 is itself a finding: it tells the post-vacation reviewer whether the gap is in `n_ticks_train` (too short — R-8 may sweep within its 3-call budget), in the metric (corpus-alignment is the wrong probe), or in the rule itself (spec §11: the binding rule is reconsidered, not the thresholds).
- **The matched-wallclock negative control is mandatory.** Per the autopilot charter and per `marker_protocol.md`: a substrate-level finding without a passing negative control is a state detector, not a finding. R-8's two test files (`test_training_run.py` and `test_training_negative_control.py`) are both pre-registered acceptance, and R-8 PASSES only when both pass on the same `TrainingRunConfig`.
- **NULL is a valid R-8 outcome.** If the substrate as-built cannot reach `alignment_train >= 0.50` AND `alignment_control < 0.40` AND `margin >= 0.10` within `n_ticks_train_max = 120_000` (3 sweeps max), the correct outcome is NULL with a postmortem describing whether the gap is in the implementation, the hypothesis, or the metric. Do NOT retune `alignment_thresh_train`, `alignment_thresh_control`, `margin_min`, `n_freq_bins`, or `freq_band_hz` after seeing run results. Those numbers are locked the moment this plan commits.
- **Pre-registration is enforced.** Thresholds in this plan are the falsifier. The pre-commit hook in `.eqmod/autopilot/CHARTER.md` blocks edits to `preregistered_acceptance:` blocks in `QUEUE.yaml` once a session starts; the thresholds in *this plan file* are protected by protocol (charter §1: "If a test fails, the verdict is NULL or FAIL — not 'loosen the threshold.'"). R-7 and R-8 must not edit this plan's threshold table.
- **The fixed cochlea is a feature, not a limitation.** Spec §5.6: the cochlea is the minimal pre-installation we accept — analogous to biological hair cells. R-8 does NOT learn the cochlea bank. If the trained substrate fails because the bank is mis-tuned for English speech, that is an F2 question and R-8 escalates as a hard architectural blocker (it does not adapt the bank).
- **No retuning of F1b / F1c / F2 / F3 configs.** Binding, plasticity, decay, thermal, cochlea, synthesis, and the F3 plasticity-rule parameters (γ, λ, flux_min) are FROZEN as the upstream items closed them. R-8 reads those values from a single source (`agent/flux/training_run.py::TrainingRunConfig` defaults) but does not modify them.
- **One sweep, one phase-log entry.** Per the F1a/F1b/F1c/F2 protocol every sweep in R-8 must be logged in `docs/flux/phase-log.md` with: name of swept variable (only `n_ticks_train` is allowed), old value, new value, measured `alignment_train`, measured `alignment_control`, measured `margin`, decision (keep / revert).
- **R-8 reuses R-5's loop infrastructure.** `agent/flux/learning_run.py::run_learning_session` already contains the tick-loop body that R-8 needs. R-8 copy-pastes that loop into `run_training_session` and swaps the waveform source — this is a deliberate copy rather than a refactor, because mid-vacation refactor risk outweighs DRY gain. The R-5 NULL did not invalidate the loop infrastructure; it found that the synthetic tone-burst probe did not produce a structure-level signal within the 10 000-tick budget. The loop itself runs cleanly to ≥ 10 000 ticks with the substrate audit balanced (the smoke tests on `tests/flux/test_learning.py` confirm this).
- **Corpus licensing.** All R-7 sources are either public-domain (LibriVox) or CC-licensed (MIT OCW CC-BY-NC-SA; CC-licensed YouTube channels). The corpus manifest records the licence string per source. EQMOD's research-non-commercial use of CC-BY-NC-SA material is consistent with the project's MIT-code / CC-BY-SA-docs licence regime.
- **Stage 4 substitute is mandatory and acoustically distinct from Stages 1+2.** The user instruction (2026-05-13 23:38) delegated substitution because the user is on vacation and cannot record their own voice. The MIT OCW commitment satisfies the substitution by introducing a third acoustic class (classroom-recorded didactic speech) that differs from Stage 1 (studio-recorded literary narration) and Stage 2 (home-studio conversational YouTube) along at least three measurable spectral / temporal features (reverb tail, consonant density, pause-cluster statistics). Without Stage 4 the substrate hears three audiobook narrators, which weakens R-8's claim that the substrate has aligned to *English speech in general* rather than to *one studio recording style*.
- **Avoid silent-pass.** Both `n_bridges_min_alive` guards (≥ 50 trained, ≥ 20 control) FAIL the test if the substrate produces too few bridges to compute a meaningful metric. A run with zero alive bridges is NOT a pass.
- **If R-7 cannot fetch sources within budget**, R-7 NULLs and R-6's plan remains valid for the next vacation cycle. The plan does not depend on R-7 succeeding on the first try.
