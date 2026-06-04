# JEP-39 — hyperbolic entailment cones: the diagnosed-correct fix for the IS-A sibling residual

## Motivation
JEP-33 showed distance/norm features cannot reject SIBLINGS (the ranking loss pulls siblings close). The
diagnosed-correct fix is ANGULAR containment - hyperbolic entailment cones (Ganea et al. 2018): each concept x
has a cone with half-aperture psi(x) (general=wider); a is-a b iff a is inside b's cone (angular condition).
Siblings are angularly OUTSIDE each other's cones, so this should reject them where distance could not.

## Pre-registration (locked BEFORE run)
- Train Poincare embeddings with the entailment-cone energy (descendants inside ancestor cones; non-pairs out,
  with margin). is_a(a,b) = energy(b,a) ~ 0 (a inside b's cone).
- Bars: is-a classification accuracy >= 0.90 AND ALL siblings rejected (cat/dog, eagle/sparrow, oak/pine) AND
  cross-branch + ancestors correct (full sanity, 0 wrong). PASS = entailment cones fix the sibling residual.
  NULL otherwise. Ganea et al. 2018 (hyperbolic entailment cones) established - named as such.

## Result — PASS (entailment cones fix the sibling residual, 1.00 on toy)
| metric | distance-based (JEP-32/33) | entailment cones (JEP-39) |
|--------|----------------------------|---------------------------|
| is-a classification acc | 0.96 | 1.00 |
| siblings (cat/dog, eagle/sparrow, oak/pine) | FALSE-POSITIVE (residual) | correctly REJECTED |
| cross-branch + ancestors | correct | correct |

**VERDICT: PASS.** Hyperbolic entailment cones (Ganea et al. 2018) - ANGULAR containment (a is-a b iff a is
inside b's cone, with half-aperture psi(x) wider for general x) - achieve 1.00 IS-A classification on the toy,
rejecting ALL siblings that the distance/norm features (JEP-32/33) could not. This is the diagnosed-correct fix:
siblings are angularly OUTSIDE each other's cones (same radius, lateral), so the cone condition rejects them
where distance could not. Genuinely resolves the JEP-33 sibling residual. Established (Ganea 2018), named. Next:
verify it holds at real WordNet scale (JEP-39b) before integrating into the shipped reasoner.
