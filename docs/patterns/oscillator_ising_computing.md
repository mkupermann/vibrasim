# Pattern — Oscillator-Ising computing ("vibrations computing", the real one)

> ⚠️ **Major correction (2026-06-05, G146–G149).** An earlier version of this pattern claimed the oscillator
> "genuinely computes" and "build this." Rigorous re-testing changed the conclusion: the oscillator-Ising
> machine merely **TIES a correct multi-restart greedy** and **LOSES to classical simulated annealing** at
> every scale (n=200–360), even at 10× compute. The G138/G139 "evidence" below compared against weak/loose
> baselines (G139's "greedy", and G145's greedy was outright sign-bugged). The genuine optimization edge is
> **simulated annealing's (a classical algorithm)** — annealing beats local search on hard frustrated
> landscapes, and the oscillator is a *legitimate but weak* annealer, no better than correct greedy. **Honest
> takeaway: to solve hard combinatorial problems, build SA / a proper annealer and benchmark against correct
> local search — the oscillator confers no edge.** The rest of this doc is kept for the method/recipe; read
> its claims through this correction. See `g146`–`g149` + FINDINGS_SUMMARY Addendum 5.

## What it is (established method — Kuramoto / oscillator Ising machine; named as such, not novel)
A network of coupled phase oscillators relaxes to a low-energy spin configuration that SOLVES a
combinatorial optimization problem (MAX-CUT, graph problems, scheduling). The problem is encoded in the
COUPLINGS J_ij; the physics does the search in parallel. This is the honest realization of "physical
vibrations computing," and unlike the EQMOD substrate it genuinely computes.

## Recipe (software reference; hardware = LC/ring oscillators)
- Encode the problem: J = −W (antiferromagnetic) for MAX-CUT so connected nodes anti-align.
- Dynamics: dθ_i = Σ_j W_ij sin(θ_i−θ_j) − K2·sin(2θ_i)·anneal  (second harmonic binarizes phases to {0,π}).
- Anneal K2 from 0→1 over the run; read spins s_i = sign(cos θ_i); the {±1} partition is the answer.
- Run a few random initializations (anneals) and keep the best — as a physical machine would.

## Evidence
- G138: finds the OPTIMAL MAX-CUT on 10-node graphs, 5/5 trials (ratio 1.00) vs random ~0.65.
- G139: scales — approximation stays close to a greedy/SDP-level heuristic as n grows.

## Why this, not EQMOD
EQMOD's own dynamics cannot optimize (G135: atoms collapse, no useful relaxation) because its
bridges/bindings are not a programmable problem Hamiltonian. Oscillator-Ising IS programmable (couplings =
problem), which is the whole point. For physical-computing HARDWARE, build this (cheap: coupled LC tanks or
ring oscillators), not an EQMOD chip.

## Caveat
This is a well-known paradigm (analog Ising machines, coherent Ising machines, oscillator computing). The
contribution here is only the honest pointer + working reference for the project's hardware question — no
novelty claimed.
