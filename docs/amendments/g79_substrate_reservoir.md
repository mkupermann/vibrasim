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

## RESULT (2026-06-03): NULL — no usable reservoir; high-dim XOR memory not co-available

| seed | XOR balanced-acc | memory (bit[t-1]) balanced-acc |
|------|------------------|--------------------------------|
| 42 | 0.57 | 0.50 |
| 7 | 0.48 | 0.42 |

G79a ✗ (XOR ≈ chance), G79b ✗ (memory ≈ chance). **Clean NULL.** The full firing lattice has
essentially NO readable fading memory (bit[t-1] ≈ chance) — firing RESETS atom charge, destroying
input history. Contrast: the proto-cell interior (G78) had MORE memory (0.73) because its slow
clearance is an integrator — but it is effectively ~1-dimensional, too low-dim to separate XOR.

**Unifying finding.** The substrate cannot simultaneously provide a HIGH-DIMENSIONAL state AND
FADING MEMORY: proto-cell = memory but ~1-dim; firing lattice = high-dim but no retained memory
(firing resets). Reservoir computing needs both → the substrate is not a usable reservoir for
temporal logic. This is the SAME memory wall that blocks digital storage, now blocking reservoir
computing too. One untested configuration is both high-dim and slow: BRIDGE STRENGTHS (hundreds,
each integrating co-firing history). G80 reads the bridge-strength state (with a leak to avoid
saturation) — the genuine high-dim-with-memory candidate.
