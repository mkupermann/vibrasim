# JEP-300 — Full multi-relational knowledge through the persistent substrate (is-a, part-of, causal, property)

## Motivation
JEP-299 bridged only the is-a DAG. Close the honest gap: bridge ALL the Understanding Engine's learned relation
types — is-a and part-of (both transitive), causal and property (multi-valued, 1-hop) — into one persistent
`SubstrateMemory(directed=True)`, and after a reload answer mixed-relation questions matching the engine. Distinct
role vectors per relation ("isa","partof","causes","hasprop") keep them from colliding. No transformer.

## Method
`e.read(corpus)` → bridge `e.parents` (isa), `e.part_of_g` (partof), `e.causes` (causes), `e.properties` (hasprop)
as directed facts. Transitive relations (isa, partof) answered by the JEP-298 gated climb; multi-valued relations
(causes, hasprop) by the new `contains()` membership probe (max-over-modules edge similarity ≥ gate). Save →
reload (engine discarded) → score against the engine's own `is_a / part_of / causes_effect / has_property`.

## Pre-registered bars (BEFORE the run)
- **J300a (multi-relational reasoning after reload):** on a mixed query set — is-a multi-hop, part-of multi-hop
  (within part-of chains), causal 1-hop (+ negatives), property 1-hop (+ negatives) — substrate answers match the
  engine ≥ 0.90, both seeds (0, 7).
- **J300b (coverage):** every stored edge of every relation recovered 1-hop / membership-true from the RELOADED
  store ≥ 0.95, both seeds.
- **J300c (persists):** reloaded answers identical to pre-save, both seeds.
- **No-regression:** JEP-298 (directed is-a) and JEP-296 (symmetric) still PASS.

Predicted most-likely failure: the single `contains()` gate calibrated on is-a edges may not fit causal/property
edge-similarity (different fan-out), pushing J300a < 0.90 on those relations. If so, report per-relation accuracy
and that each relation needs its own gate — a finding, not a tuned global threshold. Cross-relation inheritance
(part-of across is-a, e.g. heart∈dog ⇒ heart∈poodle) is engine-side multi-relation reasoning the single-relation
climb does NOT replicate; excluded from the query set and reported as a known boundary, not hidden.

## Result (seeds 0, 7): **PASS**
- **J300a:** substrate vs engine = **1.000** over 66 mixed queries; per-relation **isa 1.0, partof 1.0,
  causes 1.0, hasprop 1.0**, both seeds. **PASS.**
- **J300b:** coverage of all stored edges (transitive 1-hop + multi-valued membership) = **1.000**, both seeds.
  **PASS.**
- **J300c:** reloaded answers identical to pre-save, both seeds. **PASS.**
- **No-regression:** JEP-296 and JEP-298 re-run still **PASS**. **PASS.**

Note: the predicted single-gate risk did not bite — the is-a-calibrated gate cleanly separated taught from
untaught across all four relations at this scale. (At higher fan-out/load a per-relation gate may still be needed;
not required here.)

## Verdict: **PASS**
The reading brain's FULL learned knowledge — is-a, part-of (both transitive, answered by multi-hop climb), causal
and property (multi-valued, answered by the `contains()` membership probe) — lives in one durable, growing
substrate store and is reasoned over after close+reopen, matching the engine exactly. Honest boundary (as
pre-registered): cross-relation inheritance (part-of across is-a) is engine-side multi-relation reasoning not
replicated by a single-relation climb — excluded from scope and named, not hidden. Arc fully closed: read →
multi-relational store → persist → grow → reason → survive restart.

