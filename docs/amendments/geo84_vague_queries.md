# GEO-84 — Robustness to VAGUE / underspecified natural queries

## Motivation
Real users ask vague, underspecified questions ("that budget thing", "the plumber guy", "when's the tax
thing due"), unlike clean test queries. GEO-84 tests whether semantic matching handles vagueness on the
personal KB — a real robustness question for actual use.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes, GEO-83). For ~8 facts, write a VAGUE colloquial query and the matching
  fact. Compare retrieval on VAGUE vs CLEAN phrasing of the same query.
- Metric: vague-query hits@1 vs clean-query hits@1. Bar: vague >= 0.7 (handles vagueness) and within 0.2 of
  clean. Honest: if vague << clean, the system needs well-formed queries (a real UX limitation).
