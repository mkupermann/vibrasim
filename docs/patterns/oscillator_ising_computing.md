# Pattern — Oscillator-Ising computing ("vibrations computing", the real one)

> ⚠️ **Correction + refinement (2026-06-05, G146–G150).** An earlier version claimed the oscillator
> "genuinely computes / build this" on the strength of G138/G139 — but those compared against weak/loose
> baselines (and G145's greedy was outright sign-bugged). Rigorous re-testing:
> - **The NAIVE phase-only oscillator (G145's dynamics) is weak** — it merely TIES a correct multi-restart
>   greedy and LOSES to classical simulated annealing 15/15 at n=200–360, even at 10× compute (G146–G149).
> - **BUT the textbook amplitude-heterogeneity correction (AHC-CIM; Leleu/Yamamoto 2019) fixes most of it**
>   (G150): the corrected machine BEATS correct greedy 5/5 at n=360 and comes within ~0.7% of SA (a hair
>   behind, edging it on 1/5). So a *properly-engineered* oscillator/CIM IS a legitimate annealer competitive
>   with SA and genuinely better than local search — the naive G145 version was just under-engineered.
> - **Honest takeaway:** for hard combinatorial optimization, a correct CIM-AHC (NOT G145's naive oscillator)
>   is competitive with classical SA; SA stays marginally best and is far simpler, so SA is the pragmatic
>   choice, but the physical-annealer paradigm is real. The recipe below should use **AHC**, not phase-only.
>   See `g146`–`g150` + FINDINGS_SUMMARY Addendum 5.

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
