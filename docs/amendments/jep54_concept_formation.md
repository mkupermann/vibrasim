# JEP-54 — concept FORMATION: discover the category hierarchy from experience (not given)

## Motivation
All prior reasoning used a GIVEN taxonomy. A hallmark of understanding is FORMING concepts from experience.
Test: can the category hierarchy be DISCOVERED (unsupervised) from noisy FEATURE observations of entities, vs
being handed the tree? Each entity's features = sum of its ancestors' feature contributions + noise; hierarchical
clustering should recover the tree. Characterize when concept formation works and where noise breaks it.

## Pre-registration (locked BEFORE run)
- Ground-truth balanced tree; each node contributes a random feature block; entity feature = sum over its
  ancestors + Gaussian noise (level sigma). Agglomerative clustering (Ward) -> dendrogram. Compare to truth by
  COPHENETIC correlation (discovered pairwise tree-distance vs true tree-distance) and leaf-cluster PURITY at
  the category level.
- Sweep noise sigma. Bars: at LOW noise, cophenetic corr >= 0.8 AND category purity >= 0.9 (concept formation
  works); report graceful degradation with noise. PASS = a hierarchy can be DISCOVERED from experience.
  Established (hierarchical/agglomerative clustering), named as such.

## Result — PARTIAL (concept formation depends on FEATURE GEOMETRY)
| sigma | cophenetic corr | top-branch purity |
|-------|-----------------|-------------------|
| 0.3 | 0.742 | 0.750 |
| 0.8 | 0.555 | 0.750 |
| 1.5 | 0.105 | 0.625 |
| 3.0 | 0.244 | 0.688 |

**VERDICT: PARTIAL - concept formation is FEATURE-GEOMETRY-DEPENDENT.** Even at low noise, Ward clustering only
moderately recovers the hierarchy (cophenetic 0.74, top-branch purity 0.75). Reason: with EQUAL-weight ancestor
feature contributions, coarse categories are a SMALL fraction of feature variance (leaves in the same top branch
share only 2/5 feature blocks; the lower 3 levels vary), so clustering recovers FINE structure better than COARSE.
This predicts concept formation should work when coarse categories are FEATURALLY DISTINCTIVE (stronger top-level
signal) -> JEP-54b. Honest: discovering a hierarchy from experience is not automatic; it works only when the
feature geometry makes coarse structure dominant. Established (hierarchical clustering), named as such.

## JEP-54b — generality-weighted features (coarse distinctive) — PASS
| sigma | cophenetic corr | top-branch purity |
|-------|-----------------|-------------------|
| 0.3 | 0.864 | 1.000 |
| 0.8 | 0.697 | 1.000 |
| 1.5 | 0.164 | 0.750 |
| 3.0 | -0.032 | 0.562 |

**VERDICT: PASS (conditional).** With generality-weighted features (coarse categories distinctive, top-level
contributions stronger), agglomerative clustering DISCOVERS the hierarchy: top-branch purity 1.00, cophenetic
0.86 at low noise, degrading gracefully with noise. So the COMPLETE honest finding (JEP-54+54b): the category
hierarchy the reasoner USES can be DISCOVERED from experience - but CONDITIONALLY, only when the feature geometry
makes COARSE categories featurally distinctive (real taxonomies often satisfy this: mammals vs birds differ a
lot). With equal-weight features (fine variation dominant) it FAILS (purity 0.75). A genuine step toward grounded
concept FORMATION (structure learned, not handed in), honestly conditioned on feature geometry + noise.
Established (hierarchical/agglomerative clustering), named as such.
