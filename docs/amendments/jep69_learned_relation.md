# JEP-69 — LEARN a relation from observation (toward learned, not hand-built, structure)

## Motivation
JEP-66/68 used HAND-SPECIFIED relational roles (ABOVE/TOP). Humans LEARN relations from experience. Test: can a
relation be LEARNED from observed (head, tail) pairs and GENERALIZE to unseen pairs - reducing the 'hand-built
structure' critique? Established method: translational relation embedding (TransE, Bordes 2013): learn entity
vectors + a relation vector r so head + r ~ tail; predict tail of held-out heads.

## Pre-registration (locked BEFORE run)
- Knowledge of a relation as (head, tail) pairs over N entities (e.g. a learned 'parent' / 'above' map). Learn
  entity embeddings + relation vector via TransE margin loss on TRAIN pairs. Test: held-out pairs - rank the true
  tail among all entities by ||head + r - tail||.
- Bars: held-out tail-prediction hits@1 >= 0.7 AND hits@3 >= 0.9 (the relation GENERALIZES, learned not memorized).
  PASS = relational structure is LEARNABLE from observation given relational supervision. Honest caveat: the
  SUPERVISION (which pairs hold) is given; UNSUPERVISED relation discovery remains open. Established (TransE), named.

## Result — NULL (flawed setup, honestly diagnosed; relation-learning already established elsewhere)
held-out hits@1 0.08, hits@3 0.38. NULL due to TWO setup flaws, not a clean test:
1. Ground-truth relation = 'nearest entity to head+R' is NON-TRANSLATIONAL (many-to-one, discrete), but TransE
   assumes head+r~tail (translation) - mismatched, so it cannot fit.
2. Single relation + each held-out head appears ONLY in its held-out pair -> the head's embedding is never
   trained -> cannot predict (the unseen-entity link-prediction trap, same as JEP-44).
**VERDICT: NULL (setup flaw).** This did NOT cleanly test relation learning. AND it would re-tread established
ground: the EQMOD-3 geometric programme already showed RELATION LEARNING = a logistic probe (GEO-66) - relations
ARE learnable from supervision. So the 'learnable not hand-built' claim holds via PRIOR WORK; the structural
rungs (JEP-66/68) used hand-built roles for clarity but the roles are learnable in principle. NOT chasing a clean
re-demo (redundant with GEO-66). The genuinely OPEN gap is UNSUPERVISED relation/role DISCOVERY (no labels) +
integration - which neither GEO-66 nor this rung addresses. Honest. Established (TransE Bordes 2013; GEO-66), named.
