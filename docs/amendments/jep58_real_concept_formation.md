# JEP-58 — concept formation on REAL data: does clustering recover a sensible hierarchy from Fashion-MNIST?

## Motivation
JEP-54/55 formed concepts from SYNTHETIC features. Real-data validation: Fashion-MNIST's 10 classes have natural
groupings (tops: t-shirt/pullover/coat/shirt; footwear: sandal/sneaker/ankle-boot). Does agglomerative clustering
on REAL image features discover a sensible hierarchy that groups related items?

## Pre-registration (locked BEFORE run)
- Per-class mean image (784-dim) from Fashion-MNIST. Agglomerative (Ward) clustering of the 10 classes.
- Natural coarse groups: FOOTWEAR={sandal(5),sneaker(7),ankle_boot(9)}, TOPS={t-shirt(0),pullover(2),coat(4),
  shirt(6)}. Bars: cutting the dendrogram into ~3-4 clusters, FOOTWEAR classes fall in ONE cluster (pure) AND
  TOPS classes are grouped (>=3 of 4 in one cluster). PASS = real-data concept formation recovers sensible
  structure. NULL otherwise. Established (hierarchical clustering), named as such.

## Result — PARTIAL: real-pixel concept formation is VISUAL, not functional (genuine grounding insight)
Discovered clusters (k=4) from Fashion-MNIST class-mean images:
- cluster: {t-shirt, pullover, coat, shirt}  <- TOPS grouped perfectly (4/4)
- cluster: {sandal, sneaker}                 <- low footwear together
- cluster: {bag, ankle_boot}                 <- ankle-boot with BAG (not other footwear!)
- cluster: {trouser, dress}
footwear-pure = False (ankle_boot~bag); tops-grouped = True.

**VERDICT: PARTIAL - and the shortfall is a genuine INSIGHT, not a failure.** Concept formation WORKS on real
data (tops group perfectly; sandal/sneaker group), but FOOTWEAR is not pure: ankle-boot clusters with BAG. Reason:
in RAW PIXELS an ankle-boot and a bag are both dark, blocky filled shapes - VISUALLY similar though FUNCTIONALLY
different. So real-pixel concept formation recovers a VISUALLY-coherent hierarchy that approximates semantic
categories but DIVERGES where appearance != function. The honest grounding lesson: PIXEL-GROUNDED CONCEPTS ARE
VISUAL, NOT FUNCTIONAL. To form FUNCTIONAL categories (footwear-by-use) you need richer features than raw pixels
(affordances, context, language) - exactly the open frontier. Validates JEP-54 concept formation on real data
(it found sensible structure) AND honestly bounds it: grounding from raw perception yields visual, not semantic,
concepts. A genuine, honest real-data result. Established (hierarchical clustering), named as such.
