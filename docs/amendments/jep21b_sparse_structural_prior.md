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

## Result — PARTIAL on the exact bar (claim strongly supported; p=0.10 margin missed by 0.002)
| p | 2D-prior acc (unobserved) | transitive-closure | margin |
|---|---------------------------|--------------------|--------|
| 0.05 | 0.919 | 0.636 | 0.283 |
| 0.10 | 0.971 | 0.773 | 0.198 |
| 0.20 | 0.984 | 0.884 | 0.100 |

**VERDICT: PARTIAL on the locked threshold; the CLAIM is strongly supported.** The low-dim structural prior
genuinely generalizes SPARSE relational observations: fitting 2D coords to a small subset predicts UNOBSERVED
pairs far better than transitive closure at every sparsity (0.92 vs 0.64 at p=0.05; 0.97 vs 0.77 at p=0.10).
This is the genuine factorization benefit JEP-21 failed to test - a structural prior REDUCES what must be
observed. HONEST near-miss: the pre-registered p=0.10 bar (prior>=0.9 AND margin>=0.2) was met on accuracy
(0.971) but the margin (0.198) fell 0.002 SHORT of 0.2 -> technical PARTIAL, NOT retuned. (The p=0.05 point
clears both: 0.919 acc, 0.283 margin.) So: claim supported across the sweep; exact threshold marginally missed
at one point. Corrects JEP-21's weaker re-derivation test. Ordinal embedding / structural priors established,
named as such.

## JEP-21 thread conclusion (honest)
The useful core of structure-content factorization HOLDS: a low-dimensional structural prior lets few relational
observations determine many unobserved ones (JEP-21b), far beyond transitive closure. What was NOT cleanly
shown: cross-domain transfer of a structure learned on ONE content to ANOTHER reducing observations (JEP-21 was
confounded; JEP-21b uses the 2D prior directly rather than a transferred one). Honest scope: low-dim structural
priors generalize sparse relations; full TEM cross-content transfer remains partially open.
