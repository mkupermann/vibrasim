# Predictive babble — operational guide

This document explains how to run the predictive-babble pipeline (G19, 2026-05-10) end-to-end. The scientific design is in [`docs/superpowers/specs/2026-05-10-predictive-babble-design.md`](superpowers/specs/2026-05-10-predictive-babble-design.md). Read that first if you want the *why*. This file is the *how*.

## What it does, in one paragraph

Four substrates run in sequence: a trained one, exposed to a four-stage German curriculum, and three controls (white noise, time-reversed German, French) that run with matched wall-clock per stage. After convergence, each substrate is asked to babble — its `audio_input` is gated off, its `audio_output` port is read for several minutes of firings, and those firings are decoded back into a wav. The four wavs go to an evaluator that computes MFCC-histogram KL-divergence against held-back German speech. Verdict is binary: **PASS** (trained beats every control by ≥ 2 σ on bootstrap), **FAIL** (trained statistically indistinguishable from white noise), **NULL** (one or more controls inconclusive — reported faithfully, not rationalised).

## Two run modes

### `--mini` — pipeline correctness

```bash
python -m agent.run_babble_experiment --mini
```

Runs in ~17 s on a normal laptop. Generates four 2 sec synthetic audio streams in memory, runs the entire pipeline (corpus → 4 substrates → babble → evaluator → verdict), produces 4 wav files in `~/.eqmod/babble/mini/{trained_de,white_noise,reversed_de,french}/babble.wav` plus `~/.eqmod/babble/mini/result.json`.

**This is the integration test, not the science test.** With 1 s of synthetic 3-tone audio per substrate and no real training, the wavs are typically silent and the verdict is FAIL. That's expected — `--mini` proves the plumbing, not the result.

### `--config` — the real run

```bash
python -m agent.run_babble_experiment --config corpus.yaml --out ~/.eqmod/babble/run-1/
```

This is the 24-hour scientific acceptance run. Requires real corpus URLs in a YAML config, real wall-clock, and (for stage 4) a webcam recording you make yourself.

## YAML config schema

```yaml
# corpus.yaml
de:
  stage1:                                   # Audiobook narrator(s) — 60+ min
    - "https://librivox.org/..."
    - "/path/to/local-audiobook.mp3"
  stage2:                                   # Single YouTuber — 120+ min
    - "https://www.youtube.com/watch?v=..."
  stage3:                                   # Multi-speaker podcasts — 180+ min
    - "https://example.com/podcast1.mp3"
    - "https://example.com/podcast2.mp3"
  stage4:                                   # Your webcam recording, single file
    - "/path/to/my-recording.wav"
fr:
  sources:                                  # French of equal total duration
    - "https://librivox.org/french-..."
seed: 0

# Production defaults (per spec §6)
n_clusters: 256
n_bootstrap: 100
babble_duration_seconds: 300.0              # 5 min wav per substrate

# Production defaults (per spec §3 and AutonomousLoopConfig)
awake_seconds_per_cycle: 30.0
dream_seconds_per_cycle: 10.0
expected_min_cycles_per_stage: 50
perplexity_eval_interval_cycles: 10
perplexity_eval_duration_seconds: 30.0
snapshot_every_seconds: 1800.0              # 30 min sim time

# Convergence detector defaults
convergence_window_size: 10
convergence_min_improvement: 0.01
convergence_min_history: 20
```

For a fast synthetic-corpus demo (sub-90 sec wall-clock) — drop everything by 30–60×:

```yaml
n_clusters: 16
n_bootstrap: 20
babble_duration_seconds: 0.5
awake_seconds_per_cycle: 0.5
dream_seconds_per_cycle: 0.2
expected_min_cycles_per_stage: 2
perplexity_eval_interval_cycles: 1
perplexity_eval_duration_seconds: 0.3
convergence_window_size: 1
convergence_min_history: 2
```

## What gets produced

After a run completes, `--out` contains:

```
{out}/
  state.json                               # Resume state, advisory
  result.json                              # The final verdict + bootstrap stats
  reference.wav                            # Held-back DE test split as wav
  corpus/
    {de,white_noise,reversed_de,fr}/
      train.f32.raw                        # Concatenation of all 4 stages, 80% split
      dev.f32.raw                          # 10% — used for perplexity eval
      test.f32.raw                         # 10% — used only by the evaluator
      stage1_train.f32.raw .. stage4_train.f32.raw  # Per-stage 80% splits
      manifest.json
  metrics/
    {trained_de,white_noise,reversed_de,french}.csv  # Per-cycle metrics
  snapshots/
    {substrate}/autonomous_cycle_NNNNNN.npz          # Every 30 min sim time
  babble/
    trained_de.wav                         # 5 min babble (default)
    white_noise.wav
    reversed_de.wav
    french.wav
```

## Reading `result.json`

```json
{
  "verdict": "PASS" | "FAIL" | "NULL",
  "null_against": ["white_noise", ...],   // controls where evidence inconclusive
  "trained_kl_mean": 1.2034,
  "trained_kl_std": 0.0421,
  "control_kl": {
    "white_noise":  [3.421, 0.089],       // [mean, std]
    "reversed_de":  [2.189, 0.067],
    "french":       [2.974, 0.072]
  },
  "z_scores": {
    "white_noise":  24.31,                 // (control.mean - trained.mean) / sqrt(trained.std² + control.std²)
    "reversed_de":  9.84,
    "french":       18.45
  },
  "n_frames_per_substrate": {"trained": 30000, ...},
  "n_bootstrap": 100
}
```

