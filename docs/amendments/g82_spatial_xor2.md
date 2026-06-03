# G82 — Instantaneous spatial XOR, proper readout (free-vibration grid)

Pre-registered: 2026-06-03 (BEFORE the run). Fixes G81's confound (atom-charge state didn't encode
input). Read FREE-VIBRATION density per 3x3x3 grid — injected vibrations sit where placed, so the
state reliably encodes the input (sanity should pass). Two CLOSE input regions (x=8, x=14) so their
vibrations meet and bind in the middle → the middle bin reflects A*B, the interaction feature XOR
needs. Raw binding substrate (no channel). Held-out balanced accuracy, 240 trials, seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| sanity | Single input readable | reading input A alone ≥ 0.65, both seeds (state encodes input) |
| G82a | Instantaneous spatial XOR | held-out balanced accuracy ≥ 0.65, both seeds |

PASS = G82a → the memoryless substrate computes instantaneous spatial XOR (nonlinear multi-input
logic from binding interaction). NULL with sanity PASS = inputs readable but XOR not → the substrate
reads inputs but cannot combine them nonlinearly into a separable representation (LINEAR-only spatial
computation). INCONCLUSIVE if sanity fails again. Honest either way. No post-hoc tuning.
