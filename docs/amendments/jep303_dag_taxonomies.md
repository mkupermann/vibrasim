# JEP-303 — DAG taxonomies: set-valued parent retrieval (multi-parent is-a)

## Motivation
The pattern doc's last named limitation: `query` returns only the single best parent, so a multi-parent node
(a penguin is a bird AND a swimmer; a platypus is a mammal AND an egg-layer) loses a branch. Feasibility check
confirmed both parents of a 2-parent node surface far above noise (0.39/0.37 vs ~0.00). Add `query_all` (all values
above the gate) and a DAG BFS climb, so the substrate handles directed acyclic taxonomies, not just trees.

## Pre-registered bars (BEFORE the run)
- **J303a (set-valued retrieval):** for every node, `query_all(node, "isa", gate)` recovers its EXACT direct-parent
  set (precision = recall = 1.0 per node) on a taxonomy with several 2-parent nodes, averaged ≥ 0.95, both seeds.
- **J303b (DAG multi-hop):** is-a by BFS over `query_all` matches the engine's `is_a` ≥ 0.90 on a balanced query
  set including ancestors reachable via EITHER branch, both seeds (0, 7).
- **J303c (persists):** answers identical after a fresh reload, both seeds.
- **No-regression:** JEP-298 (single-parent directed climb) and JEP-301 (inheritance) still PASS.

Predicted most-likely failure: with k parents the per-parent similarity falls ~1/√(load); a node with many parents
plus high total load could push a true parent below the gate (recall miss) or lift a crosstalk value above it
(precision miss). If J303a < 0.95, report the max parent-count / load at which set retrieval stays clean.

## Result (seeds 0, 7): **PASS**
- **J303a:** exact direct-parent SET recovery = **1.000** across all nodes (3 are 2-parent: penguin, platypus,
  bat), both seeds. **PASS.**
- **J303b:** DAG multi-hop is-a (BFS over `query_all`) matches engine = **1.000**, both seeds. **PASS.**
- **J303c:** identical after reload. **PASS.** **No-regression:** JEP-298 & JEP-301 still PASS. **PASS.**
- Demo: `query_all(penguin, isa)` = {bird, swimmer}; `penguin is animal` = True (via either branch);
  `platypus is animal` = True.

## Verdict: **PASS**
`query_all` (all values above the gate) + a BFS climb let the substrate handle multi-parent DAG taxonomies, not
just trees — matching the engine over the persistent store. Closes the last named limitation of the durable VSA
memory pattern. The k parents of a node co-exist in the bundle and each surfaces well above noise (0.39/0.37 vs
~0.00 at this load); at much higher per-node fan-out the 1/√load decay would eventually require more dimension
or a module split (the JEP-296 lever).

