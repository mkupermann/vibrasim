# JEP-43 — order embeddings on the toy: fix siblings + scale, but a cross-branch residual (method tradeoff)

## Result — PARTIAL (order embeddings fix siblings AND scale, but introduce a cross-branch residual)
Toy sanity: classification 0.984; ALL siblings REJECTED (cat/dog, eagle/sparrow, oak/pine - fixes the JEP-33
residual); ancestors + most cross-branch correct; BUT one error: is_a(rose, animal)=True (WRONG - rose is a
plant). At WordNet scale TNR was 0.97 (3% cross-branch false positives).

**VERDICT: PARTIAL - order embeddings are NOT strictly better; they trade residuals.** Order embeddings FIX the
sibling residual (siblings do not dominate each other in the partial order) AND scale to real WordNet (0.91,
JEP-42), but introduce a CROSS-BRANCH residual: a specific concept (rose, large coords) can coordinate-wise
DOMINATE an unrelated general concept (animal, small coords) even across branches - the classic order-embedding
false-positive. So each is-a method has a DIFFERENT residual:

| method | siblings | cross-branch | scale (WordNet 366) |
|--------|----------|--------------|---------------------|
| calibrated Poincare (JEP-32) | residual (FP) | correct | 0.78 ceiling |
| entailment cones (JEP-39) | correct | correct | fails (TPR 0.42) |
| order embeddings (JEP-42/43) | correct | residual (FP ~3%) | 0.91 |

## Honest decision + IS-A method landscape conclusion
No single is-a method is universally best. ORDER EMBEDDINGS are the best for LARGE REAL hierarchies (0.91 +
siblings fixed; small cross-branch residual). ENTAILMENT CONES are best for SMALL/CLEAN taxonomies (1.00, both
residuals fixed; do not scale). CALIBRATED-POINCARE is the robust middle (cross-branch fixed, sibling residual,
0.78 at scale) - and is KEPT as the shipped default because it passes the cross-branch test and is a reasonable
all-rounder. Order embeddings would REGRESS the cross-branch test (is_a(rose,animal)), so NOT made default;
documented as the recommended method for large real hierarchies. This is an honest, complete map of the is-a
method tradeoffs - surfaced by the JEP-40/41 self-correction that the ceiling was the method. Established methods
(Vendrov 2016 order embeddings, Ganea 2018 cones, Nickel-Kiela 2017 Poincare), named as such. tools/run_jep42/43.
