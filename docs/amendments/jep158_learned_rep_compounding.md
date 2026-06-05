# JEP-158 — does multi-hop inference over LEARNED embeddings compound? + substrate Hopfield cleanup as the cure
(Connects the four pillars [learned reps] + the universal compounding insight + "where is the substrate in the chain")

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 multi-hop translation in learned embedding space WITHOUT cleanup DEGRADES with hop-depth (translation errors
  accumulate ~sqrt(k)*noise — the universal compounding insight holds for the LEARNED path too); per-hop
  NEAREST-ENTITY cleanup (snap to nearest entity vector = attractor/Hopfield, the substrate's native op) re-anchors
  each hop and RESTORES deep accuracy (the learned-rep analogue of redundant-path aggregation, substrate as cure).
  MOST-LIKELY MISS: embeddings too clean to compound (inject noise per the JEP-157 lesson); or cleanup snapping to
  WRONG attractors once noise exceeds the basin.

## Acceptance (characterization)
- Report multi-hop relational-inference accuracy by hop-depth, WITHOUT vs WITH per-hop nearest-entity cleanup, at a
  realistic embedding-noise level. Showing the universal insight in the LEARNED/continuous regime + substrate
  cleanup as the cure is the finding. Established (TransE, vector-symbolic cleanup memory, Hopfield); named; no novelty.

## Result — MISS (prediction wrong in direction; + a REPEATED bug) -> a genuine refined insight
### The honest process (recorded in full)
- 158 / 158b: BOTH runs were broken by the SAME bug — I scaled D-dimensional noise as sigma*randn(D) which has
  magnitude sigma*sqrt(D), so sigma=0.15 at D=64 gave perturbation norm ~1.2, SWAMPING the unit signal |t|=1 (even
  depth-1 failed, cleanup snapped into wrong attractors). This is a CARDINAL REPEATED MISTAKE (made it twice): in D
  dimensions ALWAYS scale noise by 1/sqrt(D) to control magnitude relative to unit vectors. Durable lesson logged.
- 158c (bug fixed, noise = f/sqrt(D)): showed NO compounding (a mean-over-19-steps learned translation averages the
  jitter out) — REFUTING the simple 'compounds like symbolic chains' hypothesis.
- 158d/158e (resolution): the real structure, OPPOSITE my prediction.

### The finding (f=0.35 per-edge error, within basin)
| chain type | d1 | d2 | d4 | d8 | d16 |
|------------|----|----|----|----|-----|
| SHARED operator (reused), no cleanup | 1.00 | 1.00 | 0.99 | 0.81 | 0.49 |
| INDEPENDENT facts, no cleanup | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 |
| INDEPENDENT facts, cleanup | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| SHARED operator, WITH cleanup | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

CONTINUOUS/distributed representations compound DIFFERENTLY than symbolic chains, OPPOSITE to symbolic intuition:
- INDEPENDENT per-hop errors → random walk ~f*sqrt(k), PARTIALLY CANCEL, and in high-D are nearly ORTHOGONAL to the
  lattice direction (which separates entities) → ROBUST (0.99 @ depth-16).
- SHARED / systematic bias → repeats COHERENTLY every hop → accumulates LINEARLY (k*bias) → FRAGILE (0.49 @ d16).
- (symbolic independent-edge errors compound EXPONENTIALLY ~(1-p)^k — the most fragile of the three.)
Per-hop nearest-entity CLEANUP (substrate Hopfield/attractor, JEP-4) re-anchors each hop and cures BOTH continuous
cases (shared 0.49 → 1.00 @ d16).

### REFINED universal insight (the genuine contribution)
The compounding EXPONENT depends on the REPRESENTATION: symbolic-independent = exponential (1-p)^k; continuous-
independent = sqrt(k) (errors average/cancel); continuous-systematic = linear k. Aggregation/cleanup cures all.
SO: continuous distributed representations are MORE robust to INDEPENDENT per-hop noise than symbolic chains (a
concrete reason the four-pillar LEARNED path helps), but VULNERABLE to systematic bias; the substrate's attractor
cleanup is the native cure for both. This ties the four pillars (learned reps) + the universal insight (now
representation-dependent) + the substrate ('where is the substrate in the chain' — Hopfield cleanup IS the cure).
Prediction MISS (wrong direction, twice; + repeated D-scaling bug); tally 52/74. Established (TransE, vector-symbolic
cleanup memory, Hopfield, random-walk error analysis); named; no novelty.
