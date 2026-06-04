# JEP-37 — stress-test the integration where is_a is NOT reliable (real WordNet); validate the honest caveat

## Motivation
JEP-34/35/36 all hit 1.00 - but only in the RELIABLE toy regime. I claimed the integration "inherits component
limits at scale". This rung TESTS that claim by running abstract-goal planning on REAL WordNet carnivore entities
(where is_a is ~0.86, not 1.0). If the integration degrades toward the component's is_a reliability, the honest
caveat is demonstrated, not just asserted.

## Pre-registration (locked BEFORE run)
- WordNet carnivore subtree as the taxonomy; reasoner fit (hyp_dim=20, 10k iters). Place ~16 real species on the
  grid; goals = intermediate categories (canine/feline/bear/...). Ground via is_a, navigate, measure correct-
  category arrival.
- This is a CHARACTERIZATION (no pass/fail): report whether integration accuracy degrades from the toy's 1.00
  toward the real is_a reliability. The honest expectation is degradation - confirming the composition inherits
  component limits. Established methods, named as such.

## Result — caveat CONFIRMED + an unexpected second finding (embedding generality-sign instability)
| measure | value |
|---------|-------|
| integration: reached correct-category entity (real WordNet) | 0.793 |
| (toy, JEP-34) | 1.000 |
| RAW norm-direction is_a (general=small norm) | 0.126 (!!) |

**FINDING 1 (intended) - caveat confirmed.** On real WordNet (is_a less reliable than toy), abstract-goal
planning reached the correct category 0.79 vs 1.00 on the toy. The integration INHERITS its components'
reliability; grounding errors from imperfect is_a propagate to wrong targets. Honest boundary demonstrated, not
just claimed.

**FINDING 2 (unexpected, important).** The RAW norm-direction readout scored 0.126 - FAR below chance - meaning
THIS embedding learned generality INVERTED (general concepts at LARGE norm, not small). The Poincare ranking
loss pulls ancestor-descendant pairs close but does NOT pin which end sits at smaller radius, so the generality
SIGN can invert run-to-run (0.126 here vs 0.86 in JEP-29b, same taxonomy/config family). The integration still
worked (0.79) because it uses the CALIBRATED is_a (JEP-32), which learns the embedding's actual sign from
training pairs and compensates. Implications: (a) this is WHY the JEP-32 calibrated classifier is necessary
(raw norm is sign-unstable); (b) it partly RE-EXPLAINS JEP-31's NULL - that used the RAW norm-direction, which
can be inverted, compounding the under-training. Honest lesson: do NOT rely on raw norm direction for is-a;
always calibrate. To pin the sign, the ranking loss should be augmented with a root-anchoring / depth term.
Surfaced by stress-testing my own integration. Established methods (Poincare embeddings), named as such.
