# Pattern: learning relational STRUCTURE from observation — where the JEP-69/70 frontier actually lies (JEP-128..134)

"Can't learn arbitrary structure" (JEP-69/70 NULL) was too pessimistic. A careful 7-rung characterization shows
where structure learning is easy, where it is genuinely hard, and WHY.

## What IS learnable (and easily)
- **A relation's algebraic properties from CLEAN data**: transitivity by closure-consistency (JEP-128, reliable at
  adequate density), composition rules by best-F1 match (JEP-129, 'uncle = parent o sibling'). On clean data the
  correct rule matches EXACTLY (F1=1.0) while spurious candidates match poorly, so it is UNIQUELY IDENTIFIABLE.
- **Robustly**: composition-rule discovery survives 15 distractor relations + 20% label noise (JEP-129); rule
  discovery is 1.00 even at depth-3 x vocab-10 (JEP-131). The limit there is SEARCH COST (|R|^depth, combinatorial),
  NOT accuracy — addressable by smarter search.
- **And reasoned with**: install a LEARNED rule and derive new facts (JEP-130, Datalog-style); a full agent learns
  taxonomy + rule from observation, reasons, and acts (JEP-132).

## Where it is GENUINELY HARD (and why)
- **NOISY data**: a noise-tolerant threshold still collapses to chance by 10-20% label noise (JEP-133). REDUNDANCY
  rescues it but needs k~25 repeated observations at 30% noise (JEP-134).
- **THE KEY INSIGHT - closures COMPOUND errors**: a transitive closure (or any multi-step derivation) needs MANY
  constituent facts ALL correct; a single residual wrong fact corrupts the whole closure. So per-fact denoising must
  be NEAR-PERFECT, not just better-than-chance. This is why structure learning is fundamentally harder than single-
  fact prediction under noise, and why it needs heavy redundancy.
- **SPARSE data**: a violation you never observe can't be detected (JEP-128) — sparse data is fundamentally
  ambiguous between transitive and non-transitive; a prior just sets the default (no free lunch).

## Sparse is SOLVED by ACTIVE querying (JEP-135)
The sparse-PASSIVE limit dissolves if the learner can CHOOSE what to observe: active querying (binary-insertion
sort = choosing the informative comparisons) determines a transitive order in ~n log n queries (1.00), vs the ~n^2
passive budget — 12x speedup at n=64, growing with n. Lesson: "not enough data" is often really "not enough of the
RIGHT data" — choose informative queries instead of waiting for them. (Caveat: noiseless oracle; under noise you
repeat queries per JEP-134; detecting a single long cycle needs path-tracing, not random triples.)

## The genuine open problem
Structure learning from NOISY + SPARSE + ONE-SHOT data simultaneously (as humans do) — needs structural PRIORS +
ACTIVE QUERYING + incremental HIGH-CONFIDENCE bootstrapping TOGETHER. Plus LEARNING the base relations themselves
(here given), which needs perceiving INTERACTIONS, not just objects.

## A calibration lesson about predicting difficulty
Measured against my own predictions, I was miscalibrated on structure learning in BOTH directions: I OVER-predicted
difficulty on CLEAN data (exact-match signals are strong - 3x over JEP-129/131) and UNDER-predicted it on NOISY
data (closures compound errors - 2x under JEP-133/134). Lesson: clean-data structure inference is easier than
intuition says (strong identifiability); noisy-data structure inference is harder (compounding). Don't trust the
intuition either way - measure. Established methods throughout (consistency inference, ILP/rule-discovery, majority-
vote denoising); named; no novelty.

## THE deep cross-cutting insight: COMPOUNDING and its cure (JEP-134/136/137/138)
Both LEARNING structure and REASONING over it are MULTI-STEP inference, and multi-step inference COMPOUNDS errors:
a k-step derivation (a transitive closure, an insertion sort, a k-hop is_a chain) is correct only if ALL k steps
are, so under per-step noise p, reliability decays ~(1-p)^k — EXPONENTIALLY with inferential DEPTH.
- Measured: noisy structure LEARNING needs redundancy growing with structure size (JEP-134/136); the engine's
  multi-hop REASONING degrades faster at greater depth (JEP-137, depth1 0.90 -> depth4 0.52 @noise0.1).
