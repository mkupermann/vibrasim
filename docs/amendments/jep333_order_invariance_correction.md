# JEP-333 — Robustness: order-invariance of answers + correction-by-negation

## Motivation
The durable store assigns facts to modules by TEACH ORDER (neurogenesis splits when a module fills), and routes
queries to the holding module. Does the order facts are taught change the ANSWERS? It must not. Also: when a fact
is later contradicted ("X is a Y" then "X is not a Y"), the store should reflect the correction. Two real
robustness properties for an interactive, incrementally-taught brain. No transformer.

## Method
- **Order-invariance:** teach the SAME fact set in 5 random orders (each into its own store, near/over a module
  boundary so splits differ), answer a fixed query set, check all orders agree.
- **Correction:** teach `(X, isa, Y)` then `(X, not_isa, Y)`; `BrainQuery.is_a(X, Y)` must be False (negation
  overrides). Same for a property exception.

## Pre-registered bars (BEFORE the run)
- **J333a (order-invariance):** across 5 random teach orders, the answer set is IDENTICAL (pairwise agreement
  = 1.0) on a mixed query set (is-a multi-hop + membership), both seeds (0, 7).
- **J333b (correction):** after teaching a fact then its negation, the answer flips correctly (is_a → False;
  property exception → False), both seeds.
- **J333c (persists):** corrected answers survive reload.

Predicted most-likely failure: order could matter if a multi-value key (DAG parent) gets split across two modules
in one ordering but not another, and routing only searches one — but `key_modules` stores a SET of modules, so all
holders are searched. If J333a < 1.0, report the key whose modules diverged (a routing-set completeness check).

## Result (seeds 0, 7): **PASS**
- **J333a:** across 5 random teach orders (small cap → ~3 modules, splits differ by order), the full answer set is
  **identical** (agreement = **1.0**), both seeds — answers are invariant to teach order because `key_modules`
  stores a SET of holding modules and routing searches all of them. **PASS.**
- **J333b:** correction-by-negation flips the answer — whale taught as fish then `not_isa fish` → is_a(whale,fish)
  **False**, is_a(whale,animal) **True**; penguin `not_hasprop fly` → has_property **False**, both seeds. **PASS.**
- **J333c:** corrected answers survive reload. **PASS.**

## Verdict: **PASS**
The durable, incrementally-taught store is ROBUST: identical answers regardless of the order facts were taught
(neurogenesis splits differ, but per-key module-set routing makes retrieval order-invariant), and a later negation
cleanly overrides an earlier mistaught fact — durably. Both are essential for an interactive teach-and-correct
brain. Honest note: "correction" here is override-by-negation (defeasible, JEP-305), not physical removal from the
superposition — the wrong positive fact still occupies bundle capacity; a compaction pass would reclaim it (future
work). No transformer.

