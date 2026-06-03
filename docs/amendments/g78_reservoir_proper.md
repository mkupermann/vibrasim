# G78 — Substrate reservoir, done properly (held-out temporal XOR)

Pre-registered: 2026-06-03 (BEFORE the run). Fixes the G77 overfitting flaw with a proper protocol:
a long random bit stream (150 bits), a high-dimensional reservoir STATE read in 8 spatial octants,
target = temporal XOR (bit[t] XOR bit[t-1]) which needs short memory + nonlinearity, and a HELD-OUT
train/test split (ridge readout trained on 70%, tested on the last 30%). #samples (≈100 test) >>
#features (8) and generalization-tested → no trivial interpolation.

## Method
Proto-cell (channel ON). Each bit = a 12-tick window; bit=1 injects bursts. Read the 8-octant
interior incompatible-vibration counts as the reservoir state at each bit step. Ridge readout
(λ=1) to XOR; report HELD-OUT test accuracy. Controls: (b) linear readout on raw bits {bit[t],
bit[t-1]} → XOR (should be ≈ chance); (c) reservoir → bit[t-1] (linear memory task). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G78a | Reservoir generalizes XOR | held-out test accuracy ≥ 0.70, both seeds |
| G78b | Task needs nonlinearity (control) | linear readout on raw bits → XOR test accuracy ≤ 0.65, both seeds |

PASS = G78a–b → the substrate's nonlinear dynamics make temporal XOR linearly readable on UNSEEN
data: a genuine reservoir (computation + short memory from fixed dynamics + a trained linear
readout, NO writable internal memory — sidesteps write=leak). A real, deadlock-free path to a
learning system on the physics. NULL = held-out XOR ≈ chance (the reservoir lacks the memory/
nonlinearity to generalize). Honest either way. No post-hoc threshold tuning. (Reservoir computing
itself is established — Jaeger/Maass; the only novelty would be using THIS physics substrate.)
