# JEP-447 — The substrate HEARS a sound and feels its energy (real-audio perceptual affect)

## Motivation
JEP-446 grounded affect in synthetic perceptual features. JEP-447 takes the natural next step flagged
there: REAL sensory input. Using the repo's audio pipeline (`world/audio_features.py`: synthesize a
waveform → log-FFT feature), the energy model predicts the affective valence of an actual SOUND from
its real spectral features — harsh/noisy/dissonant = dark, clean/consonant = bright (established
psychoacoustics: dissonance and noise are perceived as unpleasant). The strong claim: this affect
generalizes to sounds with a NOVEL fundamental (an "object" never heard) — the substrate feels a
sound's energy from acoustics, independent of recognizing it. Established methods (FFT features +
reservoir/RLS), named. No transformer.

## Method (`tools/run_jep447_audio_perceptual_affect.py`)
Each sound = a fundamental f0 (the "object" identity) + an overtone + noise:
- **bright (+1):** consonant overtone (perfect fifth, 1.5·f0), low noise (0.01).
- **dark (−1):** dissonant overtone (minor second, 1.06·f0 — beating) + high noise (0.15).
Waveform via `synth_tone`, feature via `samples_to_feature` (real log-FFT). Train the energy model on
f0 ∈ {220,247,262,294,330} Hz (musical notes); test on held-out renderings of those AND on NOVEL
fundamentals {175,392,440} Hz never heard in training. Seeds 0 & 7; ~300 train / 150 test.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J447a (hears affect from real FFT):** energy valence accuracy on all test sounds ≥ 0.85, both seeds.
- **J447b (generalizes to UNHEARD objects):** on the novel-fundamental subset, valence accuracy
  ≥ 0.80, both seeds.
- **J447c (it is the learned rule):** shuffled-valence control ≤ 0.60, both seeds.

Predicted PASS: the energy model perceives a sound's affect from its real spectrum and generalizes to
novel fundamentals — real-sensor "perceiving the energy of the environment." NULL if J447b fails
(affect rode the specific fundamentals, not the acoustic harshness). Bars locked; no retuning. No
transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | affect acc (all) | novel-fundamental affect | shuffled control | feat dim |
|------|------------------|--------------------------|------------------|----------|
| 0 | 1.000 | 1.000 | 0.467 | 32 |
| 7 | 1.000 | 1.000 | 0.473 | 32 |

J447a ✓ · J447b ✓ · J447c ✓ → **PASS, both seeds.**

## Verdict: the substrate hears a sound and feels its energy
A real waveform (`synth_tone`) → real log-FFT feature (`samples_to_feature`, 32 bins) → the energy
model predicts the sound's valence at 1.000, and generalizes perfectly to sounds whose FUNDAMENTAL
was never heard in training (novel-object affect 1.000) — harsh/dissonant/noisy = dark, clean/
consonant = bright. A shuffled-valence control is at chance. So the substrate perceives a sound's
affective "energy" from its real spectrum, independent of recognizing the specific note — the
real-sensor realization of "perceive the energies of the environment" (extends the synthetic JEP-446
to actual acoustics).

**Honest scope.** Audio is SYNTHESIZED (not a live microphone) and the affect mapping (consonant/low-
noise vs dissonant/harsh) is engineered, with the noise level a strong broadband FFT cue — so this
demonstrates real-FFT grounding + generalization to unheard fundamentals, not a discovered affect
rule. Established methods (FFT features + reservoir/RLS), named. A live-microphone version (the repo's
audio I/O exists) is the natural final step. No transformer.
