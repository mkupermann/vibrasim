# JEP-318 — Auto-discovering INVERSE relation pairs from data (generalizes abduction)

## Motivation
JEP-308 hand-stored an inverse edge (caused_by) to enable abduction. The meta step: DISCOVER that two relations are
inverses from the fact pattern — (a R1 b) ⟺ (b R2 a) — then auto-enable answering R2 via R1's reverse, WITHOUT
materializing all R2 facts. Established relational-pattern induction, named as such. No transformer.

## Method
For each ordered relation pair (R1, R2), inverse score = rate over stored (a,R1,b) that (b,R2,a) is stored (on the
SEED pairs where both are present). Classify inverse if ≥ 0.8. Then for a discovered inverse pair, answer a
HELD-OUT `R2(a,b)` query by checking `R1(b,a)` — even though that R2 fact was never stored.

## Pre-registered bars (BEFORE the run)
- **J318a (discovery):** classify relation pairs as inverse / not — ground truth inverses
  {parent_of↔child_of, causes↔caused_by, bigger_than↔smaller_than, north_of↔south_of}, non-inverses
  {eats×likes, owns×wants} — accuracy ≥ 0.90, both seeds (0, 7).
- **J318b (auto-apply without materializing):** store R1 fully + only SEED R2 pairs; answer HELD-OUT R2 queries via
  the discovered inverse of R1 vs ground truth ≥ 0.90, both seeds.
- **J318c (persists):** discovery + answers identical after reload, both seeds.

Predicted most-likely failure: a symmetric relation is trivially its own inverse and could be mis-paired; or seed
overlap too small to score. If J318a misclassifies, report the pair + its inverse score (a separability finding),
don't move the 0.8 threshold.

## Result (seeds 0, 7): **PASS**
- **J318a:** inverse-pair discovery = **1.0** — found exactly {parent_of↔child_of, causes↔caused_by,
  bigger_than↔smaller_than, north_of↔south_of}, no false pairs among eats/likes/owns/wants, both seeds. **PASS.**
- **J318b:** answering HELD-OUT R2 queries via the discovered inverse of R1 (those R2 facts never stored) vs ground
  truth = **1.0**, both seeds. **PASS.**
- **J318c:** discovery + answers identical after reload. **PASS.**

## Verdict: **PASS**
The substrate DISCOVERS which relations are inverses of each other from a couple of seed pairs in the fact pattern,
then answers the inverse relation via the discovered mapping WITHOUT materializing it — generalizing the hand-built
inverse edge of JEP-308 (abduction) into a learned structural rule. Together with JEP-316/317 the system now induces
relation algebra (symmetry, transitivity) AND relation structure (inverses) from data, and applies them. Established
relational-pattern induction, named as such; no transformer.

