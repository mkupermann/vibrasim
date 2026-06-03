# G80 — Bridge-strength reservoir (the high-dim + fading-memory candidate)

Pre-registered: 2026-06-03 (BEFORE the run). G79 showed the substrate can't give high-dim state AND
fading memory via atom charge (firing resets it) or the proto-cell (~1-dim). The one configuration
that is BOTH: bridge STRENGTHS — hundreds of them, each integrating co-firing history (slow), with a
bridge_leak_rate so they FADE (a fading memory, not saturating latches). State = bridge strengths
binned into a 3x3x3 spatial grid (27 nodes). Drive a random bit stream into an input region; ridge
readout, held-out balanced accuracy on temporal XOR + memory. 200 bits, seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G80a | Bridge reservoir generalizes XOR | held-out balanced accuracy ≥ 0.65, both seeds |
| G80b | Fading memory (diagnostic) | bit[t-1] balanced accuracy ≥ 0.65, both seeds |

PASS = G80a → the bridge-strength state is a usable reservoir: high-dim + fading memory make temporal
XOR linearly readable on unseen data → the physics substrate IS a reservoir (deadlock-free learning
path). NULL = XOR ≈ chance → even the bridge state lacks the memory×separation for temporal logic,
and the reservoir direction is exhausted (the substrate does instantaneous analog computation but
not temporal computation — the memory wall is total). Honest either way. No post-hoc tuning.

## RESULT (2026-06-03): NULL — reservoir direction EXHAUSTED; memory wall is total

| seed | XOR balanced-acc | memory bit[t-1] |
|------|------------------|-----------------|
| 42 | 0.50 | 0.49 |
| 7 | 0.59 | 0.52 |

G80a ✗, G80b ✗. Bridge strengths give no usable fading memory of the input either (≈ chance). All
three reservoir states fail: proto-cell (low-dim, partial memory, no XOR); firing lattice (high-dim,
no memory); bridge strengths (high-dim, no usable memory). **The reservoir direction is exhausted.**

**Unifying conclusion (cognition question, definitively closed).** The substrate cannot usefully
retain and separate input HISTORY in any readable form — so the same memory wall that blocks digital
storage (G33–G73, ~45 experiments) ALSO blocks reservoir computing (G77–G80). The substrate does
INSTANTANEOUS nonlinear analog computation (filter/demodulate/receive — G60–G76, all PASS) but NOT
TEMPORAL computation. It is a MEMORYLESS nonlinear analog processor. No form of learning/memory is
achievable on this physics. Next: test the flip side — SPATIAL/instantaneous computation (needs no
memory), which should be within reach where temporal failed.
