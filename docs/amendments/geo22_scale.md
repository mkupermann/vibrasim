# GEO-22 — Does the method hold at SCALE? (retrieval/multi-hop as the store grows)

## Motivation
GEO-15–19 saturated at 1.00 on ~12 entities. The honest open question: does geometric retrieval/multi-hop
degrade as the candidate pool grows to hundreds? GEO-22 sweeps store size and measures the accuracy curve —
finding the real operating point, not a saturated toy number.

## Pre-registration (locked BEFORE run)
- Generate N person->company->city chains for N in {25,100,400}. Synthetic but distinct names.
- Single-hop retrieval (person's company) and 2-hop (person's city) accuracy over all N, pool = all N
  same-relation facts (no easy distractors — the hard case: N near-miss peers).
- Report accuracy vs N. Bars (descriptive, not pass/fail tuning): record the curve; flag the N where 2-hop
  drops below 0.9 and below 0.7. Chance = 1/N.
- This is a characterization rung: the curve IS the finding (where does PC-scale geometry stay usable).
