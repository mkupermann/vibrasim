# JEP-48 — do the is-a method findings replicate on a DIFFERENT WordNet domain (vehicles)?

## Motivation
The whole reasoning thread used animal/carnivore taxonomy. Test whether the key finding (order embeddings >
calibrated-Poincare for held-out is-a at real scale, JEP-42) is DOMAIN-GENERAL or carnivore-specific, by
replicating on a structurally different domain: vehicle.n.01 (520 artifact concepts).

## Pre-registration (locked BEFORE run)
- vehicle.n.01 subtree (~520 concepts). Same held-out 30% IS-A eval. Compare isa_method 'poincare' vs 'order'.
- Bars: order balanced held-out IS-A > poincare by >= 0.05 (replicates JEP-42 cross-domain) AND order >= 0.85.
  PASS = the finding is domain-general. NULL/PARTIAL if it does not replicate (then it was carnivore-specific).
  Established (Vendrov 2016, Nickel-Kiela 2017), named as such.

## Result — PASS (the is-a method finding is domain-general)
| domain | calibrated Poincare | order embeddings |
|--------|---------------------|------------------|
| carnivores (366, JEP-42) | 0.78 | 0.91 |
| vehicles (520, JEP-48) | 0.861 | 0.917 |

**VERDICT: PASS.** On vehicle.n.01 (520 artifact concepts - a structurally different domain from animals), order
embeddings (0.917) beat calibrated-Poincare (0.861) on held-out IS-A, the same pattern as carnivores (JEP-42).
So order>Poincare-at-scale is DOMAIN-GENERAL, not carnivore-specific - a robustness confirmation. Note Poincare
did BETTER on vehicles (0.86) than carnivores (0.78): vehicles are a SHALLOWER hierarchy (Poincare's depth-12
weakness is less exposed), but the RELATIVE finding (order > Poincare) holds. Strengthens the shipped method
guidance: for raw is-a classification at scale, order embeddings are the better method across domains.
Established (Vendrov 2016, Nickel-Kiela 2017), named as such.
