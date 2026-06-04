# JEP-57 — consolidate the error-propagation principle (amplify vs absorb)

Not a new experiment - a consolidation of the JEP-46 vs JEP-56 contrast into a reusable principle (added as
docs/patterns/honest_evaluation.md #8).

## The principle
The same downstream pipeline stage amplified upstream errors (JEP-46) and absorbed them (JEP-56). The difference
is the ERROR TYPE:
- CONFIDENT-WRONG upstream outputs get SELECTED by the downstream and AMPLIFIED (JEP-46: cross-branch is-a FP
  grounded a wrong entity -> agent navigated to it).
- MINORITY-NOISE within a mostly-correct set gets ABSORBED by a robust-aggregate downstream (JEP-56: impure
  discovered category, correct majority -> nearest-target navigation hit a correct member).
Consequence: a CONSERVATIVE component (high precision / low recall - misses things but rarely confidently wrong)
is SAFER in a pipeline than a high-aggregate-accuracy-but-confidently-wrong one. This unifies JEP-46/52/56 and
explains why conservative calibrated-Poincare is the grounding default. Established reasoning (error analysis),
named as such - no novelty, a consolidation.
