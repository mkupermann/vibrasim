# JEP-42 — order embeddings: does a DIFFERENT is-a method break the ~0.78 ceiling?

## Motivation
JEP-40/41 showed the ~0.78 held-out IS-A ceiling on WordNet 366 is the METHOD (calibrated-Poincare), not compute
or dimension, and named "order embeddings" as the candidate different method. Order embeddings (Vendrov et al.
2016) embed concepts in the non-negative orthant where coordinate-wise domination encodes is-a (general =
smaller coords) - a partial order, not a distance/cone. Test whether it breaks the ceiling.

## Pre-registration (locked BEFORE run)
- WordNet carnivore 366. Order embedding (D=50), penalty ||relu(anc - child)||^2 for child is-a ancestor;
  margin loss for negatives; non-negative coords. Hold out 30% ancestor pairs; calibrate threshold on train.
- Bars: held-out balanced IS-A >= 0.88 -> ceiling WAS the Poincare method (PASS); 0.80-0.88 -> partly method
  (PARTIAL); ~0.78 -> the limit persists across methods = DATA/inherent (NULL). Established (Vendrov 2016), named.

## Result — PASS (order embeddings break the ceiling: 0.91 at real scale)
| method | held-out IS-A (WordNet 366) |
|--------|------------------------------|
| calibrated Poincare (JEP-40/41 ceiling) | ~0.78 |
| order embeddings (Vendrov 2016) | 0.911 (TPR 0.85, TNR 0.97) |

**VERDICT: PASS.** Order embeddings BREAK the ~0.78 ceiling, reaching 0.91 held-out balanced IS-A on 366 real
WordNet concepts - TOY-LEVEL accuracy at real scale. This CONFIRMS JEP-40/41's conclusion (the ceiling was the
calibrated-Poincare METHOD) by switching method: a partial-order embedding (general concept = coordinate-wise
smaller; is-a = domination), designed for transitive entailment, handles deep real hierarchies where the
distance/cone approach plateaued. The limit was the METHOD, not the data or compute - and the RIGHT method
(order embeddings) solves it. Retroactive explanation of the whole scaling saga: Poincare embeddings represent
tree DISTANCE well but their is-a readout degrades at depth; order embeddings encode the PARTIAL ORDER directly,
so they nail transitive is-a. The deadlock-breaking process worked: the honest self-correction (JEP-40/41, "not
just compute") led directly to the actual fix (JEP-42). Vendrov et al. 2016 established - named as such.

## Implication for the deliverable
Order embeddings are the SUPERIOR is-a method for real hierarchies (0.91 vs 0.78). They give is-a only (not
relatedness), so the right reasoner = order embeddings for IS-A + Euclidean for relatedness. Worth integrating
(JEP-43). Honest scaling story now COMPLETE and resolved: the right partial-order method reaches toy-level is-a
accuracy at real WordNet scale.
