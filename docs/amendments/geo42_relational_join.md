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
