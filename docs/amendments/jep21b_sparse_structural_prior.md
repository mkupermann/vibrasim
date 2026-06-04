# JEP-21b — does a low-dim STRUCTURAL PRIOR generalize sparse relational observations? (genuine factorization test)

## Motivation
JEP-21 only re-derived structure from full adjacency. The genuine claim: a LOW-DIMENSIONAL structural prior
(here 2D) lets you infer UNOBSERVED relations from a SPARSE subset of observed ones - the operational core of
"structure reduces what you must observe" (the useful half of TEM factorization). Test vs a no-structure
baseline (transitive closure over observed relations only).

## Pre-registration (locked BEFORE run)
- N entities with true 2D coordinates. Observe a fraction p of all pairwise AXIS comparisons (i east/north of j).
- WITH 2D prior: fit 2D coordinates by gradient descent on a hinge loss over the OBSERVED comparisons; predict
  UNOBSERVED comparisons from fitted coords.
- BASELINE (no structural prior): transitive closure over observed comparisons (predict only what is derivable
  by transitivity; else chance 0.5).
- Sweep p in {0.05, 0.10, 0.20}. Bars: at p=0.10 the 2D-prior accuracy on UNOBSERVED pairs >= 0.9 AND exceeds
  transitive-closure by >= 0.2. PASS = a low-dim structural prior genuinely generalizes sparse relational
  observations. NULL otherwise. Ordinal embedding / structural priors established - named as such.
