# GEO-90 — Quantitative operators: range, sum, sort (completing operator coverage)

## Motivation
Count (GEO-18) and compare (GEO-51) are validated. Real quantitative queries also need RANGE ("due within 2
years"), SUM ("total budget"), and SORT ("tasks by date"). GEO-90 completes the quantitative operator coverage
over the structured store — geometry/structure resolves the entities, the symbolic layer computes.

## Pre-registration (locked BEFORE run)
- Store with numeric attributes (tasks with due-year, items with amounts).
- Queries: RANGE (tasks due in [2024,2025]), SUM (total of amounts), SORT (entities by a numeric key), plus
  a combined range+filter.
- Operators: pure symbolic over meta. Metric: exact correctness on each. Bar: all correct (>=0.9). These are
  set-logic/arithmetic — expected exact; the value is completing coverage, not uncertainty.

## Result — PASS (1.00, operator coverage complete)
range / sum / sort / combined all OK. Operator set now complete: count(18) compare(51) negate(53)
range/sum/sort(90) join(42) temporal(47) contradiction(41/52) conflict(62) ambiguity(65) counterfactual-sim(77).
Predictable symbolic set-logic (as flagged GEO-62/65/77) — completes coverage, not a research finding.
