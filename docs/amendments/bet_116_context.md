# BET-116 — Context-Gated Transitions (disambiguate concurrent sequences)

Pre-registered: 2026-05-31 (BEFORE the run). BET-115 found that concurrent
sequences interfere in the shared Hebbian transition matrix T. Fix: give each
sequence a CONTEXT tag (an "episode id" on dedicated context nodes, held constant
within a sequence and clamped during recall). The same content in different
sequences then has a different FULL state, so transitions disambiguate.

## Mechanism
N=120 with C=20 context nodes + 100 content nodes. Each sequence s gets a fixed
random tag on the context nodes; every pattern in s carries that tag. Train with
train_sequence (W + T over full states). Recall: clamp the context nodes to the
sequence tag throughout, predict next via T, clean up with context held.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T116a | Multiple sequences recalled | with S=3 length-4 sequences, every sequence's min per-step CONTENT overlap >= 0.90 |
| T116b | Beats no-context | a no-tag baseline (same S=3) has min content overlap < 0.75 |
| T116c | Scales | S=5 sequences still recalled with min content overlap >= 0.85 |

PASS = T116a-c. PASS = context-gating fixes the concurrent-sequence interference —
the substrate holds multiple episodic sequences, a hierarchical predictive step.

## RESULT (2026-05-31): NULL — context did not disambiguate at the capacity edge

S=3 with context min content overlap 0.550; no context 0.520; S=5 context 0.460.
Context-gating did NOT help: at N=120, 12 patterns is the static-capacity edge, so
the clean-up attractors are already overloaded/marginal — a context tag cannot
disambiguate states the attractors themselves cannot hold cleanly. The bottleneck
is attractor CAPACITY here, compounded with transition interference. T116a x,
T116b ok (no-context also fails), T116c x. BET-117 tests the capacity hypothesis:
multiple sequences at LARGER N (12 patterns well within capacity).
