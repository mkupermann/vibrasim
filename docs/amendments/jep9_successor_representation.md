# JEP-9 — Successor Representation (local TD) captures geodesic structure where contrastive failed

## Motivation
JEP-8/8b NULL: the simple contrastive rule learned a positional/Euclidean metric, not geodesic connectivity.
The established fix is the SUCCESSOR REPRESENTATION (Dayan 1993): M = (I-gamma P)^-1 encodes expected discounted
future occupancy -> diffusion/geodesic structure; its eigenvectors are grid-cell-like. SR is learnable by a
LOCAL TD rule (substrate-compatible). Tested on a large randomly-generated MAZE where Euclidean is strongly
deceptive.

## Pre-registration (locked BEFORE run)
- Random maze (DFS spanning tree) on an MxM cell grid -> long winding paths, geodesic >> Euclidean for many
  pairs. Random-walk transition matrix P over carved edges.
- SR: closed-form M=(I-gamma P)^-1 (gamma 0.95); embedding = top-k SVD components of M. ALSO learn M_TD by
  LOCAL TD: M[s] += alpha*(onehot(s) + gamma*M[s'] - M[s]) on walk transitions -> verify TD approximates the
  closed form (substrate-relevance).
- Tests/bars:
  (1) Spearman(SR-emb-dist, GEODESIC) >= 0.7 AND >= Spearman(SR-emb-dist, EUCLIDEAN) + 0.15.
  (2) energy-MPC on SR-emb reaches >= 0.7 AND >= Euclidean-control + 0.2 AND >> random.
  (3) SR beats the CONTRASTIVE rule (JEP-8) on the SAME maze (geodesic corr and navigation).
  (4) TD-learned M correlates with closed-form M >= 0.9 (local learnability).
- PASS = SR (local TD) captures geodesic structure + enables maze planning where contrastive failed. Methods
  (successor representation, TD, diffusion maps, EBM/MPC) established - named as such.
