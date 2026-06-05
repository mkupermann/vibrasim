# JEP-329 — Temporal / event reasoning over the durable store (before/after, what happened first)

## Motivation
The engine learns temporal order (`_orders['before']`, a transitive before-DAG). Extend the substrate reasoning
suite into SEQUENCE: bridge `before` edges, answer "did X happen before Y?" (transitive, asymmetric) and "what
happened first?" over the durable store. `before` is just a directed transitive relation — reuses the validated
climb (JEP-298/307). No transformer.

## Method
Bridge `eng._orders['before']` into `SubstrateMemory(directed=True)` as `before` edges. `happened_before(x,y)` =
gated transitive climb on `before`. `what_first(events)` = the event no other event happened-before (no predecessor
in the before-closure). Ground truth = transitive closure of the engine's before-DAG.

## Pre-registered bars (BEFORE the run)
- **J329a (transitive + asymmetric):** `happened_before` matches the before-closure ≥ 0.90 on a balanced set incl.
  multi-hop positives AND the asymmetry (before(a,c) True ⇒ before(c,a) False), both seeds (0, 7).
- **J329b (what happened first):** `what_first` returns the unique earliest event (no predecessor), both seeds.
- **J329c (persists):** answers identical after reload.

Predicted most-likely failure: `what_first` is O(events²) over climbs; a dropped deep edge could make a late event
look first. Routing/climb should hold at this size; if J329b misses, report whether a before-edge failed to climb.

## Result (seeds 0, 7): **PASS**
- **J329a:** `happened_before` vs before-closure = **1.0** (transitive multi-hop AND asymmetric: protest→peace
  True, peace→protest False), both seeds. **PASS.**
- **J329b:** `what_first` = **{drought, protest}** = ground truth (two independent event chains, each with its own
  earliest event), both seeds. **PASS.**
- **J329c:** identical after reload. **PASS.**

## Verdict: **PASS**
The durable store answers temporal ordering (before/after — transitive and asymmetric) and "what happened first",
bridged from the engine's `_orders['before']`. `before` is a directed transitive relation, so it reuses the
validated climb (JEP-298/307) directly — sequence/time is now in the reasoning suite. Correctly handles MULTIPLE
timelines (two chains → two firsts). Established temporal precedence over a DAG, named as such; no transformer.

