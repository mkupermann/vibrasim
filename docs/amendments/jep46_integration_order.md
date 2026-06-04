# JEP-46 — does fixing the is-a component (order embeddings) improve the integration at real scale?

## Motivation
JEP-37: abstract-goal planning on real WordNet degraded to 0.79, inheriting the Poincare is-a's ~0.78 reliability.
JEP-42-45 fixed the component (order embeddings, 0.91 is-a). Re-run the real-WordNet integration with
isa_method="order" - if it improves toward 0.91, the component fix PROPAGATES to the integrated behaviour,
closing the loop on JEP-37.

## Pre-registration (locked BEFORE run)
- Same WordNet carnivore environment + entities + SR planner as JEP-37, but reasoner uses isa_method="order".
- Bar: reached-correct-category >= 0.88 (improves on JEP-37's 0.79 with poincare). PASS = the component fix
  propagates to the integration. NULL otherwise. Established methods (Vendrov 2016 order, SR/TD), named.

## Result — NULL (counterintuitive: better-aggregate component gave WORSE integration)
| is-a method | aggregate is-a (WordNet) | integration (reached-correct-category) |
|-------------|--------------------------|----------------------------------------|
| poincare (JEP-37) | 0.78 | 0.79 |
| order (JEP-46) | 0.91 | 0.50 |

**VERDICT: NULL - hypothesis REFUTED, important finding.** The better-AGGREGATE is-a method (order, 0.91) gave
WORSE integration (0.50) than poincare (0.79). My hypothesis "better component -> better integration" was WRONG.
The reason: the ERROR PATTERN matters more than aggregate accuracy. Grounding "which entities are-a category"
needs PRECISION against CROSS-BRANCH confusions - and cross-branch false-positives are exactly order embeddings'
weakness (a specific concept dominating an unrelated general one; e.g. a canine grounded as a feline). Those FPs
ground WRONG entities -> the agent navigates to them. Poincare's errors are SIBLINGS, which NEVER arise in
entity-vs-category grounding (entities are not siblings of categories), so its errors don't hurt this use case.
REFINES JEP-37: the integration inherits the component's ERROR PATTERN, not its aggregate accuracy - and
aggregate accuracy is the WRONG metric for predicting downstream utility. So the "best is-a method" depends on
the USE CASE: order embeddings for raw classification at scale; POINCARE for grounding/integration (cross-branch
precision). A genuinely counterintuitive, honest result - higher benchmark accuracy can mean worse task
performance when the error types differ. Established methods (Vendrov 2016, Nickel-Kiela 2017, SR/TD), named.
