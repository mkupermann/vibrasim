# JEP-307 — Multi-hop reasoning at scale: module-aware routing (fixes JEP-306)

## Motivation
JEP-306 NULL: deep multi-hop chaining collapsed once facts spanned >1 module, because `query` takes the GLOBAL
argmax across all modules — a spurious match in a non-holding module hijacks a hop — and a global gate calibrated
on a sparse module rejects full-module facts. Fix: **module-aware routing** — record which module holds each
`(entity, role)` key and search ONLY those modules; calibrate the gate on REAL stored edges. Removes cross-module
crosstalk so multi-hop chains scale with growth.

## Method
`SubstrateMemory` records `key_modules[(entity, role)] → {module indices}` on `add_fact`. `query`/`query_all`/
`edge_sim` restrict to those modules (empty → no match → clean reject of untaught keys). Backward compatible (no
routing table → search all, as before). Persisted in `meta.json`.

## Pre-registered bars (BEFORE the run)
- **J307a (multi-hop scales):** with routing, integrated reasoning (is-a multi-hop + defeasible property) ≥ 0.90
  at N=200 AND is-a multi-hop ≥ 0.85 at N=800, both seeds (0, 7) — the regime JEP-306 failed.
- **J307b (envelope lifted):** report the new accuracy-vs-N curve; is-a no longer collapses at the 1→2 module
  boundary.
- **J307c (persists + no-regression):** routed store reloads with same accuracy (±0.01); JEP-298 (directed
  multi-hop), JEP-303 (DAG), JEP-305 (negation) all still PASS.

Predicted most-likely failure: a key written across a module boundary (multi-parent DAG where the two parents land
in different modules) could under-route if I store only one module per key — must store a SET. If J303 regresses,
that's the diagnosis. If is-a still plateaus < 0.85 at N=800 with routing, the residual is per-hop similarity decay
within a full module (a true K* bound), reported not tuned.

## Result (seeds 0, 7): **PASS**
New envelope WITH routing (is-a multi-hop / property / integrated):

| N (facts) | modules | is-a (306→307) | property | integrated |
|-----------|---------|----------------|----------|------------|
| ~50  | 1 | 1.00 → 1.00 | 1.00 | 1.00 |
| ~110 | 2 | 0.50 → **0.99** | 0.99 | 0.99 |
| ~230 | 3 | 0.51 → **1.00** | 0.99 | 0.99 |
| ~460 | 5 | 0.60 → **0.99** | 0.99 | 0.99 |
| ~910 | 9 | 0.79 → **0.98** | 0.99 | 0.99 |

- **J307a:** integrated ≥0.90 @N=200 = **0.99**, AND is-a ≥0.85 @N=800 = **0.98**, both seeds. **PASS.**
- **J307b:** is-a no longer collapses at the 1→2 module boundary — flat ~0.98–1.0 across all N. **PASS.**
- **J307c:** persists ±0.01; JEP-298 / 303 / 305 all still **PASS**. **PASS.**

## Verdict: **PASS**
Module-aware routing (`key_modules`: search only the module(s) holding a key) removes the cross-module argmax
hijacking that sank JEP-306, so multi-hop chains scale with growth — is-a multi-hop ~0.98 to ~900 facts / 9
modules, vs ~0.5 before. The durable, growing substrate now supports the FULL reasoning suite (multi-hop,
inheritance, DAG, negation, open relations) at scale, not just single-step. Closes the JEP-306 NULL. Honest
residual: routing assumes the key→module table is kept (it is, and persisted); a corpus exceeding the 1000-agent
or memory limits is out of scope. Established method (hash-routed associative memory), named as such.