- THE CURE: REDUNDANT independent paths + aggregation. A DAG (many paths to a conclusion) error-corrects broken
  edges — a true conclusion survives if ANY path does (JEP-138, recall 0.89 vs a chain's 0.73 @20% noise) — at a
  precision cost (spurious paths -> more false positives).
- LESSON: human-like robust inference under noise is NOT a single deep clean chain; it is MANY independent
  derivation paths + voting, with redundancy/error-correction scaling with inferential depth. This is why brittle
  long chains fail and why brains/robust systems use massively redundant, re-derived, cross-checked inference.

## The complete inference-robustness picture: CHAINING vs AGGREGATION (JEP-137/138/140)
- **CHAINING compounds** (deduction multi-hop, transitive closures, insertion sorts): a k-step result needs ALL k
  steps correct -> reliability ~(1-p)^k, fragile, decays exponentially with DEPTH (JEP-137).
- **AGGREGATION averages** (induction = majority over instances; redundant DAG paths = vote over derivations):
  tolerates noise up to ~50% where the majority flips (JEP-140: induction 0.91 @30% noise vs deduction depth-4
  0.20).
- **The cure for chaining fragility IS aggregation**: many independent derivation paths + voting (JEP-138) makes
  brittle deduction robust (recall), at a precision cost. Confidence-via-path-count, however, does NOT improve
  precision (JEP-139 NULL) — redundancy helps RECALL, not precision.
- LESSON: human-like robust inference under noise = AGGREGATION + REDUNDANCY, not deep clean chains. Match the
  inference SHAPE to the noise: if data is noisy, prefer wide aggregation over deep chaining.

## One-shot / minimal data: PRIORS help, with a bias cost (JEP-151)
The "needs priors" piece of the noisy/sparse/one-shot frontier, measured: an Occam (simplicity) prior on minimal
ambiguous data picks the true structure FAR better than random-among-consistent WHEN the true structure is SIMPLE
(depth-1: 0.87 vs 0.17 from ONE example) but WORSE when it is genuinely COMPLEX (depth-3: 0.06 vs 0.18, under-fits).
NO FREE LUNCH: priors buy one-shot generalization ONLY when the world matches the prior; bias is the price. So the
COMPLETE structure-learning picture: clean=easy (search-cost), noisy=hard (closures compound; redundancy at cost),
sparse-passive=ambiguous, sparse=ACTIVE-querying solves (n log n), one-shot=PRIORS help (Occam) with a bias cost.
The genuine open problem (all of noisy+sparse+one-shot+unknown-prior at once, as humans handle) remains — it needs
the RIGHT prior, which itself must be learned/meta-learned. Established (Occam/MDL, Bayesian Occam, no-free-lunch).

## Meta-learning the prior (JEP-152) — and the exhaustive close
The deepest piece ("learn the prior itself"): meta-learning a domain's complexity prior from a few structures HELPS
one-shot inference of a new structure RELATIVELY (beats fixed-Occam 3.6x on a consistently-deep domain) but doesn't
SOLVE it absolutely (0.18 — one example of a deep structure is under-determined even with the right prior), and is
uninformative on heterogeneous domains (no regularity to learn).

### THE EXHAUSTIVE STRUCTURE-LEARNING MAP (JEP-128..152), reframing the JEP-69/70 NULL
| regime | learnable? | how / why |
|--------|-----------|-----------|
| clean | YES, easily | uniquely identifiable (exact match); limit is SEARCH COST (|R|^depth) |
| noisy | HARD | closures COMPOUND errors; redundancy rescues at cost (k~size) |
| sparse, passive | ambiguous | a violation never observed can't be detected |
| sparse, ACTIVE | YES | choose informative queries (sort = n log n) |
| one-shot | priors help | Occam helps simple-true, hurts complex-true (no free lunch) |
| meta-prior | partial | learn the prior from a consistent domain; doesn't solve deep one-shot |

So "can't learn arbitrary structure" was wrong for clean data and a partial truth for noisy/sparse/one-shot. The
genuine residual: human-level learning combines compositional REUSE + ACTIVE querying + the RIGHT (meta-learned)
prior SIMULTANEOUSLY, from noisy sparse one-shot data — no single ingredient suffices. Established methods
throughout (consistency inference, ILP, active learning, Occam/MDL, hierarchical Bayes); named; no novelty.

## THE FULL RECIPE + the universal unification (JEP-153/154/154b) — capstone
Combining the ingredients on the genuinely-hard regime (deep target + 15% noise + minimal data) gives the complete,
measured recipe for human-like EFFICIENT structure learning — and a universal insight.

### The recipe (each ingredient fixes a distinct binding constraint)
1. **Compositional REUSE** fixes the SEARCH constraint: searching over already-learned SUB-RULES instead of base
   relations collapses |R|^depth -> |subrules|^2 (scratch 0.00 -> reuse 0.54 from one noisy example; JEP-153 ~5x
   sample-complexity cut). This is the DOMINANT ingredient.
2. **Few-shot REDUNDANCY** (active querying that also buys repeats) beats NOISE: accuracy -> 0.99 as k grows.
3. **NOISE-TOLERANT SOFT aggregation** is the CRITICAL ENABLER of (2): with SOFT best-overlap scoring, more data
   helps (0.55->0.99 as k:1->20); with STRICT consistency (obs subset of candidate), more noisy data is ACTIVELY
   HARMFUL (0.55->0.06) because one bad observation falsely eliminates the true hypothesis.
4. The right **PRIOR** (Occam/meta-learned) adds a little more (JEP-151/152).

### The universal unification
This is the SAME CHAINING-vs-AGGREGATION lesson (JEP-137/138/140) — now shown to govern LEARNING as well as
REASONING. Hard consistency (a strict deductive chain, or a strict subset test) is FRAGILE under noise: one broken
step/observation breaks the whole result. SOFT aggregation (voting over paths, overlap counts, majority denoising)
is ROBUST: it averages noise out. The compounding insight is UNIVERSAL across multi-step inference AND structure
learning. Human-like robust cognition under noise = soft redundant aggregation everywhere, never brittle hard chains.

### A calibration lesson recorded honestly
I MISSED JEP-154 by not applying my OWN prior finding (JEP-134): I used strict consistency under noise and predicted
few-shot would help, when it hurt. The discipline is to CARRY FORWARD lessons, not re-learn them — the predict-
calibrate value isn't just per-experiment accuracy, it's accumulating a model that doesn't repeat known mistakes.
Established throughout (robust estimation, M-estimators, compositional/transfer learning, majority denoising); named.

## REFINEMENT: the compounding EXPONENT is representation-dependent (JEP-158)
The chaining-vs-aggregation insight has a representation-dependent EXPONENT, measured:
- SYMBOLIC, independent edges: reliability ~ (1-p)^k — EXPONENTIAL decay with depth (each discrete edge can fail
  independently; one wrong edge breaks the chain). The most fragile.
- CONTINUOUS/distributed, INDEPENDENT per-hop errors: error ~ f*sqrt(k) — SUB-LINEAR (random walk: errors partially
  CANCEL, and in high-D are nearly orthogonal to the discriminating lattice direction). ROBUST — continuous reps
  AVERAGE independent noise. (A concrete reason distributed/learned representations help.)
- CONTINUOUS, SYSTEMATIC/shared bias: error ~ k*bias — LINEAR (a reused operator's bias accumulates coherently).
  Fragile, but less than exponential.
CURE (universal): per-hop nearest-entity / attractor CLEANUP (the substrate Hopfield, JEP-4) re-anchors each hop and
cures BOTH continuous cases. So: chained inference compounds, but HOW FAST depends on the representation, and
aggregation/cleanup is the universal cure. CALIBRATION: I predicted continuous compounds 'like symbolic' — WRONG
(direction), and hit a CARDINAL repeated bug (D-dim isotropic noise has magnitude sigma*sqrt(D); always scale by
1/sqrt(D)). Measure, don't carry intuition across representations. Established (random-walk error, cleanup memory).

## REDUNDANCY unifies robustness AND generalization (JEP-176/177)
Bridging the symbolic learn-from-prose pipeline to the joint-embedding pillar surfaced a deeper unification of the
redundancy theme. The learned embedding faithfully reconstructs a prose-learned taxonomy's is_a closure IN-SAMPLE
(order 0.99 at 24 concepts — small scale is fine for reconstruction; the JEP-52 <50 caveat is about HELD-OUT
generalization, NOT in-sample — distinguish them). But held-out is-a GENERALIZATION is ILL-POSED on a TREE: every
non-root concept has exactly ONE parent edge, so holding it out ISOLATES the concept and NEITHER symbolic closure NOR
the embedding can infer it. Generalization needs REDUNDANT structure (a DAG / multi-parent / sibling regularity /
features) — the geometry infers an unstated relation only from OTHER kept relations.
THE UNIFICATION: REDUNDANCY is the common requirement for BOTH
- ROBUST INFERENCE under noise (error-correct a broken chain via independent paths — JEP-138/140), and
- GENERALIZATION (infer a held-out edge from independent related structure — JEP-177).
A single-path TREE supports neither; a many-path DAG supports both. Robustness and generalization are two faces of
the same structural property — redundancy. (And symbolic closure vs learned embedding are COMPLEMENTARY: symbolic =
exact on known/derivable structure, embedding = generalizes to unstated structure given redundancy + scale.)
Established (transitive-closure inference, order/poincare embeddings, error-correcting redundancy); named; no novelty.
