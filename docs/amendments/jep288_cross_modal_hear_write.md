# JEP-288 — cross-modal grounding: 'hear A' <-> 'write A' (per Michael: "when it hears A it links it to written A")

Pre-registered 2026-06-05 (BEFORE the run). Michael: "when it hears 'A' it can link it to the written letter 'A'."
JEP-287 built the modality-agnostic hook (prototypes keyed by (modality, symbol)). This BET demonstrates the actual
HEAR<->WRITE binding: the engine grounds letters in TWO senses — SIGHT (written-letter images) and SOUND (synthesized
per-letter audio: real waveform synthesis + FFT features, NOT real recordings, NOT AI) — bound to the SAME symbols,
and shows cross-modal transfer: hearing a letter retrieves its symbol AND its written form.

## Method (no transformer / no pretrained model)
- SIGHT: centred written-letter images A-Z (as JEP-287). SOUND: each letter -> a distinct deterministic 3-formant
  tone (sum of 3 sine waves at letter-specific frequencies) over 0.2s; the 'heard' feature = log-FFT magnitude
  (32 bins) + noise. Both are real signals + real feature extraction.
- The engine (ActiveLearner) is TAUGHT both modalities bound to the same symbols. Tests:
  - within-sound recognition: hear a held-out sound -> correct symbol.
  - CROSS-MODAL recall: hear 'A' -> its symbol -> retrieve the WRITTEN 'A' prototype; check the retrieved visual
    prototype is the one whose nearest test-image is actually an 'A' (sound -> symbol -> sight).
  - the shared symbol unifies them: the set of symbols grounded by sound == the set grounded by sight.
- Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J288a | It HEARS letters | held-out sound recognition accuracy >= 0.90 over A-Z (both seeds) |
| J288b | hear<->write share ONE symbol | for every letter, the sound-modality symbol == the write-modality symbol (the binding is to the same symbol, not two) (both seeds) |
| J288c | CROSS-MODAL recall works | hearing a letter's sound retrieves the correct WRITTEN prototype (sound -> symbol -> sight) for >= 0.90 of letters (both seeds) |
| J288d | Transfer: name learned in EITHER sense | a symbol taught only by SOUND is then recognized by SIGHT after one written example, and vice versa (demonstrated) |

PASS = J288a-c -> the engine HEARS letters and links them to the WRITTEN letters via a shared symbol (Michael's
hear<->write link). NULL (honest): J288a fails -> the synthesized sounds aren't separable by FFT features (unlikely,
they're distinct by construction); J288c fails -> the cross-modal retrieval doesn't bind. No post-hoc tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 J288a PASS (~0.98+: the per-letter formant tones are distinct by construction -> FFT features separate cleanly).
J288b PASS (the (modality, symbol) store binds both senses to the SAME 26 symbols by construction -> sets equal).
J288c PASS (sound -> argmax symbol -> that symbol's written prototype; since both are grounded correctly, the
retrieved visual prototype is the right letter >= 0.90). J288d demonstrated. NET: 'hear A' and 'write A' ground ONE
'A' -- the cross-modal link Michael described, on real (synthesized) audio. HONEST scope: synthesized tones stand in
for speech (no microphone/real-speech data, no pretrained audio model); the contribution is the cross-modal binding +
its demonstration, ready for real audio to drop into the same (modality, symbol) store. Established (multi-modal
prototype grounding, FFT features, cross-modal retrieval), named; no novelty -- the value is the demonstrated hear<->write link.

## RESULT (2026-06-05): PASS — the engine HEARS letters and links them to the WRITTEN letters (shared symbol)

| seed | hear acc | same symbol set | cross-modal recall (hear->write) | transfer (ear->eye) |
|------|----------|-----------------|----------------------------------|----------------------|
| 42 | 1.00 | True (26/26) | 0.962 | True |
| 7  | 1.00 | True (26/26) | 1.00 | True |

- **J288a ✓** — it HEARS letters: held-out synthesized-sound recognition = 1.00 (distinct per-letter formant tones,
  FFT features). The engine has a second sense.
- **J288b ✓** — hear and write ground the SAME symbol set (26 sound, 26 write, all A-Z): the binding is to ONE 'A',
  not two unrelated things.
- **J288c ✓** — CROSS-MODAL recall: hearing a letter -> its symbol -> retrieves the correct WRITTEN prototype, 0.96-1.00.
  Hearing 'A' brings up the written 'A'. The hear<->write link Michael described.
- **J288d ✓** — TRANSFER: a letter taught only by EAR is then recognized by SIGHT after one written example (and vice
  versa) — because both senses share the symbol, knowledge crosses modalities.

**Calibration note:** the first cut FAILED J288a (hear-acc 0.25) — my FFT binning was STRIDED (every-nth bin) instead
of CONTIGUOUS frequency bands, scrambling the formant structure. Fixed to contiguous bands -> 1.00. (The flagged
feature-separability risk, materialized in the feature extraction, not the signal.)

**FINDING (per Michael's steer):** 'hear A' and 'write A' ground ONE symbol 'A' — the engine perceives letters through
TWO senses and links them, on real (synthesized) audio signals + real FFT features, no transformer / no pretrained
audio model. Combined with JEP-287 (the ask-when-unsure teacher loop + GUI), the slow grounded-learning foundation is
in place: a learner that grounds symbols from a teacher across SIGHT and SOUND, querying only when unsure. HONEST
scope: synthesized tones stand in for speech (no microphone / real-speech / pretrained audio); the contribution is the
demonstrated cross-modal binding, ready for real audio to drop into the same (modality, symbol) store. NEXT: real
audio input (microphone) into the teach GUI; words after letters; richer no-pretrained visual features for harder
classes. Verdict: PASS (predict-calibrate HIT — hear 1.0, shared symbols, cross-modal recall 0.96, transfer, all as
forecast after the FFT-binning fix). Established (multi-modal prototype grounding, FFT features, cross-modal retrieval),
named; no novelty — the value is the demonstrated hear<->write link.
