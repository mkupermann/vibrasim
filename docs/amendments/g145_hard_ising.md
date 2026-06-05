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

## ⚠️ CORRECTION (2026-06-05, G146–G148): this headline advantage does NOT survive scrutiny
G145's "genuine advantage" was REFUTED then re-examined rigorously:
- **G146**: G145's greedy baseline was SIGN-BUGGY (it descended toward MIN-cut, returning negative cuts). A
  *correct* multi-restart greedy reaches the optimum on all 8 of G145's n=30 instances — they are not hard.
  Oscillator-anneal merely ties correct greedy there; the "8/8 win" was a win over a backwards baseline.
- **G147–G148**: scaling to n=200–360 (hard regime), **classical simulated annealing** genuinely beats a
  strong correct greedy (~+2%, 14/15) — the real, textbook "annealing > local search on glassy landscapes."
  But separating the *physical oscillator machine* from classical SA: the **oscillator TIES correct greedy
  (6/15, gap ≈ 0) and loses to SA 15/15** at every scale.
- **Corrected niche:** the genuine advantage belongs to the **classical SA algorithm (no substrate needed)**,
  NOT to the physical/vibrations oscillator machine. So the honest final answer collapses to: the physics is
  decorative *everywhere tested* — including hard combinatorial optimization. See
  `g146_oscillator_vs_simulated_annealing.md`, `g147_advantage_at_scale.md`, `g148_advantage_larger_scale.md`.
