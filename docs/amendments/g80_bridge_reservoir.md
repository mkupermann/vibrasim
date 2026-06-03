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