- **PASS:** every z-score ≥ 2 AND `trained_kl_mean` < every `control_kl[X][0]`.
- **FAIL:** z-score against `white_noise` ≤ 0 — trained is no better than noise.
- **NULL:** anything else. `null_against` lists which control(s) were inconclusive.

The verdict is computed once with frozen parameters. We do not iterate or re-run to nudge it. PASS, NULL, and FAIL are all real outcomes — a NULL on one control is a finding, not a failure.

## Resumability

If the run crashes or you Ctrl-C it, the next invocation with the same config + out_dir will read `state.json` and skip already-completed substrates. State is best-effort, not transactional — if you killed the process mid-cycle, the corresponding substrate's last-saved snapshot is the resume point.

## Known caveats

1. **Substrate saturation on noisy audio.** The `CorpusAudioFeeder` caps emissions per inject call at `max_vibrations_per_inject = 256` by default. Without this cap, white-noise and multi-speaker audio fill `n_nodes_max = 4096` atoms within a few cycles and physics tick scales O(N²); a single awake phase ends up taking 30+ minutes. The cap retains rich spectral information for clean audio while bounding the worst case for noisy audio. Set to 0 only for debugging.

2. **In-memory state snapshot is a parallel implementation.** Dev-split perplexity evaluation snapshots the full mutable World state in-memory (per-array `.copy()`) before injecting dev audio, then restores after. This works around `world/snapshot.py:save_snapshot` not persisting `k_pattern_id`, `k_eligibility`, the slot-recycling free-list, the self-model, the workspace state, etc. If `World` gains new mutable fields in the future, dev evaluation will silently leak state. Fix `world/snapshot.py` if/when this matters.

3. **`_NO_SIGNAL_PERPLEXITY` sentinel.** When the substrate hasn't fired in `audio_input` yet, perplexity evaluation returns 1e6 instead of `inf`. `inf - inf = NaN` would break the convergence detector's plateau math. The 1e6 sentinel lets stages advance even when the substrate is silent (the matched-wallclock control path needs this), and gets dwarfed correctly when real signal arrives (real perplexity < 100 → "improving, not plateaued").

4. **Synthetic corpora produce silent babble.** With short stages of synthetic tones and an 8-cycle minimum stage, the substrate's `audio_output` port doesn't develop firings — the babble wav is silence. This is honest: real phonological learning requires real corpora and substantial training. The `--mini` and synthetic-config runs are pipeline tests, not scientific tests.

5. **Stage 4 closed-loop hazard.** During webcam-live exposure, the substrate's `audio_output` is gain-gated to zero by the babble runner's design (output is only opened during the explicit babble phase). The substrate listens to you; it does not echo back during training. This prevents runaway feedback while preserving the perception–production loop semantically.

## What you need to launch a real run

1. **A `corpus.yaml`** with real source URLs for all four DE stages plus a French source list. The CorpusBuilder uses `yt-dlp` for YouTube/SoundCloud and direct ffmpeg for `https://...mp3` and local file paths.
2. **A stage-4 webcam recording.** ~30 minutes of you talking, in the same language as the trained corpus (German). Save as `.wav` or `.mp4`; CorpusBuilder will normalise.
3. **A laptop with sleep mode disabled** for 24+ hours. The pipeline runs serially across the four substrates; matched-wall-clock means each control eats the same per-stage wall-clock as the trained substrate.
4. **Disk space.** Per-substrate corpus ≈ 3–4 GB at 6 hours × 16 kHz × float32 × 4 splits. Plus snapshots every 30 min. Plan for 20+ GB total per run.
5. **A pre-registered acceptance criterion.** This is the spec §6 verdict. Do not edit the verdict logic between runs.

## How to run

```bash
# Generate / fetch your corpus.yaml first.
# Then:
caffeinate -dis python -m agent.run_babble_experiment \
  --config corpus.yaml \
  --out ~/.eqmod/babble/run-$(date +%Y%m%d-%H%M)/

# In another shell, tail the metrics CSVs:
ls ~/.eqmod/babble/run-*/metrics/*.csv
```

`caffeinate -dis` keeps the laptop awake. The run produces a stream of per-cycle metrics CSVs you can plot live. When all 4 substrates finish babbling and the evaluator runs, `result.json` is written and the process exits 0.

## See also

- Spec: [`docs/superpowers/specs/2026-05-10-predictive-babble-design.md`](superpowers/specs/2026-05-10-predictive-babble-design.md)
- Build retrospective: [`LOGBOOK.md`](../LOGBOOK.md) — `## 2026-05-10 — Predictive babble pipeline (G19)`
- Tests: `tests/test_corpus_builder.py`, `tests/test_decoder_audio.py`, `tests/test_audio_predictor.py`, `tests/test_curriculum_scheduler.py`, `tests/test_corpus_audio_feeder.py`, `tests/test_babble.py`, `tests/test_evaluate_babble.py`, `tests/test_babble_integration.py`
