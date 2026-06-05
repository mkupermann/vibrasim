# G140 — The physical-computing paradigm also does ASSOCIATIVE MEMORY (Hopfield recall)

## Result (n=64, exact recovery from noisy cue)
| stored K | 5% noise | 15% noise | 25% noise |
|----------|----------|-----------|-----------|
| 3 | 1.00 | 1.00 | 1.00 |
| 5 | 1.00 | 1.00 | 1.00 |
| 8 | 1.00 | 0.88 | 0.75 |

**VERDICT: PASS** — content-addressable recall works (1.00 for ≤5 patterns at ≤15% noise), degrading
gracefully near the classical Hopfield capacity (~0.14·n ≈ 9 patterns).

## Finding — one physical paradigm gives no-LLM memory AND compute
The SAME coupled-relaxation dynamics that solve optimization (G138/G139, Ising/MAX-CUT) also perform
content-addressable MEMORY (G140, Hopfield recall). So the recommended hardware substrate — coupled
oscillators / Ising machine — is a complete no-LLM physical-AI primitive set: store-and-recall + optimize.
Established methods (Hopfield network, Ising machine), named as such; this is the honest, buildable answer
to the user's physical-computing goal, and the contrast with EQMOD (which does neither in its own dynamics:
no useful optimization G135, and its memory needs an engineered scaffold).

## The complete, honest arc for the user's question
- EQMOD physics: a no-LLM data store only; no learning/compute (G131–G137).
- "Human-like AI without LLM": not reachable on these pieces (linear-composable ceiling, bigram on real text).
- The realizable physical-computing path: oscillator/Ising/Hopfield hardware — optimization + associative
  memory, scaling, buildable cheaply (LC/ring oscillators). Build THIS.
  > ⚠️ **Tempered (G146–G149, 2026-06-05):** the *optimization* half of this does NOT hold for the oscillator —
  > it ties a correct greedy and loses to classical SA at scale (build SA, not the oscillator, for hard
  > combinatorial problems). The *associative-memory* half (this G140 Hopfield recall) remains a valid bounded
  > primitive (established Hopfield dynamics, named as such). See g146–g149 + FINDINGS_SUMMARY Addendum 5.
