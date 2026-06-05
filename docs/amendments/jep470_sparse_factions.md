# JEP-470 — Sparse signed affect: two camps (strong balance) or many factions (weak balance)?

## Motivation
JEP-469 showed COMPLETE signed-affect networks balance into exactly 2 antagonistic camps (Cartwright-
Harary guarantees this for complete graphs). Real affect networks are SPARSE, and sparse signed
networks can settle into WEAK balance (Davis 1967) — k > 2 mutually-antagonistic FACTIONS, not a clean
binary (weak balance forbids only the +,+,− triad, allowing all-negative triads = many cliques). The
genuinely uncertain question: does our signed-affect representation, when sparse, organize into 2 camps
or fragment into multiple factions? This bounds how affect structures collectives in the realistic
(sparse) case.

## Method (`tools/run_jep470_sparse_factions.py`)
Sparse signed graph: N=18 nodes, each pair connected with prob p=0.45 (signed ±1 at random). Greedy
de-frustration dynamic (flip the existing edge that removes the most imbalanced triads), as JEP-469.
After convergence, count CLUSTERS = connected components of the +edge subgraph (a balanced cluster has
+ within, − between). Report final imbalanced-triad count and cluster count. Seeds 0 & 7, 5 graphs each.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J470a (de-frustration works):** the dynamic reduces imbalanced triads (final ≤ 0.25 × initial), both
  seeds.
- **J470b (sparse → MORE than 2 factions):** the mean final cluster count > 2.5, both seeds — sparse
  affect fragments into multiple factions, NOT a clean binary (weak balance, contra the complete-graph
  2-camp result).
- **J470c (report):** state mean cluster count and final frustration.

Predicted: sparse networks fragment into k > 2 factions (weak balance) — the 2-camp result is specific to
fully-connected affect. NULL if they still reach 2 camps (strong balance holds even sparse — also
informative). Bars locked; no retuning. Established theory (Davis 1967 k-clustering; Cartwright-Harary
1956), named; a demonstration, not new science. No transformer.

## RESULT (2026-06-05): NULL — prediction wrong, AND a design flaw (I tested strong-balance by construction)

| seed | imbalanced triads 0→final | mean clusters (per-graph) |
|------|----------------------------|----------------------------|
| 0 | 404 → 0.0 | 2.0 ([2,2,2,2,2]) |
| 7 | 398 → 33.6 | 1.8 ([1,2,2,2,2]) |

J470a ✓ (de-frustration works, seed 0 fully balanced), **J470b ✗ (clusters ≈ 2, NOT >2.5) → NULL.**

**My prediction was wrong AND the design conflated the two balance regimes.** Sparse networks still
reach ~2 camps, but that is BY CONSTRUCTION, not a discovery: my `imbalanced()` counts the all-negative
(−,−,−) triad as imbalanced (product < 0), which is the STRONG-balance definition — a dynamic that
eliminates those triads necessarily drives toward 2-clustering. The genuine FACTION (weak-balance, Davis
1967) regime is defined by FORBIDDING ONLY the (+,+,−) triad while ALLOWING (−,−,−), which permits k > 2
mutually-antagonistic cliques. I never tested that — my objective targeted strong balance, so 2 camps
was inevitable.

**Honest conclusion.** The robust, correctly-attributed result is just JEP-469 restated: a strong-balance
dynamic on signed affect → 2 camps, robust to sparsity. The faction question remains OPEN and would need
a weak-balance / correlation-clustering objective (allow all-negative triads). I am NOT chasing it
further here — it is increasingly tangential social-network theory, well outside the substrate's core,
and I have a clean honest result (strong balance → 2 camps) plus an honest acknowledgement of what was
not tested. Recorded NULL against the locked bars; no retuning. Established theory, named.
