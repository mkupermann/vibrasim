# JEP-5 — does a LOCALLY-LEARNED representation fix energy-based MPC? (tests the JEP-2 diagnosis)

## Hypothesis (from JEP-2 NULL)
JEP-2 found energy-based MPC failed (0.07) because a RANDOM encoder makes embedding-distance uncorrelated with
grid-distance -> energy uninformative. Claim: a representation LEARNED so that successively-visited states are
close (temporal coherence / slow-feature, learnable by a LOCAL contrastive rule - substrate-native) makes
energy meaningful and MPC works. If true, it proves the diagnosis AND demonstrates the substrate's local-
learning benefit for JEPA-style representation learning.

## Pre-registration (locked BEFORE run)
- Learn cell embeddings by a LOCAL contrastive rule on random-walk transitions: ATTRACT successive cells'
  embeddings, REPEL random non-adjacent pairs past a margin (collapse-free). No backprop, local updates only.
- Energy E(s,goal) = ||emb[s]-emb[goal]||; greedy energy-descent planner picks the action reducing energy.
- Metric: fraction of held-out start/goal pairs reached within step budget. Compare RANDOM embedding (JEP-2
  control, ~0.07) vs LOCALLY-LEARNED embedding.
- Sanity: learned-embedding distance must correlate with true grid (Manhattan) distance (Spearman > 0.7).
- Bars: learned-embedding MPC >= 0.8 reached AND >> random-embedding. PASS = the JEP-2 diagnosis confirmed and
  local-rule representation learning enables energy-based planning. NULL if learned rep doesn't help.
