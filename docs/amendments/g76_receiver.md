# G76 — Complete analog receiver: recover an AM envelope buried in noise

Pre-registered: 2026-06-03 (BEFORE the run). Capstone of the analog-computing thread: combine
denoising (G62) and demodulation (G75) in one pass. Input = an amplitude-modulated carrier (period
40, envelope 600) PLUS broadband random noise of comparable amplitude. A complete receiver recovers
the slow envelope while rejecting the noise. Measure interior response at the envelope frequency vs
an off-signal probe frequency (noise floor). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G76a | Envelope recovered from noise | interior amp(envelope) / amp(off-signal probe) ≥ 3.0 AND amp(envelope) ≥ 0.02 (both seeds) |

PASS = G76a → the substrate is a complete analog RECEIVER (denoise + demodulate): it extracts a
weak AM envelope from noise — a multi-stage nonlinear computation from substrate primitives. NULL =
the envelope is lost in noise (the receiver is incomplete). Honest either way. No post-hoc tuning.
