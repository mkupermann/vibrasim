# BET-081 — Emergent Audio-Cortex Clustering (Continuous Stream)

Pre-registered: 2026-05-25, before any training run.

## Hypothesis

A 8K-neuron cortical substrate (4-layer, STDP + homeostasis) fed a
**continuous, unsegmented** English audiobook stream will develop
distinct L5-neuron clusters that respond selectively to different
recurring acoustic motifs — without any labels, segmentation, or
pre-trained models.

## Architecture

- 8K excitatory + 2K inhibitory = 10K neurons total
- 4 layers: L4 (2000E+500I), L23 (2500E+625I), L5 (2000E+500I), L6 (1500E+375I)
- Input: 32 Mel-frequency bands → 32 Poisson neurons
- Mel spectrogram: librosa, n_mels=32, n_fft=512, hop_length=160, sr=16000
  (no pre-trained model — just FFT + triangular Mel filterbank)
- Chunk duration: 10ms sim-time per 10ms audio frame (hop_length=160 @ 16kHz)
- STDP on all E→E pathways, homeostatic threshold drift
- Connection probabilities: same ratios as BET-077c

## Input

Continuous concatenated LibriVox audiobook (Pride and Prejudice chapters
1-9 + Walden excerpts, ~82 min total). Audio is streamed frame-by-frame
through the substrate. No segmentation, no silence removal, no labels.
The stream loops when exhausted.

## Evaluation (post-hoc probing only)

After N hours of continuous training:
1. Freeze STDP (set learning rates to 0)
2. Stream a held-out 5-minute audio segment through the substrate
3. Record L5 spike patterns per 100ms window (10 frames)
4. Cluster L5 spike-pattern vectors with k-means (k=10)
5. For each cluster, collect the corresponding audio windows
6. Measure intra-cluster acoustic similarity (mean pairwise cosine of
   Mel vectors within cluster) vs inter-cluster similarity

## Acceptance Bars (pre-registered)

| ID | Criterion | Bar |
|----|-----------|-----|
| T81a | Training duration | >= 4h wallclock continuous without crash |
| T81b | L5 neuron activity | >= 50% of L5 E-neurons fire at least once during eval |
| T81c | Cluster distinctness | At least 3 of 10 k-means clusters have intra-cluster cosine > inter-cluster cosine + 0.05 |
| T81d | Non-trivial selectivity | Silhouette score of L5 spike-pattern clustering > 0.05 (above random baseline) |
| T81e | Negative control | Untrained substrate (same architecture, no STDP exposure) must FAIL T81c and T81d |

## Time Budget

- Realistic: 6h wallclock (4h training + 2h eval/probing)
- Hard ceiling: 12h wallclock
- Overrun = FAILED post-mortem in LOGBOOK.md

## What this BET does NOT use

- Labels of any kind (no human annotation, no forced alignment)
- Pre-trained models (no Whisper, Wav2Vec, Vosk, HMM-GMM)
- External segmentation (no energy-VAD, no silence detection)
- Backpropagation or gradient descent
- BPE tokenizer or text embeddings
