# JEP-29 — concept reasoner scales to a REAL WordNet taxonomy (carnivore subtree, 366 concepts)

## Pre-registration (locked BEFORE run)
- Extract the carnivore.n.01 hyponym closure from WordNet (~366 real synsets) as an IS-A taxonomy.
- Fit the mixed-curvature ConceptReasoner (Euclid 4D + hyperbolic 10D). Hold out 30% of ancestor pairs; train on
  the rest.
- Bars: held-out IS-A direction accuracy >= 0.85 (generalizes at real scale) AND real-synset sanity queries
  correct (dog is-a carnivore True, carnivore is-a dog False, etc). PASS = the reasoning result holds at ~5x
  scale on REAL data. NULL otherwise. WordNet + Poincare embeddings (Nickel-Kiela 2017) established - named.

## Result — NULL (toy result does NOT transfer to real 366-concept scale with modest training)
| metric | 77-concept toy (JEP-28b) | 366-concept WordNet (JEP-29) |
|--------|--------------------------|------------------------------|
| trained IS-A direction acc | 0.78 | 0.712 |
| HELD-OUT IS-A direction acc | 0.911 | 0.681 |
| sanity queries | correct | correct (but EASY cases) |

**VERDICT: NULL - honest scaling failure.** On a REAL 366-concept WordNet carnivore taxonomy, held-out IS-A
direction accuracy DROPS to 0.681 (vs 0.911 on the 77-concept toy) - barely above chance. The sanity queries
(dog is-a carnivore, etc.) all pass, but those are EASY/clear cases that MASK the aggregate degradation - which
is precisely why aggregate accuracy, not cherry-picked queries, is the honest metric. Also nearest('dog')
returned alphabetically-first A-words (aardwolf, afghan_hound, ...), suggesting the EUCLIDEAN relatedness
embedding is also poorly trained at scale (deep-tree graph distances span ~20 and the single-scale stress fit
collapses many leaves). So the toy-scale reasoning result does NOT automatically transfer to real scale with my
modest training budget (10D, 4000 iters). Nickel-Kiela used much larger embeddings + careful optimization. Test
whether more compute recovers it -> JEP-29b; if not, the approach has a real scaling cost at this budget. Honest
caveat on the JEP-28 concept-reasoner deliverable: validated on a curated toy, NOT yet at real scale. Bars locked.
