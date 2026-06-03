# G81 — Instantaneous spatial XOR: what the memoryless substrate CAN compute

Pre-registered: 2026-06-03 (BEFORE the run). The substrate is a memoryless nonlinear analog
processor: it can't do temporal computation (G77-G80) but should be able to do INSTANTANEOUS
nonlinear computation (no memory needed). Test: spatial XOR. Two input regions A,B driven
SIMULTANEOUSLY per a random 2-bit input; target = XOR of the CURRENT input. Both inputs are present
at once, so no memory is required — the substrate's instantaneous nonlinearity (saturation creates
an A*B interaction feature) must make XOR linearly readable from the CURRENT 27-node atom-charge
grid. Ridge readout, held-out balanced accuracy, 220 trials, seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G81a | Instantaneous spatial XOR | held-out balanced accuracy ≥ 0.65, both seeds |
| G81b | Single input readable (sanity) | reading input A alone ≥ 0.65, both seeds |

PASS = G81a → the memoryless substrate computes instantaneous spatial XOR: genuine nonlinear
classification of a simultaneous input, no memory needed. The substrate is a usable INSTANTANEOUS
nonlinear computer (it just can't compute over time). NULL = even instantaneous XOR is not linearly
readable → the nonlinearity does not create a usable interaction feature in the readable state; the
substrate's computation is limited to single-channel nonlinear transforms (filter/demodulate), not
multi-input logic. Honest either way. No post-hoc tuning.
