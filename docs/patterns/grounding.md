# Pattern: grounding concepts in perception — what the EQMOD-4 grounding thread learned (JEP-54..63)

How to form concepts from experience and use them to reason and act, and where it breaks. Each insight is from a
specific rung; methods are established (clustering, SR/TD, Poincare embeddings), the discipline is the point.

## The closed loop works (conditionally)
The full **experience -> form concepts -> reason -> act** loop closes: cluster feature observations into a
hierarchy, fit a reasoner (IS-A) on the SELF-DISCOVERED taxonomy, and plan to discovered categories. Works on
synthetic features (JEP-55: 1.00) AND real Fashion-MNIST images (JEP-59: 0.94). Nothing given but features.

## 1. Concept formation is FEATURE-GEOMETRY-dependent (JEP-54)
Clustering recovers a hierarchy only when COARSE categories are featurally distinctive (dominate the variance).
With equal-weight ancestor features, fine variation dominates and coarse structure is lost (purity 0.75); with
generality-weighted (coarse-distinctive) features it works (1.00). Discovering structure from experience is NOT
automatic - it depends on whether the feature geometry makes the structure you want dominant.

## 2. Raw-perception concepts are VISUAL, not functional (JEP-58)
Clustering raw pixels groups by APPEARANCE: Fashion-MNIST ankle-boot clusters with BAG (both dark, blocky), not
with other footwear. Pixel-grounded concepts capture how things LOOK, not what they're FOR.

## 3. The right FEATURE bridges visual->functional - when function correlates with an invariance (JEP-60)
Shape-profile features (low, sole-at-bottom) group all footwear correctly, UNSUPERVISED, where pixels failed. So
the visual-functional gap is partly about WHICH features. BOUND: this works because footwear's function
correlates with a capturable shape invariance. For functions UNCORRELATED with any visual feature (tools:
hammer/saw look nothing alike), no visual feature recovers the category - that needs non-visual signal
(interaction, language). Choose features that capture the invariance your target structure rides on.

