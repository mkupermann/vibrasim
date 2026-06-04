# JEP-73 — unified grounded+structured system: learn concepts -> decorrelate -> compose (relations + analogy)

## Motivation
JEP-72 found the decorrelation interface bridging grounding (correlated concepts) and structure (VSA). Build the
UNIFIED pipeline on REAL data: form concepts from Fashion-MNIST -> whiten (the bridge) -> structured composition
(relational queries AND analogy) on the LEARNED concepts. Demonstrates the two main threads unified into one
system on real perceptual concepts.

## Pre-registration (locked BEFORE run)
- Fashion-MNIST class-mean concepts -> whiten (decorrelate) -> VSA. Tasks on the LEARNED-whitened concepts:
  (a) relational query 'what is above Y'; (b) one-shot analogy A:B::C:? (transformation = a learned-concept
  relation). 
- Bars: both relational-query AND analogy accuracy >= 0.9 on real learned concepts. PASS = the unified
  grounded+structured system works on real data via the decorrelation bridge. NULL otherwise. Established
  (clustering, PCA-whitening, VSA/HRR), named as such.

## Result — PARTIAL: relational integrates via whitening (1.00), analogy needs UNITARIZATION (0.47)
| operation | learned-whitened concepts |
|-----------|---------------------------|
| relational query | 1.000 |
| one-shot analogy | 0.470 |

**VERDICT: PARTIAL - refines the integration requirement.** Relational query works (1.00) on whitened
(decorrelated) learned concepts, but analogy degrades (0.47). Reason: analogy uses the CONCEPT as an unbinding KEY
(T = B (x) A^-1), which needs the concept to be UNITARY (A (x) A^-1 = identity); whitening gives ORTHOGONALITY
(enough for relational query, where the concept is just a distinct filler) but NOT unitarity. So DIFFERENT
structural operations have DIFFERENT representation requirements: relational -> decorrelated; analogy -> unitary.
The grounding<->structure bridge is not one transform - it is REPRESENTATION-MATCHING per operation. Fix: UNITARIZE
the learned concepts (JEP-73b). Honest, refined integration insight. Established (VSA/HRR), named.

## JEP-73b — unitarization — PASS (the complete bridge)
| | learned-whitened (JEP-73) | learned-UNITARIZED (JEP-73b) |
|---|---|---|
| off-diag cosine | ~0 | 0.042 |
| relational query | 1.00 | 1.00 |
| one-shot analogy | 0.47 | 1.00 |

**VERDICT: PASS.** UNITARIZING the learned concepts (unit-magnitude FFT, identity preserved in phase) makes BOTH
relational composition (1.00) AND analogy (1.00) work on real Fashion-MNIST concepts. Unitarization both
DECORRELATES (0.77 -> 0.04) and makes vectors UNITARY (self-invertible), satisfying ALL VSA structured operations.
So the COMPLETE grounding<->structure bridge is UNITARIZATION of learned concepts.

## Integration synthesis (JEP-72/73/73b)
The two main EQMOD-4 threads UNIFY into one pipeline on REAL data: GROUND (form concepts from perception) ->
UNITARIZE (the bridge) -> COMPOSE structurally (relations + analogy via VSA). Concrete integration recipe found:
unitarize learned concepts so similarity-based grounded representations plug into orthogonal-needing symbolic
composition - resolving the connectionist-symbolic representation tension (JEP-72). Genuine progress on the
INTEGRATION gap toward a unified cognitive architecture. HONEST remaining gaps: toy scale (10 concepts); the
RELATIONS and TRANSFORMATIONS are still hand-specified (ABOVE role, analogy operator), not LEARNED; and the
unsupervised structure-discovery gap (JEP-69/70) is unsolved. So: grounded LEARNING + structured COMPOSITION are
unified (real concepts, all VSA ops), but LEARNING THE STRUCTURE and SCALING remain open. Established methods
(clustering, unitary HRR/VSA, FFT), named as such - the integration RECIPE is the step, no new method.
