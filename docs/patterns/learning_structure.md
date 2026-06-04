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
