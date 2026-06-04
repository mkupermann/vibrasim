# Pattern: grounding concepts in perception — what the EQMOD-4 grounding thread learned (JEP-54..61)

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

## The honest frontier (mapped, not waved at)
Unsupervised perceptual concept formation reaches FUNCTIONAL categories WHEN function correlates with a capturable
visual invariance (pick the right features). The residual - functions independent of appearance - needs
non-visual signal: interaction/affordances, context, or language. That, plus grounding at scale and the real
substrate, is the open work. Everything here is toy-environment + real-features; not human-level understanding.
