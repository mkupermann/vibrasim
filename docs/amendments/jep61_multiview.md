# JEP-61 — multi-view fusion for concept formation: pixels + shape vs each alone (real Fashion-MNIST)

## Motivation
JEP-60: shape features group footwear where pixels fail; pixels may capture other structure shape misses. Test
whether FUSING two real feature views (pixels + shape) gives better FUNCTIONAL concept formation than either alone
- a concrete, non-contrived multi-view test on real data, toward the multimodal-grounding path (JEP-60 frontier).

## Pre-registration (locked BEFORE run)
- Fashion-MNIST class means. Functional ground-truth groups: TOPS{t-shirt,pullover,coat,shirt}, LOWER{trouser,
  dress}, FOOTWEAR{sandal,sneaker,ankle_boot}, ACCESSORY{bag}. Cluster into 4 with: pixels, shape, fusion
  (z-scored concat). Metric = cluster PURITY vs functional groups (fraction in their cluster's majority group).
- Bar: fusion purity >= max(pixels, shape) purity AND fusion >= 0.8. PASS = multi-view fusion >= best single view
  (concrete multi-view benefit). NULL otherwise. Established (multi-view clustering), named as such.

## Result — NULL (naive fusion HURTS; the right single view is best) - an important honest finding
| view | functional purity vs ground-truth |
|------|-----------------------------------|
| pixels (784-d) | 0.90 |
| shape (56-d) | 1.00 |
| naive fusion (z-concat) | 0.90 |

**VERDICT: NULL - and it strengthens the story.** Naive multi-view fusion does NOT beat the best single view: it
DROPS from shape's 1.00 to 0.90, because the noisier high-dimensional PIXEL view drags the concatenation toward
its own error (ankle_boot~bag). So MORE MODALITIES IS NOT AUTOMATICALLY BETTER - naive concat lets the weaker/
noisier view dominate. The honest path to functional concepts is the RIGHT invariance-capturing FEATURE, not
adding views: shape ALONE achieves PERFECT (1.00) functional grouping on Fashion-MNIST (tops/lower/footwear/
accessory all correct), unsupervised. This is consistent with JEP-46 (more isn't better; the RIGHT thing is) and
refines JEP-60: for Fashion-MNIST the visual->functional gap is FULLY bridged by choosing shape features - no
multimodal signal needed because function correlates with shape. To benefit from multiple views you'd need
QUALITY-WEIGHTED fusion (know which view is better), not naive concat. The residual frontier (functions
uncorrelated with ANY visual invariance) still needs non-visual signal. Established (multi-view clustering),
named as such.
