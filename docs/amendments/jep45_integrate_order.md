# JEP-45 — integrate order embeddings as a selectable is-a method in the concept reasoner

## Motivation
JEP-42 showed order embeddings are the best is-a method for LARGE REAL hierarchies (0.91 vs the Poincare 0.78
ceiling) and fix the sibling residual. Ship it: add isa_method="order" to ConceptReasoner.fit so users can choose
the best method for their taxonomy. Keep "poincare" default (passes cross-branch test, robust all-rounder).

## Pre-registration (locked BEFORE run)
- ConceptReasoner.fit(isa_method="order") trains order embeddings; is_a uses coord-domination + calibrated thr.
- Bars: (a) existing tests still pass with default (poincare); (b) on WordNet carnivore 366, isa_method="order"
  held-out IS-A >= 0.88 (ships the JEP-42 result through the API); (c) order method rejects toy siblings.
  PASS = order embeddings integrated + verified through the shipped API. NULL otherwise. Vendrov 2016, named.
