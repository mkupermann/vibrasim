# G87 — Instantaneous spatial XOR on a quiet substrate (low-dim interpretable readout)

Pre-registered: 2026-06-03 (BEFORE the run). Builds on G83 (quiet substrate reads input perfectly,
1.00) and fixes its weaknesses: weak nonlinear interaction (inputs too far) and overfitting risk
(coarse 27-bin grid). Inputs CLOSE (A=9, B=13) so their vibrations interact; readout is only 4
INTERPRETABLE features: free-vibration count in the A-region, B-region, and OVERLAP region (M=11),
plus atom count in the overlap (binding = the A*B interaction term). 4 features vs ~150 samples +
held-out split -> no overfitting. Background culled each trial (quiet). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| sanity | Single input readable | single-input(A) held-out balanced acc >= 0.70, both seeds |
| G87a | Instantaneous spatial XOR | held-out balanced acc >= 0.70, both seeds |

PASS = G87a -> the quiet substrate computes instantaneous spatial XOR: genuine nonlinear multi-input
logic (the overlap binding provides the A*B interaction), no memory needed. NULL with sanity PASS =
inputs readable but no usable nonlinear interaction (linear-only spatial computation). INCONCLUSIVE
if sanity fails. Honest either way. No post-hoc tuning.

## RESULT (2026-06-03): NULL (sanity PASS) — quiet substrate is a LINEAR spatial reader, no XOR

| seed | single-input(A) | spatial XOR |
|------|-----------------|-------------|
| 42 | 1.00 | 0.52 |
| 7 | 1.00 | 0.49 |

Sanity PASS (1.00 both) confirms G83: a quiet substrate reads input perfectly. But XOR ≈ chance —
the overlap region does NOT provide a usable A*B interaction. The quiet substrate does LINEAR
instantaneous spatial computation (reads A, reads B, sums them) but NOT nonlinear multi-input logic.
Its proven nonlinearity (saturation/demodulation, G74/G75) is SINGLE-CHANNEL (one accumulator), not
a cross-input interaction. Precise bound: instantaneous spatial computation is LINEAR-only.
