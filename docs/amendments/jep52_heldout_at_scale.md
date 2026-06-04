# JEP-52 — clarify the held-out generalization limitation: calibrated is_a RECALL at scale

## Motivation
JEP-51 found held-out calibrated is_a recall ~0.4 on a SMALL (30-node) taxonomy. But my scale measurements
(JEP-29b 0.86, JEP-42) reported the DIRECTION metric or ORDER embeddings - I never cleanly measured CALIBRATED
POINCARE is_a held-out RECALL at scale. This clarifies whether the held-out limitation is small-taxonomy-specific
or broader.

## Pre-registration (locked BEFORE run)
- WordNet carnivore 366. Poincare, hold out 30% ancestor pairs. Measure held-out CALIBRATED is_a TPR (recall on
  held-out true ancestors), TNR, balanced acc - across taxonomy sizes (subtree truncations: ~50, ~150, 366).
- CHARACTERIZATION: report held-out calibrated is_a recall vs size. If recall rises with size toward usable
  levels, the limitation is small-taxonomy-specific. If it stays low, the held-out generalization issue is broad
  and the deliverable is a KNOWN-taxonomy lookup tool, not a link predictor. Established methods, named.

## Result — the held-out limitation is SMALL-TAXONOMY-specific (bounded precisely)
| taxonomy size | held-out is_a TPR | TNR | balanced acc |
|---------------|-------------------|-----|--------------|
| 30 (JEP-51) | ~0.4 | - | poor |
| 50 | 0.763 | 0.974 | 0.868 |
| 150 | 0.691 | 0.980 | 0.836 |
| 366 | 0.729 | 0.979 | 0.854 |

**VERDICT: limitation BOUNDED + reassuring.** Held-out calibrated is_a recall jumps from ~0.4 (30 nodes) to
~0.73 (50+ nodes) and holds ~0.7-0.76 through 366, with balanced acc ~0.84-0.87. So the JEP-51 held-out
generalization weakness is SPECIFIC to VERY SMALL taxonomies (<~50 nodes); at realistic scale the deliverable
generalizes reasonably to UNSEEN is_a relations (balanced 0.85). Also note TPR (0.73) << TNR (0.98): the
calibrated classifier is CONSERVATIVE on held-out - misses ~30% of true ancestors but rarely false-positives.
That high precision is exactly why poincare is best for GROUNDING (JEP-46/47) - it grounds few wrong entities.
Net honest statement: the concept reasoner is a reliable lookup over a known taxonomy (in-sample ~1.0) AND a
decent link predictor at moderate+ scale (>=50 nodes, balanced ~0.85); only on tiny taxonomies is unseen-relation
prediction weak. The earlier README caveat (held-out needs scale) is correct and now QUANTIFIED. Established
methods (Nickel-Kiela 2017), named as such.
