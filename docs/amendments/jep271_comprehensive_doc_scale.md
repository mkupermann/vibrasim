# JEP-271 — comprehensive document-scale validation across ALL construction profiles (post 254..270)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the fully-hardened engine handles a comprehensive document spanning ALL 6 construction profiles (definitional,
  spatial, mereological, possession, ability, temporal-multiword, object-WH, ...) + every relation type at >=0.9.

## Result — PASS (HIT): 16/16 = 1.00
Read a fresh 19-sentence document exercising EVERY construction added in JEP-254..270 + every relation type; checked
16 ground-truth facts/answers: definitional is-a (dog->canine->mammal->animal via 'defined as'), 'means', 'such as',
adjectival property, part-of, mereological verb, INHERITED possession ('does a puppy have a heart?'), ability can/
cannot, passive causal, object-side open-relation WH ('what does a dog chase?'), comparison, spatial 'in', multi-word
verb-phrase temporal ('was signed before') + transitive, numeric. 16/16 = 1.00 (vs JEP-266's 0.94, which predated
267..270 and the >=2-occ open-relation case). The cumulative prose hardening (254..270, 16 fixes across 6 construction
profiles / 5 domains) achieves PERFECT recall on a comprehensive multi-construction document with multi-hop chains,
ROBUST (JEP-265, 0/4000), 110 unit tests. Prediction HIT; tally 150/186. Established (document-scale evaluation),
named; no novelty. The real-prose extractor now covers the common declarative construction space; the bound is the
NER/multi-word-entity wall (proper-noun caps, multi-word named entities, multi-word concept coreference) = no-pretrained.
