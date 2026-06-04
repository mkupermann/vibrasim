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

## The genuine open problem
Structure learning from NOISY + SPARSE + ONE-SHOT data (as humans do) — needs more than data: structural PRIORS,
ACTIVE QUERYING, and incremental HIGH-CONFIDENCE bootstrapping. Plus LEARNING the base relations themselves (here
given), which needs perceiving INTERACTIONS, not just objects.

## A calibration lesson about predicting difficulty
Measured against my own predictions, I was miscalibrated on structure learning in BOTH directions: I OVER-predicted
difficulty on CLEAN data (exact-match signals are strong - 3x over JEP-129/131) and UNDER-predicted it on NOISY
data (closures compound errors - 2x under JEP-133/134). Lesson: clean-data structure inference is easier than
intuition says (strong identifiability); noisy-data structure inference is harder (compounding). Don't trust the
intuition either way - measure. Established methods throughout (consistency inference, ILP/rule-discovery, majority-
vote denoising); named; no novelty.
