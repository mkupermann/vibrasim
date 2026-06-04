# Pattern: honest evaluation — lessons the EQMOD-4 NULLs earned

Reusable methodological patterns, each from a specific NULL/self-correction in the JEPA programme (JEP-1..46).
These are about HOW to evaluate, not what to build — and each cost a wrong claim before it was learned.

## 1. Error PATTERN beats aggregate accuracy for downstream utility (JEP-46)
A method with higher benchmark accuracy can make a DOWNSTREAM TASK worse. Order embeddings had better is-a
classification (0.91 vs 0.78) but made an integrated agent WORSE (0.50 vs 0.79) - because grounding needs
precision against CROSS-BRANCH confusions, which was exactly order embeddings' error type, while the better-on-
benchmark method's errors (siblings) never arose in that task. **Evaluate methods on the actual downstream task,
and look at WHICH errors they make - not just a scalar benchmark.** SHARPENED (JEP-47): even a PRECISION
metric must be measured on the TASK's pair distribution, not random pairs. Entailment cones had the best
random-pair precision (TNR 0.98) but the WORST grounding (0.24), because the task checks leaf-vs-general-category
pairs where general concepts' wide cones produce cross-branch false-positives that random-pair metrics never
surfaced. Two wrong predictions (JEP-46/47) both reduced to: measure on your task's actual input distribution.

## 2. Quantify a claim before repeating it (JEP-40/41)
I asserted "real-scale under-convergence is just compute" across several rungs. When finally measured: accuracy
plateaus with iterations (JEP-40) AND is flat with dimension (JEP-41) - the limit was the METHOD, not compute.
A repeated, unverified claim was simply wrong. **If you find yourself asserting the same thing repeatedly,
measure it.**

## 3. Aggregate accuracy can hide failure that cherry-picked queries mask (JEP-29)
A reasoner scored 0.53 (~chance) on real WordNet while its hand-picked sanity queries all PASSED - the easy
queries masked the aggregate collapse. **Always report the aggregate over a representative set; never trust a
few demo queries.**

## 4. Hold out EDGES, not just labels, for relational link prediction (JEP-44)
Holding out ancestor-pair LABELS while keeping all graph EDGES leaks the relationship (graph distance encodes
ancestry). A guard or feature computed from the full graph is then circular. **For relational generalization,
hold out the structure, not just the test labels - and check whether a feature secretly contains the answer.**

## 5. Stress-test your OWN deliverable; it has bugs (JEP-32, JEP-33, JEP-38)
`is_a` shipped with a real correctness bug (cross-branch false-positives) found only by adversarially testing it.
A "fix" (lateral feature) didn't work and was reverted. A pushed test was red and was caught. **Treat your own
output as untrusted: probe its failure modes, revert fixes that don't work, and check tests actually pass.**

## 6. Report near-misses as misses; don't round up (throughout)
0.002, 0.019, 0.034, 0.043 short of a pre-registered bar were each recorded as PARTIAL/miss, not rounded to PASS.
Bars were locked before running and never tuned post-hoc. **Pre-register, then report what happened.**

## 7. A NULL with a diagnosis is more valuable than a forced PASS
Most rungs that "failed" produced the insight that drove the next step: JEP-2 NULL (random encoder) -> JEP-5
fix; JEP-37 (integration degrades) -> the error-pattern finding; JEP-40/41 (method ceiling) -> JEP-42 the right
method. **Chase the diagnosis, not the green checkmark.**

These patterns are the deadlock-breaking process the project is actually about ("developing a deadlock-breaking
process, not necessarily succeeding at the simulation" - CLAUDE.md). The methods studied are all established
(named in the amendments); the discipline is the transferable part.
