# JEP-469 — Does balance-seeking on signed affect produce emergent us-vs-them camps?

## Motivation
JEP-467/468 gave the substrate signed affect relations (friend/enemy) and Heider imbalance detection.
Heider's theory + the Cartwright-Harary structure theorem (1956) predict a genuine EMERGENT phenomenon:
a signed network driven toward balance (imbalanced triads are tense and resolve) spontaneously
partitions into exactly TWO mutually-antagonistic camps — "us vs them" emerges from signed energies
alone. JEP-469 tests whether our signed-affect representation, under a local balance dynamic, produces
this emergent 2-clustering. Vision-aligned (energies create group structure); established theory, named.

## Method (`tools/run_jep469_emergent_camps.py`)
Complete signed graph on N=12 concepts (every pair tagged friend +1 / enemy −1 at random). Balance
dynamic: while imbalanced triads exist (product of the 3 edge signs = −1), flip the single edge whose
flip removes the MOST imbalanced triads (greedy de-frustration); iterate. Measure: #imbalanced triads
over time, and 2-clusterability (greedy 2-coloring: + edges within a camp, − between; count violations)
BEFORE vs AFTER. Seeds 0 & 7 (5 random graphs each).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J469a (random start is frustrated):** initial #imbalanced triads > 0 and initial 2-coloring has
  > 10% edge violations, both seeds (a random signed network is NOT a clean 2-camp structure).
- **J469b (balance produces 2 camps):** after the dynamic, #imbalanced triads = 0 AND a 2-coloring is
  consistent (≤ 2% edge violations) — emergent us-vs-them, both seeds.
- **J469c (monotone de-frustration):** #imbalanced triads is non-increasing under the dynamic, both seeds.

PASS = signed affect, driven toward balance, self-organizes into two antagonistic camps (Cartwright-
Harary), demonstrated in our representation. NULL if it does not converge to balance / 2 camps (the
dynamic or representation differs). Bars locked; no retuning. Established theory (Heider 1946;
Cartwright-Harary 1956), named; a demonstration in our system, not new science. No transformer.

## RESULT (2026-06-05): **PASS** — two antagonistic camps emerge from signed affect

| seed | BEFORE imbalanced triads / 2-color violations | AFTER imbalanced triads / 2-color violations |
|------|-----------------------------------------------|-----------------------------------------------|
| 0 | 109 / 0.42 | **0 / 0.000** |
| 7 | 110 / 0.43 | **0 / 0.000** |

J469a ✓ (random start frustrated), J469b ✓ (→ 0 imbalanced, perfect 2-clustering), J469c ✓ (monotone) →
**PASS, both seeds** (5 graphs each).

## Verdict: us-vs-them emerges from signed energies (Cartwright-Harary, in our representation)
A random signed-affect network is frustrated (~110 of 220 triads imbalanced, 42% inconsistent with any
2-partition). Driven toward balance by a local greedy de-frustration dynamic (flip the most-frustrating
edge), it converges monotonically to ZERO imbalanced triads and a PERFECT 2-clustering (0 violations) —
the network spontaneously splits into exactly two mutually-antagonistic camps (all friends within a camp,
all enemies between camps). So in our signed-affect representation, "us vs them" structure EMERGES from
signed energies alone — the Cartwright-Harary structure theorem (1956) realized. This extends the
affect work from individual valence to EMERGENT GROUP STRUCTURE, directly aligned with Michael's
"energies of the environment". Established theory (Heider 1946; Cartwright-Harary 1956), named; a clean
demonstration in our system, not new science. No transformer.
