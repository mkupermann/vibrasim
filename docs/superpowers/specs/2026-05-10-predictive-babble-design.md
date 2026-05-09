# Predictive Babble — Design Spec

**Status:** Draft, awaiting review
**Date:** 2026-05-10
**Goal:** Extend the EQMOD substrate from a self-modelling autopoietic loop with no external input into one that learns the phonological distribution of a natural language from raw audio, then produces speech-like utterances ("babble") in that language without labels or semantic supervision.

This spec is the result of a brainstorming pass. The acceptance test is binary and pre-registered. Components are scoped to one purpose each, mostly new, with one minimal change to the existing autonomous loop.

---

## 1. Locked decisions

| # | Decision | Value |
|---|---|---|
| 1 | Goal | Predictive babble. No labels, no semantics. Substrate produces speech-like utterances in the trained language's phonology. |
| 2 | Training source | Four-stage curriculum: audiobook narrator → single YouTuber → multi-speaker podcasts → webcam live (user's voice). |
| 3 | Language | German only for the trained substrate. |
| 4 | Babble trigger | Convergence-based. Listen silently until held-out audio-prediction perplexity plateaus for K consecutive evaluation cycles, then switch to babble-only mode. |
| 5 | Falsifier battery | Three controls run in parallel: white-noise, time-reversed German, French. All four substrates produce babble; trained must beat all three on the acceptance metric. |

These were settled by clarifying questions during brainstorming. Reopening any of them resets the design.

---

## 2. Architecture

Four substrates run the autonomous loop simultaneously. Each receives a different audio stream of equal total duration. All four advance through the curriculum on a matched schedule. When the trained substrate's perplexity plateaus, all four switch to babble mode. The evaluator scores all four babble outputs against held-out German.

```
[corpus_builder] → 4 streams (DE / noise / DE-reversed / FR) + held-out DE eval
                       │
                       ▼
       ┌───────────────┴───────────────┐
4 × [autonomous_loop + audio_predictor + YouTubeFeeder]
                       │
                       ▼
              [convergence_detector]
                       │
                       ▼
4 × [babble runner + decoder_audio]  →  4 × .wav
                       │
                       ▼
            [evaluator → KL-divergence report]
                       │
                       ▼
                PASS / FAIL / NULL
```

---

## 3. Components

Each component owns one file and one responsibility. New unless noted.

| File | Responsibility |
|---|---|
| `agent/corpus_builder.py` | Source from stage URLs (yt-dlp, LibriVox), normalise to 16 kHz mono float32, build the three control streams (white-noise, time-reversed German, French of equal duration), split 80/10/10 into train / dev / test. Train feeds the substrate. Dev is used by the convergence detector for perplexity (so plateau detection does not overfit the final test). Test is held back until the acceptance run in §6 and used nowhere else. |
| `agent/curriculum_scheduler.py` | Advance each substrate through the four stages. Trained substrate advances on perplexity plateau; controls advance on schedule matched to the trained substrate's wall-clock per stage. |
| `world/audio_predictor.py` | Extends the existing `self_aware` machinery with audio-pattern next-step prediction. The prediction target is the next pattern_id firing in the audio_input port, not the next raw audio sample. The metric is categorical cross-entropy / perplexity over the substrate's predicted pattern_id distribution against the actual next-firing pattern_id, evaluated on the **dev split** every K cycles. |
| `agent/decoder_audio.py` | Inverse of `agent/encoder_audio.py`: read atom firings in audio_output port → STFT bin activations → ISTFT waveform. |
| `agent/babble.py` | Run the substrate with input gated off; sample audio_output activations; convert via `decoder_audio` to a wav file of fixed duration (default 30 s). |
| `agent/convergence.py` | Track windowed perplexity. Trigger stage advance when perplexity stops improving over the last K cycles (default K=10). Trigger babble mode when stage 4 also plateaus. |
| `agent/run_babble_experiment.py` | Top-level driver. Spawn four substrates, run the pipeline end-to-end, log to disk, produce final report. |
| `agent/evaluate_babble.py` | Compute MFCC-distribution KL-divergence between each substrate's babble wav and the held-out German eval set. Produces the binary PASS/FAIL/NULL result per §6. |
| `agent/youtube_feeder.py` | Reused unchanged. |
| `agent/autonomous_loop.py` | One change: accept an optional `audio_io` parameter. When set, the awake phase pulls audio from it instead of running on pre-seeded engrams alone. |

---

## 4. Critical design decisions baked in

**Audio prediction at the pattern scale, not the sample scale.** The substrate predicts which pattern_id will fire next in the audio_input port, on the order of 100 ms granularity (phoneme-scale). Sample-rate prediction is infeasible at 4096 nodes; pattern-scale prediction is what BTSP's 2 sec eligibility tau was designed for.

**Stage 4 closed-loop hazard, gated.** During webcam live exposure, the substrate's audio_output gain is forced to zero. It listens to the user's voice; it does not echo back. Output gain only opens after convergence triggers babble mode. This prevents runaway feedback while preserving the self-prediction loop semantically.

**Controls advance on matched schedule, not their own perplexity.** Otherwise the white-noise control will never advance and we cannot compare babble at matched training duration. Each control eats the same wall-clock per stage as the trained substrate.

**Stage 3 is the genuine generalisation test.** Multi-speaker phoneme abstraction at 4096 nodes may fail. If it does, the result is reported as "single-speaker bound at this scale" — a real finding, not a failure to hide.

**No silent-pass eval paths.** The evaluator handles edge cases (substrate produces silence, output frequencies out of band, NaN MFCCs) with explicit assertions. Reference: prior F3b silent-pass bug in this project.

---

## 5. Data flow per evaluation cycle

1. Awake phase: substrate pulls one block of audio from its assigned source via `YouTubeFeeder` → `AudioIO` → atom firings in audio_input port.
2. Tick loop: BTSP, workspace, self-prediction, self-modify all run as before. `audio_predictor` records prediction error against the next-pattern target.
3. Dream phase: existing replay + concept-blending machinery runs; new audio pattern_ids may emerge as proto-phonemes.
4. Every K cycles: substrate is evaluated against the held-out German set (each substrate against the same set, even controls). Perplexity is logged.
5. Convergence detector inspects the trained substrate's perplexity series. On plateau, advances stage. After stage 4 also plateaus, triggers babble mode for all four.
6. Babble mode: input gated off, output gain raised, 30 s of audio_output → wav per substrate.
7. Evaluator runs once on the four wav files.

---

## 6. Acceptance criterion (the falsifier)

Pre-registered, not retrofitted.

After the curriculum runs, each substrate produces a single 5-minute babble wav. From each wav we extract MFCC frame vectors at 10 ms hop and build a histogram in MFCC space (k-means quantisation to 256 bins, codebook fit on the held-back **test split** of the held-out German set). Compute KL-divergence between each substrate's MFCC histogram and the test-split histogram. To estimate variance, bootstrap-resample 100 times over MFCC frames within each wav (not 100 separate babble runs).

- **PASS:** trained substrate's mean KL is lower than every control's mean KL by ≥ 2 standard deviations.
- **NULL on any control:** if the trained substrate fails to beat one specific control, the result is reported as null for that ablation. Not rationalised, not retrofitted, not iterated to make it pass.
- **FAIL:** trained substrate is statistically indistinguishable from the white-noise control. Substrate is not learning audio-distributional structure at this scale.

This addresses the persona-review concern flagged in project memory: tests must not be calibration definitions ("iterate parameters until F1 holds"). Here, parameters are frozen before the run; the result is whatever falls out.

---

## 7. Risks (named, not hidden)

1. **Convergence at 4096 nodes is uncertain.** Multi-speaker stage 3 is the most likely point of failure. The risk is not catastrophic — a single-speaker-only result is still publishable as a scope finding.
2. **Inverse-encoder fidelity floor.** STFT → atom firings → ISTFT is lossy. Even a perfect predictor may sound muffled. Roundtrip RMS test in unit tests quantifies the floor before the full run.
3. **Total compute.** Roughly six hours of audio × four substrates with realtime pacing ≈ 24 hours wall-clock. Single MacBook session with sleep mode disabled. Snapshots every 30 min for crash resumability.
4. **F3b-style silent-pass bugs in the new evaluator code.** Mitigation: explicit assertions, unit tests on edge cases (silence, NaN, out-of-band frequencies).
5. **Stage 4 webcam logistics.** Requires the user to spend time talking into the mic. Mitigated by allowing stage 4 to be a recorded session played back, not necessarily live.

---

## 8. Testing strategy

**Unit tests**
- `corpus_builder` produces four streams of equal duration at 16 kHz mono float32.
- Time-reversal preserves power spectrum within 1 % bin-by-bin.
- Inverse encoder roundtrip: encode(audio) → decode(firings) reconstructs STFT-domain audio with RMS error ≤ 10 %.
- Convergence detector fires correctly on synthetic perplexity series (monotone-decreasing, plateau, oscillating).

**Integration test**
- A 60 sec mini-curriculum (one short clip per stage, shrunk control corpora) runs end-to-end and produces four wav files. Tests pipeline correctness, not science. Must complete under 5 min.

**Acceptance test**
- The full falsifier in §6. This is the only test that adjudicates the scientific claim.

---

## 9. Out of scope (v2)

- Visual co-prediction (Approach B from brainstorming). Audio-only is v1.
- Multilingual (DE + EN). Single language is v1.
- Word-level or compositional grounding. Sub-second phonological structure is v1.
- Conversational turn-taking. Listen-then-babble is v1; dialogue is not.
- TTS-quality output. Babble may sound coarse. Acceptance is statistical distribution-match, not naturalness.

---

## 10. Implementation order (high level)

For the writing-plans skill to expand:

1. `corpus_builder` + unit tests (no substrate touched).
2. `decoder_audio` + roundtrip unit test (no substrate touched).
3. `audio_predictor` extension + minimal change to `autonomous_loop` to accept `audio_io`.
4. `convergence` + `curriculum_scheduler` + `babble` runner.
5. `evaluate_babble` + `run_babble_experiment` driver.
6. Mini-curriculum integration test green.
7. Full curriculum acceptance run.

Steps 1–2 produce something testable independent of the substrate, which de-risks the whole design.
