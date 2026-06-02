# G60 — Frequency response: is the proto-cell controller a low-pass filter?

Pre-registered: 2026-06-02 (BEFORE the run). G58/G59 established the proto-cell as a first-order
linear homeostatic controller (transient τ≈75 ticks + proportional DC gain). A first-order system
is a LOW-PASS FILTER: it tracks disturbances slower than its cutoff (~1/τ) and attenuates faster
ones. G60 completes the linear system-ID by measuring the frequency response — apply a sinusoidally
MODULATED foreign influx and measure the interior's response amplitude at the drive frequency.

## Method
Proto-cell (channel ON, pre-cleared). Inject foreign at rate n(t)=round(base·(1+sin(2π t/period)))
each tick (base=4). Two drive periods: SLOW (600 ticks, below cutoff → should track) and FAST
(60 ticks, above cutoff → should attenuate). Window 1200 ticks. Extract the interior response
amplitude at the drive frequency via a single-bin DFT (robust to small-signal noise). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G60a | Low-pass behavior | response amplitude(slow) / amplitude(fast) ≥ 2.0 (both seeds) |

PASS = G60a → the proto-cell controller is a genuine first-order LOW-PASS FILTER: it passes slow
disturbances and attenuates fast ones, completing the linear system-ID (step + DC gain + frequency
response). The proto-cell is a substrate-level analog low-pass element. NULL: if the ratio < 2 the
response is not frequency-selective (or the signal is too noisy to resolve) — an honest limit on
the characterization. No post-hoc threshold tuning.

## RESULT (2026-06-02): PASS — first-order LOW-PASS FILTER

| seed | amp(slow, P=600) | amp(fast, P=60) | ratio |
|------|------------------|-----------------|-------|
| 42 | 0.226 | 0.035 | 6.43 |
| 7 | 0.217 | 0.033 | 6.56 |

G60a ✓ → **PASS.** The interior tracks slow disturbances (amp 0.22) and attenuates fast ones ~6.5×
(amp 0.035), both seeds. The proto-cell controller is a genuine first-order LOW-PASS FILTER.
This completes the linear system-ID: step response (G58) + DC gain (G59) + frequency response (G60),
all PASS both seeds. The proto-cell is a fully characterized substrate-level analog low-pass /
first-order homeostatic controller, built bottom-up from physics primitives. Surfaced as
docs/patterns/protocell_controller.md.
