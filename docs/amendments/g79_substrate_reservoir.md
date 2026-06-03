# G79 — Whole-substrate reservoir (high-dimensional state, held-out temporal XOR)

Pre-registered: 2026-06-03 (BEFORE the run). G78's NULL was confounded by an impoverished readout
(tiny proto-cell interior, 8 sparse counts). G79 reads the FULL firing substrate: a random bit
stream is injected into an input region of a neuron_dynamics lattice; the reservoir STATE is a
3x3x3 spatial grid of atom charge (27 'nodes') capturing the substrate's recurrent activity. Ridge
readout trained on 70%, evaluated on a held-out tail with BALANCED accuracy (robust to class
imbalance). Targets: temporal XOR (bit[t]^bit[t-1]; needs memory + nonlinearity) and bit[t-1]
(memory). 200 bits. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G79a | Reservoir generalizes XOR | held-out BALANCED accuracy ≥ 0.65, both seeds |
| G79b | Fading memory (diagnostic) | held-out balanced accuracy for bit[t-1] ≥ 0.65, both seeds |

PASS = G79a → the full substrate is a usable RESERVOIR: its recurrent nonlinear dynamics make
temporal XOR linearly readable on unseen data — computation + short memory with NO writable internal
memory (sidesteps write=leak). A genuine deadlock-free path to a learning system on the physics.
NULL = XOR ≈ chance even with the rich state → the substrate's reservoir capacity (fading memory ×
nonlinear separation) is insufficient for temporal logic; report what memory it does have (G79b).
Honest either way. No post-hoc tuning. (Reservoir computing is established — Jaeger/Maass; novelty
only in using this physics substrate.)
