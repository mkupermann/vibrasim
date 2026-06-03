# G75 — Nonlinear computation: AM demodulation (envelope detection)

Pre-registered: 2026-06-03 (BEFORE the run). G74 found a saturating nonlinearity. The proof that it
enables real COMPUTATION (not just filtering): AM demodulation. Drive the interior with an
amplitude-modulated influx — a FAST carrier (period 40, above the low-pass cutoff) whose amplitude
is a SLOW envelope (period 600). The envelope frequency is NOT in the input spectrum (the input has
energy at the carrier and carrier±sidebands, none at 600 Hz directly); a LINEAR system therefore
outputs ~0 at the envelope frequency. Only a NONLINEAR element (rectification/saturation) can
demodulate the envelope. If the interior shows the envelope frequency, the substrate computed a
nonlinear function a filter alone cannot.

## Method
Proto-cell (channel ON), AM influx n(t) = round(BASE·env(t)·carrier(t)), env period 600, carrier
period 40, window 1200. Measure interior response amplitude (single-bin DFT) at the envelope vs the
carrier frequency. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G75a | Envelope recovered | interior amp(envelope) / amp(carrier) ≥ 2.0 AND amp(envelope) ≥ 0.02 (both seeds) |

PASS = G75a → the substrate DEMODULATES: it recovers the slow envelope that exists only in the
modulation — a nonlinear computation (AM detection) impossible for a linear filter. The proto-cell
is not just an analog filter but a nonlinear analog COMPUTER (filter + saturation = demodulator).
NULL = the envelope is not recovered (the nonlinearity is too weak or the carrier dominates) — the
substrate's analog capability is limited to linear filtering. Honest either way. No post-hoc tuning.

## RESULT (2026-06-03): PASS — the substrate DEMODULATES (nonlinear computation)

| seed | envelope_amp | carrier_amp | env/carrier |
|------|--------------|-------------|-------------|
| 42 | 0.167 | 0.017 | 9.79 |
| 7 | 0.158 | 0.017 | 9.58 |

G75a ✓ → **PASS.** The interior recovers the slow envelope (0.16) at ~10× the carrier — a frequency
that exists ONLY in the amplitude modulation, absent from the input spectrum. A linear filter outputs
~0 there; only the saturating nonlinearity (G74) can demodulate it. The substrate performed AM
demodulation = a genuinely nonlinear computation (saturation + low-pass). It is a nonlinear analog
COMPUTER, not just a filter. (Honest: envelope detection is textbook engineering — this is a clean
demonstration the substrate implements a real nonlinear computation, not a novel discovery.)
