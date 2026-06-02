# G62 — Analog denoising: the proto-cell recovers a signal from noise

Pre-registered: 2026-06-02 (BEFORE the run). The proto-cell is a tunable first-order low-pass
filter (G60/G61). A low-pass filter DENOISES: given a slow signal buried in fast noise, it passes
the signal and rejects the noise. This BET demonstrates the substrate performing a useful ANALOG
COMPUTATION (signal recovery) — a constructive contrast to the memory deadlock (the substrate
cannot store, but it can PROCESS).

## Method
Proto-cell (channel ON, pre-cleared). Drive the interior with a foreign influx carrying TWO
equal-amplitude components: a slow SIGNAL (period 600, below cutoff) + fast NOISE (period 40, above
cutoff): n(t)=round(base·(1 + 0.4·sin(2π t/600) + 0.4·sin(2π t/40))), base=6. Window 1200 ticks.
Measure the interior response amplitude at the signal and noise frequencies (single-bin DFT). At
the INPUT the two components are equal; a denoising filter makes the OUTPUT signal-dominated.
Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G62a | Denoising gain | interior amplitude(signal) / amplitude(noise) ≥ 3.0 (both seeds) |

PASS = G62a → the proto-cell recovers the slow signal and rejects the fast noise (≥3× SNR gain
from an equal-amplitude input): a substrate-level analog denoising computation. The substrate can
PROCESS signals even though it cannot STORE selective memory. NULL: if the ratio < 3 the filtering
is too weak to denoise at this noise frequency (or signal too noisy to resolve). No post-hoc tuning.

## RESULT (2026-06-02): PASS — ~9× SNR gain (analog denoising)

| seed | amp signal | amp noise | SNR gain |
|------|-----------|-----------|----------|
| 42 | 0.131 | 0.014 | 9.32 |
| 7 | 0.128 | 0.014 | 9.19 |

G62a ✓ → **PASS.** From an equal-amplitude signal+noise input, the interior recovers the slow
signal (0.13) and rejects the fast noise (0.014): a ~9× SNR gain, both seeds. The proto-cell
performs an analog DENOISING computation — concrete evidence the substrate can PROCESS signals
even though it cannot STORE selective memory.
