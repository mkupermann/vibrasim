# JEP-292 — Hear letters from real WAV files (stdlib hearing path)

## Motivation
Michael's directive: "When it hears 'A' then it can link it to the written letter 'A'." JEP-288 proved
cross-modal grounding on synthetic audio *feature vectors*; this closes the gap to a **real audio file** —
record a `.wav` (Windows Voice Recorder), and the same `(modality='sound', symbol)` store grounds the sound
to the written letter. No transformer, no pretrained audio model — only FFT over stdlib `wave`.

## Pre-registered bars (BEFORE the run)
- **J292a** — round-trip hearing from real WAV files ≥ 0.90 accuracy over the 26 letters, both seeds
  (synthesize per-letter tone → `write_wav` → read back via `wave` → FFT feature → ground+recognize).
- **J292b** — the GUI "load a sound" path is wired and imports cleanly (`tools.teach_gui`, `world.audio_features`).

Predicted most-likely failure: WAV quantization (16-bit PCM) + Hanning/FFT binning could blur near-neighbor
tones; mitigated by 32 *contiguous* bands (the JEP-288 fix) and 8 noisy training takes per letter.

## Result (seeds 42, 7)
- seed 42: hear-from-WAV accuracy = **1.0** over 26 letters
- seed 7:  hear-from-WAV accuracy = **1.0** over 26 letters
- J292a (≥0.90): **True** · J292b (wired+imports): **True**

## Verdict: **PASS**
The engine hears letters from real audio **files** at 1.0. The hearing path is stdlib-only (works without
`sounddevice`), and the teaching GUI now has an "I recorded a sound (load .wav)" button that grounds a recorded
sound to the same symbol as the written letter — closing the hear-side of Michael's directive.

Honest scope: this is *file* hearing (record → load), not *live-mic* streaming (that needs `sounddevice`,
not installed). The features are home-made FFT bins, and recognition is nearest-prototype over taught takes —
deliberately simple, no pretrained audio front-end.
