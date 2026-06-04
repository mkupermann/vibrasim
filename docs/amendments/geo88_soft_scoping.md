# GEO-88 — Soft kind-scoping (boost, don't filter) recovers robustness

## Motivation
GEO-87: HARD kind-scoping + a fallible router HURTS (0.67 < 0.90 unscoped) because a mis-route empties the
scope -> IDK. Proposed fix: SOFT scoping — BOOST the routed kind's similarity by a margin instead of filtering
others out, so a mis-route degrades gracefully (the right fact can still win on raw similarity). GEO-88 tests
whether soft scoping beats both hard (0.67) and unscoped (0.90).

## Pre-registration (locked BEFORE run)
- Personal KB + LinearRouter (GEO-87 setup). Soft scoping: sims[fact] += boost if fact.kind == routed_kind;
  pick argmax. Sweep boost in {0.05, 0.1, 0.2}.
- Compare: unscoped (0.90), hard-scope (0.67), soft-scope (each boost).
- Bar: best soft-scope >= 0.90 (recovers robustness) AND ideally > unscoped (helps cross-type without
  brittleness). NULL if soft scoping doesn't beat hard / doesn't recover.
