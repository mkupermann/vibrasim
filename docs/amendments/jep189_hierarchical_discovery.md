# JEP-189 — hierarchical concept discovery from REAL images (does visual clustering recover a taxonomy?)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 agglomerative clustering recovers SOME visual super-structure (footwear vs tops) but imperfectly; sub-clusters
  recover individual classes at ~0.8 purity; the top split partially separates. Grounding the discovered hierarchy
  enables multi-hop reasoning. Honest finding: hierarchical visual discovery is partial.

## Result — HIT (qualitative) + an EMERGENT insight; sub-level magnitude over-predicted
Hierarchically clustered Fashion-MNIST (6 classes, 2 super-categories tops{tshirt,pullover,coat} / footwear{sandal,
sneaker,ankleboot}), raw pixels:
- TOP-level (2 clusters) purity vs tops/footwear: 0.87
- SUB-level (6 clusters) purity vs individual classes: 0.62
- multi-hop over the DISCOVERED hierarchy (perceive -> discovered sub -> discovered super -> garment) connects (1.00,
  a CONNECTIVITY check — all classes are garments, so this confirms the grounded hierarchy wires up, NOT a
  discrimination claim; the purities are the genuine measures).
HIT on the qualitative core (hierarchical visual discovery is PARTIAL; the coarse super-structure emerges). EMERGENT
INSIGHT (not predicted): the COARSE super-categories are MORE visually separable (0.87) than the FINE individual
classes (0.62) — counter to the naive expectation. In pixel space, shape-based super-categories (footwear vs tops)
separate cleanly while appearance-similar fine classes (tshirt/pullover/coat) overlap. So visual clustering recovers
a sensible COARSE taxonomy better than fine distinctions — visual similarity aligns with COARSE semantic structure
but diverges at the fine level (the JEP-58/61 visual-vs-functional gap, now at the hierarchy level). MAGNITUDE MISS:
I predicted sub-level ~0.8, got 0.62 (Fashion-MNIST fine classes overlap more in pixel space than expected). The
developmental loop extends from FLAT concept discovery (JEP-179/187) to HIERARCHICAL discovery, grounded + reasoned
over. Prediction HIT (qualitative); tally 78/105. Established (hierarchical agglomerative clustering); named; no novelty.
