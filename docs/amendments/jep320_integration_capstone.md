# JEP-320 — Grand integration capstone: the whole stack in one reloaded store

## Motivation
Each capability (JEP-294..319) was validated in isolation. Lock the INTEGRATED system: build ONE durable store
holding a taxonomy + properties/exceptions + causal + open relations + a family tree, persist it, RELOAD (fresh
object), and exercise every operation against that single reloaded store — proving the pieces compose and survive a
restart together. One regression for the whole arc. No transformer.

## Method
Bridge a mixed corpus into `SubstrateMemory(directed=True)`; `save`; `load` into a fresh object; then run, against
the reloaded store: is-a multi-hop, inheritance, negation/exception, DAG (multi-parent), abduction, contradiction
detection, induce-symmetry/transitivity (316), discover-inverse (318), induce-composition (319). Each checked vs
ground truth.

## Pre-registered bars (BEFORE the run)
- **J320a:** ALL ten operation checks pass on the single reloaded store, both seeds (0, 7) — each at its own
  established bar (membership/multi-hop ≥0.90, induction exact, contradiction P=R=1).
- **J320b:** the store is genuinely reloaded (fresh object, no shared RAM) and the value-vocabulary / routing table
  survive — i.e. operations use the persisted state only.

Predicted most-likely failure: interactions at the boundary — e.g. the open-relation roles or the inverse seeds
inflating the value vocabulary and shifting the global gate, dropping one multi-hop op below 0.90. If one op misses
only in the integrated store (but passed standalone), that's a cross-feature interference finding, reported not
tuned.

## Result (seeds 0, 7): **PASS**
- **J320a:** all 11 operation checks pass on the single reloaded 36-fact store, both seeds:
  is-a multi-hop, inheritance, negation/exception, DAG (penguin→{bird,swimmer}), negative-is-a, abduction
  (cancer←{smoking,radiation}), open relation (cat eats fish), contradiction (robin swim flagged),
  induce-symmetry (married_to), discover-inverse (parent_of↔child_of), induce-composition (grandparent). **PASS.**
- **J320b:** all run against a FRESH `SubstrateMemory.load` (no shared RAM); routing table + value vocabulary
  survived. **PASS.**

## Verdict: **PASS**
The whole stack — every reasoning and meta-learning operation from JEP-294..319 — composes in ONE durable store and
survives a restart together, with no cross-feature interference (the predicted gate/vocabulary boundary issue did
not appear at this scale). This is the integration regression for the entire arc: read/bridge → store → persist →
reload → reason → learn rules, end to end, no transformer.

