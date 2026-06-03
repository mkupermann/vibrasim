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

## RESULT (2026-06-03): NULL — reservoir doesn't generalize XOR; readout too impoverished

| seed | reservoir XOR (held-out) | memory bit[t-1] | linear-on-raw-bits XOR |
|------|--------------------------|-----------------|------------------------|
| 42 | 0.47 | 0.73 | 0.93 (control broken) |
| 7 | 0.36 | 0.60 | 0.18 (control broken) |

G78a ✗ (XOR ≈ chance), G78b ✗. **NULL.** Two honest caveats: (1) the substrate shows PARTIAL fading
memory (bit[t-1] at 0.73 on seed 42 — it retains some input history); (2) the linear-on-raw-bits XOR
control gave 0.93/0.18 — impossible for true XOR — revealing the held-out set (~44 points, class-
imbalanced) is too small for reliable thresholded accuracy. The likely cause of the NULL: the
proto-cell INTERIOR is a poor reservoir — ~16 particles → 8 sparse, noisy octant counts is far too
LOW-DIMENSIONAL and noisy. This is a readout/scale problem, not a clean substrate verdict. The fair
test (G79): a LARGER substrate, a high-dimensional state read from a 3D spatial grid, a longer bit
stream, and a noise-robust metric (correlation + accuracy on a bigger held-out set).
