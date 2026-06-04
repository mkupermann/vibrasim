# JEP-60 — does FEATURE CHOICE bridge the visual-functional gap? (shape profiles vs raw pixels)

## Motivation
JEP-58: raw-pixel concept formation grouped ankle-boot with BAG (both dark blocky), splitting footwear. Question:
is the visual-functional gap fundamental, or partly about WHICH features? Footwear shares a distinctive SHAPE
(low, sole-at-bottom). Test concept formation with SHAPE-PROFILE features (row/column sums) vs raw pixels - does
shape group footwear (sandal/sneaker/ankle-boot) where pixels did not? Derived features, NOT supervision.

## Pre-registration (locked BEFORE run)
- Fashion-MNIST class means. Features: (a) raw pixels (784), (b) shape profiles = row-sums + column-sums (56).
  Agglomerative clustering; check if FOOTWEAR={sandal,sneaker,ankle_boot} forms one cluster (k=4).
- Bar: shape features put all 3 footwear in ONE cluster (where pixels did not). PASS = feature choice partly
  bridges the gap (shape > pixels for functional footwear grouping). NULL if shape also splits footwear.
  Established (hierarchical clustering, shape features), named as such.

## Result — PASS (feature choice partly bridges the gap; honestly bounded)
| features | footwear (sandal/sneaker/ankle_boot) |
|----------|--------------------------------------|
| raw pixels | SPLIT (ankle_boot clustered with bag) |
| shape profiles (row+col sums) | ONE cluster (bag separate) |

**VERDICT: PASS - feature choice bridges part of the gap, WITHOUT supervision.** Shape-profile features group
all 3 footwear where raw pixels split them (ankle_boot~bag), with bag correctly separated. So the JEP-58 visual-
functional gap is PARTLY about WHICH features: shape captures footwear's functional commonality (low, sole-at-
bottom) that pixels miss - unsupervised, derived features move concepts TOWARD functional. HONEST BOUND: this
works because footwear's FUNCTION CORRELATES with a capturable visual invariance (shape). For functions
UNCORRELATED with any visual feature (e.g. "tools": hammer/screwdriver/saw look nothing alike), NO visual feature
recovers the functional category - that needs NON-VISUAL signal (interaction, language). So the refined honest
story: unsupervised perceptual concept formation can reach FUNCTIONAL categories WHEN function correlates with a
capturable invariance (pick the right features); otherwise it stays visual and needs external signal. Hopeful and
bounded. Established (shape features, hierarchical clustering), named as such.

## Perceptual grounding thread (JEP-58/59/60) conclusion
- Raw-pixel concept formation is VISUAL not functional (JEP-58: ankle_boot~bag).
- The complete grounded loop works on real perception (JEP-59: 0.94).
- FEATURE CHOICE partly bridges visual->functional WITHOUT supervision, WHEN function correlates with a
  capturable invariance (JEP-60: shape groups footwear). Functions uncorrelated with appearance need non-visual
  signal. The path toward functional grounding: better invariance-capturing features + (for the rest) multimodal/
  interactive/linguistic signal - the open frontier, now mapped concretely.
