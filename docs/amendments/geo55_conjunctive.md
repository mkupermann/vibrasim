# GEO-55 — Conjunctive multi-constraint queries (compose constraints with AND)

## Motivation
Single operators are validated. Real queries often AND multiple constraints: "who is on Analytics AND based
in Boston?", "who is on Platform AND earns more than 100k?". This needs constraint EXTRACTION (multiple) +
symbolic AND-filter. GEO-55 tests whether the system composes constraints — a genuine step up in query
complexity with real uncertainty (does the parser find all constraints?).

## Pre-registration (locked BEFORE run)
- 12 people with team + city(via team) + salary. Conjunctive queries with 2 constraints each (team+salary,
  city+salary, team+city), 8 queries, known answer sets.
- Method: extract each constraint (regex over known field values + numeric thresholds), AND-filter the rows.
- Metric: set-F1. Bar: >= 0.85 (the system composes constraints). Report which constraint types parse.
  NULL if multi-constraint extraction fails.
