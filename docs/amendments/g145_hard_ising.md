# G145 — A GENUINE physical advantage: oscillator-anneal beats greedy on HARD frustrated MAX-CUT

## Result (spin-glass MAX-CUT, signed weights, n=30, 8 instances)
| metric | value |
|--------|-------|
| oscillator-anneal wins | 8/8 |
| mean (oscillator − greedy) cut | **+95.1** |
| greedy cuts | NEGATIVE (−25 to −67) — trapped in bad local minima |

**VERDICT: PASS** — on hard FRUSTRATED instances the oscillator-Ising machine WITH noise annealing
decisively beats multi-restart greedy (escapes local minima greedy cannot).

## Finding — there IS a real regime where physical/energy-based computing genuinely wins
This is the honest counterpoint to the project's "physics is decorative" pattern (G133/G144): on HARD
combinatorial optimization (frustrated/glassy landscapes), the physical ANNEALING machine genuinely
outperforms local search — which is exactly why Ising machines / annealers exist. The annealed noise lets
the dynamics escape the local minima that trap greedy.

Honest caveat: greedy is a WEAK baseline for frustrated problems; the proper peer is SIMULATED ANNEALING,
and the oscillator-Ising machine essentially IS a physical annealer. So the precise claim is "annealing
(physical or simulated) beats local search on hard instances" — established, real, and the oscillator-Ising
is a legitimate physical realization of it. THIS is the one place EQMOD-adjacent "vibrations computing"
has a genuine edge: hard combinatorial optimization via annealing, NOT feature-learning / language / the
EQMOD substrate's own dynamics.

## Final, complete answer
- EQMOD substrate: computationally empty (memory only).
- No-LLM cognition stack: bounded; standard ML carries it, physics decorative.
- BUT the oscillator/Ising/annealing paradigm has ONE genuine advantage — hard combinatorial optimization
  (G145) — plus the bounded recall/learn/generate primitives (G140-142). That is the real, buildable,
  honest niche.
