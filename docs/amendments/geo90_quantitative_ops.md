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
