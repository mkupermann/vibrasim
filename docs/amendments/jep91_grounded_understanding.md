# JEP-91 — grounded understanding: comprehension from PERCEPTION, not text (symbol grounding)

## Why
JEP-90's understanding machinery is TEXT-ONLY. Human-level (25yo) understanding grounds symbols in perception
(the symbol-grounding requirement; grounding thread JEP-54..63). This rung unifies them: the same parse->bind+
closure machinery answers comprehension from a PERCEPTUAL scene, with nouns recognized from noisy features.

## Setup
- Concepts have perceptual PROTOTYPES (feature vectors) + an IS-A graph (poodle->dog->animal->living_thing).
- A scene = (entity_a features, relation, entity_b features). Ground a,b to concepts by nearest prototype, then
  VSA-bind into a grounded fact.
- Comprehension from perception: (A) same-bag truth ("dog chases cat" vs "cat chases dog") verified against the
  grounded scene; (B) grounded multi-hop ("perceive a poodle -> is it an animal?") via IS-A closure on the
  grounded concept.

## Pre-registration (locked BEFORE run)
- (i) perceptual grounding accuracy under feature noise (sigma=0.6) >= 0.90.
- (ii) grounded comprehension: same-bag truth >= 0.90 AND grounded multi-hop >= 0.90.
- PASS = all three: the understanding machinery works GROUNDED in perception, not just on text symbols.
- HONEST BOUND up front: prototypes are given/learned-from-features (JEP-54..63), perception is toy, relation
  labels are given — full grounding (learning concepts AND relations from raw embodied experience) remains the
  frontier. Established (VSA/HRR, prototype perception, transitive closure), named; no novelty.

## Result — PASS (with an honest perception caveat)
- (i) perceptual grounding accuracy (sigma=0.6) = **1.00**
- (ii-A) grounded same-bag truth = **1.00**
- (ii-B) grounded multi-hop IS-A = **1.00**

**VERDICT: PASS.** The understanding machinery operates GROUNDED in perception: nouns recognized from noisy
features, then the SAME parse->bind+closure answers same-bag truth and grounded multi-hop inference from a
PERCEPTUAL scene, not text symbols. Symbol grounding is closed on the understanding pipeline (JEP-90 + JEP-54..63).
HONEST CAVEAT (self-flagged): grounding is 1.00 because the 9 prototypes are well-separated random 32-d vectors and
sigma=0.6 noise is small relative to their spacing — perception here is EASY. JEP-54/56 already characterized the
hard regime (overlapping concepts, high noise). The contribution is the GROUNDED PIPELINE, not hard perception.
HONEST BOUND: prototypes given/learned-from-features; relation labels given; toy perception. Learning concepts AND
relations from raw embodied experience (unsupervised) + robust parsing at scale = the open frontier. Established
(VSA/HRR, prototype perception, transitive closure), named; no novelty.
