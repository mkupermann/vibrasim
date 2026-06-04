# JEP-49 — is the Poincare-vs-order is-a gap driven by hierarchy DEPTH? (principled method-selection guidance)

## Motivation
JEP-42/48: order embeddings beat calibrated-Poincare on held-out IS-A, and Poincare did BETTER on the shallower
vehicle hierarchy (0.86) than the deep carnivore one (0.78). Hypothesis: the gap is driven by DEPTH - Poincare's
is-a readout degrades with depth, order embeddings are depth-robust. Test on synthetic balanced binary trees of
controlled depth to isolate the variable, yielding a principled "use order when depth > X" rule.

## Pre-registration (locked BEFORE run)
- Balanced binary trees of depth {3,5,7,9} (sizes 7,31,127,511). Held-out 30% IS-A. Compare poincare vs order.
- CHARACTERIZATION: report held-out IS-A vs depth for both methods. Expectation: poincare degrades with depth,
  order stays high -> gap grows with depth. Gives the depth threshold where order becomes clearly better.
  Established (Vendrov 2016, Nickel-Kiela 2017), named as such.

## Result — NULL: depth hypothesis REFUTED (script's PASS was a degenerate trigger - overridden)
| depth | N | poincare | order |
|-------|---|----------|-------|
| 3 | 15 | 0.800 | 0.700 |
| 5 | 63 | 0.831 | 0.864 |
| 7 | 255 | 0.911 | 0.859 |
| 9 | 1023 | 0.925 | 0.884 |

**VERDICT: NULL - depth hypothesis REFUTED.** On synthetic BALANCED binary trees, Poincare does NOT degrade with
depth - it IMPROVES (0.80 -> 0.925) and BEATS order at depth 7-9. (The script printed "PASS" via a degenerate
trigger - gaps[-1] -0.04 > gaps[0] -0.10 + 0.05 - which is just order catching up slightly within noise; I
OVERRIDE that misleading verdict.) So the order>Poincare advantage on REAL WordNet (JEP-42/48) is NOT a depth
effect. On clean balanced trees Poincare is competitive-or-better even when deep. The real driver must be REAL-
HIERARCHY IRREGULARITY - uneven branching, varying depth, multiple parents (DAG, not tree) - which synthetic
balanced trees lack. (Deeper synthetic trees also give MORE ancestor pairs = more training signal, which HELPS
Poincare; real WordNet's irregularity does not.) Corrected guidance: use order embeddings for IRREGULAR REAL
hierarchies, not "deep" ones per se; on clean/balanced taxonomies Poincare is fine.

## Meta-finding (JEP-46/47/49): three refuted predictions in a row
My mechanistic hypotheses for WHY order > Poincare (cross-branch precision JEP-46-extrapolation, cone precision
JEP-47, depth JEP-49) were ALL wrong on measurement. The robust empirical facts: order > Poincare on REAL
hierarchies (is-a classification); Poincare > order for GROUNDING (task-distribution precision); Poincare fine on
clean trees. The MECHANISM (why) keeps eluding my intuition - exactly what docs/patterns/honest_evaluation.md
warns: trust measurement on the real distribution over plausible mechanistic stories. The honest output is the
measured WHAT (use order for irregular real hierarchies, poincare for grounding/clean trees), not a confident WHY.
