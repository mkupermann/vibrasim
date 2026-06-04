# JEP-1 — Toy JEPA: predict a masked element's REPRESENTATION from context (learn world structure)

## Motivation
Demonstrate the JEPA principle (LeCun): learn by predicting in REPRESENTATION space. A structured latent world
(8x8 grid); context = an item + a direction; target = the neighbouring item. A JEPA predictor maps context
embeddings -> the TARGET's embedding (in representation space, NOT raw coords). If it learns the world's
transition structure, it predicts held-out targets' embeddings whose nearest item is the correct one.

## Pre-registration (locked BEFORE run)
- 8x8 latent grid (64 cells); each cell embedded by a FIXED random MLP (the "representation", frozen target
  encoder). Context = (cell embedding, one-hot direction); target = neighbour cell's embedding.
- Train the predictor on a subset of (cell, dir) on TRAIN cells; test on HELD-OUT cells (disjoint).
- Metric: held-out hits@1 = predicted embedding's nearest grid cell == true neighbour. Baselines: COPY
  (predict context cell's own embedding), MEAN (predict average embedding).
- Bar: JEPA held-out hits@1 >= 0.7 AND >> baselines (it learned the transition structure in representation
  space, generalizing to unseen cells). NULL if it just memorizes / doesn't generalize.
