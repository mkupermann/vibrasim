# G138 — Reference: "vibrations computing" done right (oscillator-Ising solves MAX-CUT)

## Why this exists
The user asked how to build physical "vibrations computing" hardware. EQMOD's own vibration dynamics
compute nothing useful (G133–G135). G138 is a concrete, runnable REFERENCE of the established paradigm I
recommended instead — a coupled-oscillator (Kuramoto-style) ISING machine — so there is a working
demonstration of what the hardware should actually do.

## Method (established — NOT novel, NOT EQMOD)
Plain coupled oscillators in numpy: phases relax under dθ_i = +Σ_j W_ij sin(θ_i−θ_j) − K2·sin(2θ_i)·anneal
(antiferromagnetic coupling J=−W drives connected nodes ANTI-aligned = a cut; the second-harmonic term
binarizes phases to {0, π} = spins). Binarized phases give the partition. This is textbook oscillator /
Ising-machine computing (Kuramoto + second-harmonic injection-locking), named as such.

## Result (random 10-node graphs, best of 6 anneals)
| trial | optimal MAX-CUT | oscillator machine | ratio | random mean |
|-------|-----------------|--------------------|-------|-------------|
| 0–4   | 14,15,17,17,16  | 14,15,17,17,16     | **1.00** each | ~9.5–11.5 |

**VERDICT: PASS** — the oscillator-Ising machine finds the OPTIMAL cut on every trial by physical
relaxation (vs random ~0.65 of optimal).

## The honest point
This is the real "physics computes in parallel" paradigm, and it WORKS — because the problem is encoded in
the COUPLINGS and the dynamics relax to the ground state. EQMOD's dynamics cannot do this (G135: atoms
collapse, no useful relaxation; its bridges/bindings are not a programmable problem Hamiltonian). So the
honest hardware advice stands: build an oscillator-Ising machine (cheap: LC/ring oscillators), not an
EQMOD chip. (Bug note: the first run synchronized all spins → cut 0; that was a MIN-cut sign error,
corrected to antiferromagnetic coupling — the established formulation.)