## 4. MORE views is NOT better; naive fusion can HURT (JEP-61)
Naive multi-view fusion (z-concat pixels+shape) DROPPED functional purity from shape's 1.00 to 0.90 - the noisier
784-d pixel view dominated the 56-d shape view and reintroduced its error. The RIGHT single view beat fusion.
Benefiting from multiple views needs QUALITY-WEIGHTED fusion (knowing which view is better), not concatenation.
(Same shape as JEP-46: more/bigger isn't better; the RIGHT thing is.)

## 5. The loop is FORGIVING of formation errors (JEP-56)
Grounded planning success slightly EXCEEDS concept-formation purity at every noise level: navigating to the
nearest grounded entity reaches a majority-(correct-)branch member even when a discovered category is impure. So
MINORITY-NOISE in the formed concepts gets ABSORBED downstream (contrast JEP-46, where CONFIDENT-WRONG errors got
amplified - see honest_evaluation.md #8).

## 6. Appearance-independent functions come from INTERACTION/AFFORDANCES (JEP-62)
When function is UNCORRELATED with appearance, clustering on AFFORDANCE outcomes (what interacting reveals: a
container holds, a tool breaks, food is consumed) recovers the functional categories perfectly (1.00) where
appearance is at chance. The agent must ACT to discover function it cannot see. So FUNCTIONAL concepts come from
EITHER the right visual invariance (when function correlates with appearance, #3) OR interaction/affordances
(when it does not, this) - a complete account. The FULL loop with functional concepts (act-to-learn-function ->
form categories -> recall to plan on functional goals) works end-to-end (JEP-63, 1.00) - learning by DOING.

## The honest frontier (mapped, not waved at)
Unsupervised perceptual concept formation reaches FUNCTIONAL categories WHEN function correlates with a capturable
visual invariance (pick the right features). The residual - functions independent of appearance - needs
non-visual signal: interaction/affordances, context, or language. That, plus grounding at scale and the real
substrate, is the open work. Everything here is toy-environment + real-features; not human-level understanding.

## 7. Self-taught grounding: observation -> structure -> meaning -> reasoning (JEP-113..118c)
The engine can learn its ENTIRE named taxonomy from raw observation + ambient language with ZERO told facts:
perceive (features) -> CLUSTER into a hierarchy (structure, JEP-113) -> CROSS-SITUATIONAL word learning (meaning
without clean labels, Yu-Smith 2007, JEP-116) -> wire IS-A from the cluster hierarchy -> reason/describe (JEP-117,
"A dog is a mammal" learned not told). It works END-TO-END in the favorable regime.

### The honest boundary (hard-won across 117->118->118b->118c)
- **Structure discovery is robust to perceptual overlap** but needs coarse-distinctive features (JEP-54 condition);
  at extreme overlap (sigma~1.5) clustering itself degrades.
- **Basic/instance-level naming is robust** (cross-situational PMI works: basic words are exclusive to a tight
  cluster).
- **Superordinate-level naming is the fragile part.** PMI SATURATES for any word exclusively associated with a
  cluster (PMI=log(1/P(cl))), so 'bird' and 'robin' have IDENTICAL PMI for the bird-super-cluster -> co-occurrence
  UNDERDETERMINES hierarchy LEVELS. (This is why child word-learning needs the taxonomic/basic-level constraints,
  Rosch/Markman.) JEP-117's apparent super-naming success was partly TIE-BREAK LUCK.
- **The correct criterion is LCA-of-extension**: a word names the SMALLEST cluster containing (almost) all its
  instances (coverage AND specificity high). 'robin'->robin-sub; 'bird'->the super-cluster. Naive PMI-max FAILED
  (JEP-118b, 0.00 - superordinate words tie across levels too). LCA fixes it AT ADEQUATE EXPOSURE.
- **Residual real limits**: rare superordinate words (heard ~20% of scenes) can't be learned reliably (coverage too
  sparse - a genuine EXPOSURE limit, not a method flaw); heavy concept overlap breaks the clustering.

### The methodological lesson
A fragile success (117) was corrected by stress-testing (118), a proposed fix FAILED and was owned (118b), and the
principled criterion (118c) was found AND bounded. Stress-test your successes; a 1.00 in one regime is not a law.

## 8. Learning relational STRUCTURE from observation (JEP-128..130) — advancing the JEP-69/70 frontier
Beyond learning FACTS, the engine can learn the STRUCTURE relations have, from observation:
- **Transitivity** (JEP-128): infer a relation is transitive iff its transitive-closure CONTRADICTS no observed-
  false pair (a total order is transitive; a cyclic tournament's closure over-predicts -> not). Reliable when
  observation is DENSE; a violating triple you never observe can't be detected (a fundamental DATA limit, not a
  method flaw). Same shape as the JEP-118c exposure limit.
- **Composition rules** (JEP-129): DISCOVER 'uncle = parent o sibling' by searching candidate compositions R1 o R2
  and picking the one whose result best matches observed target facts (F1). ROBUST: the correct composition's F1
  dominates spurious ones even with 15 distractor relations + 20% label noise. (I over-predicted the difficulty —
  spurious matches don't fool it when the signal is real; cf. JEP-76/107 non-materializing boundaries.)
- **Reason with learned structure** (JEP-130): install the learned rule (add_rule) and DERIVE new facts (Datalog-
  style relation_holds) — structure-learning + reasoning unified.

The honest open frontier: deeper/longer rules (3+ relations -> combinatorial), LEARNING the base relations
themselves (here given), and large relation vocabularies. But within 2-relation composition over given relations,
structure is LEARNABLE from observation, robustly — a genuine step past the JEP-69/70 NULL. Lesson: "can't learn
arbitrary structure" was too pessimistic; CONSISTENCY and RULE-MATCH signals make a lot of structure learnable when
the data is adequate. Established (consistency-based inference, ILP/rule-discovery simplest form), named.
