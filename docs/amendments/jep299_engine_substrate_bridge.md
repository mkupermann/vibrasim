# JEP-299 — The reading brain remembers across sessions: Understanding Engine → persistent substrate store

## Motivation
JEP-298 gave the substrate durable, directed, multi-hop memory. The Understanding Engine reads English into an
is-a DAG (`e.parents`) but that lives in RAM Python dicts. Bridge the engine's learned taxonomy INTO a
`SubstrateMemory(directed=True)`, persist it, and answer multi-hop questions FROM THE RELOADED SUBSTRATE (engine
gone) — so the reading brain's knowledge survives close+reopen and is reasoned over through the substrate itself,
not the engine's data structures. No transformer, no pretrained model.

## Method
`e.read(corpus)` → for each child→parent in `e.parents`, `mem.add_fact(child, "isa", parent)` (directed). Save
`mem`; reload into a FRESH `SubstrateMemory`; answer `is_a(x, y)` by the JEP-298 gated climb. Ground truth = the
engine's own `e.is_a(x, y)` on the SAME query set (all true descendant→ancestor pairs from the DAG's transitive
closure as positives + matched random non-pairs as negatives).

## Pre-registered bars (BEFORE the run)
- **J299a (transfers + reasons after reload):** substrate-store answers match the engine's `is_a` ground truth on
  the full query set ≥ 0.90 (incl. multi-hop positives it was never told directly), both seeds (0, 7).
- **J299b (1-hop coverage / faithful bridge):** every is-a edge in `e.parents` is recovered 1-hop from the
  RELOADED substrate ≥ 0.95, both seeds.
- **J299c (persists):** reloaded-store answers identical to pre-save answers, both seeds.

Predicted most-likely failure: deep chains (≥5 hops) accumulate per-hop similarity decay below the gate → some
true deep positives read False, dropping J299a under 0.90. If so, report the max faithful depth as the finding
(not a gate tweak); the bridge/persistence (J299b/c) would still stand.

## Result (seeds 0, 7): **PASS**
- **J299a:** substrate-store answers match the engine's `is_a` ground truth = **1.000** over 70 queries
  (35 multi-hop positives + 35 negatives), both seeds. **PASS.**
- **J299b:** 1-hop coverage of all 14 is-a edges from the RELOADED store = **1.000**, both seeds. **PASS.**
- **J299c:** reloaded answers identical to pre-save, both seeds. **PASS.**
- Concrete demo: after the engine is discarded and the store reloaded from disk, `is_a(poodle, organism)` =
  **True** (4 hops, never told directly) — answered by the substrate alone.

## Verdict: **PASS**
The reading brain's learned taxonomy now lives in the **durable substrate**: read English → bridge into
`SubstrateMemory(directed=True)` → save → reopen → the substrate by itself answers multi-hop questions matching
the engine, perfectly. This connects the whole arc end to end: **read (Understanding Engine) → store/persist/grow
(JEP-294/295/296) → reason transitively (JEP-298) → all survive a restart (here)**. Honest scope: the bridge
carries the is-a DAG; richer relations (part-of, causal, properties) are a mechanical extension of the same
`add_fact` path, not yet measured.

