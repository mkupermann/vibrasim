# Analog Computer Summary (G44 → G76) — what the substrate CAN compute

Consolidated 2026-06-03. After the digital-memory deadlock was proven fundamental (write=leak across
all channels and ~45 experiments — see MEMORY_PROGRAMME_SUMMARY + FINDINGS_SUMMARY Addendum 2), this
thread establishes what the substrate genuinely IS: a tunable, nonlinear ANALOG SIGNAL PROCESSOR,
built bottom-up from physics primitives + one engineered §4.8 channel. No LLM.

## The capability, fully demonstrated (all PASS, seeds 42 & 7)
| Stage | Result | What |
|-------|--------|------|
| G44 | regulation | restores interior set-point after perturbation |
| G58 | step response | first-order, magnitude-independent time-constant τ≈75 ticks |
| G59 | DC gain | bounded, influx-proportional steady state |
| G60 | low-pass | tracks slow, attenuates fast (6.5×) |
| G61 | tunable cutoff | τ ∝ membrane radius (design law) |
| G62 | denoise | ~9× SNR gain (recover signal from noise) |
| G63 | filter bank | two sizes discriminate frequency (2.5×) |
| G74 | saturation | clamped-linear: the first computing NONLINEARITY |
| G75 | demodulation | recovers an AM envelope (nonlinear; ~10× carrier) |
| G76 | receiver | recover AM envelope buried in noise (SNR ~7-9) |

## What it means
- **Linear element:** a tunable first-order low-pass filter (leaky integrator). Cutoff set by membrane
  size. Filters, integrates, rejects disturbances — proportionally and boundedly.
- **Nonlinear element:** a saturating limiter (G74). This is the piece that lets it COMPUTE, not just
  filter: AM demodulation (G75) and a complete denoise+demodulate receiver (G76).
- **Mechanism:** the selective channel does proportional efflux (→ leaky integrator) that saturates at
  high load (→ limiter). Computation from selective transport, the substrate's genuine strength —
  NOT a selective write (the deadlock).

## Honest scope
These are TEXTBOOK analog operations (RC low-pass, envelope detector, AGC) reproduced from substrate
primitives — a clean CHARACTERIZATION of the substrate's computational class, NOT novel discoveries.
The honest headline: **the substrate is a nonlinear analog signal processor, not a digital memory.**
It computes continuous/temporal functions (filter, integrate, demodulate, denoise); it cannot store
selective symbolic memory. Its value lies in the former.

## Reusable
docs/patterns/protocell_controller.md — the proto-cell as a tunable nonlinear analog element.
