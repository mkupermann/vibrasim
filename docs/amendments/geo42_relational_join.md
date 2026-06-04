# GEO-42 — Relational JOIN queries (same-as, comparison across entities)

## Motivation
Beyond single chains, understanding a knowledge base needs RELATIONAL queries that join across entities:
"who works in the same city as X?", "are X and Y on the same team?". Hybrid: geometric resolution of each
entity's attribute (chain) + symbolic JOIN/compare over the resolved values. GEO-42 tests this richer
reasoning pattern.

## Pre-registration (locked BEFORE run)
- KB: 12 people, each with team + (team->city). Several share city/team.
- (A) "Who works in the same city as <P>?" -> resolve P's city (chain), return the SET of others whose
  resolved city matches. Metric: set-F1 vs ground truth, averaged.
- (B) "Are <X> and <Y> on the same team?" -> resolve both teams, compare. 12 pairs (mix same/different).
  Metric: yes/no accuracy.
- Bars: (A) mean F1 >= 0.7; (B) accuracy >= 0.8. PASS if both. Hybrid geometric-resolve + symbolic-join.
  NULL if resolution errors break the joins.

## Result — PASS
| query type | result |
|------------|--------|
| (A) same-city join (set-F1) | **1.00** |
| (B) same-team comparison (acc) | **1.00** |

**VERDICT: PASS.** Relational JOIN queries work: geometric entity resolution (chain person->city / person->
team) + symbolic join/compare answers "who works in the same city as X" (F1 1.00) and "are X and Y on the
same team" (1.00). Richer-than-chaining relational reasoning over the store. (Clean small entities, so
resolution is reliable; the join is symbolic and exact.)

## Unifying principle (GEO-18/20/41/42)
Every reasoning operation BEYOND pure retrieval follows ONE pattern: **geometry RESOLVES (relevance,
entities, relations); the symbolic layer OPERATES (count, negate, compare, join, detect contradictions).**
Aggregation (GEO-18), negation/comparison (GEO-20), contradiction detection (GEO-41), and relational joins
(GEO-42) are all instances. Pure geometry alone is at/below chance on the symbolic part each time; the hybrid
solves it. This is the architectural core: a geometric resolver feeding a thin symbolic operator layer.
