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
## Result — PASS (1.00; two "misses" were ground-truth errors in my test)
Recorded mean-F1 = 0.95. The two sub-1.0 cases ("Platform AND >110", "Denver AND >100") returned {Bob,Eve}
— which is CORRECT: my pre-registered expected sets wrongly included Nina, who is on Product/Seattle (salary
115), NOT Platform/Denver. So the SYSTEM was right and MY ground truth was wrong; true accuracy = 1.00.

**VERDICT: PASS.** Conjunctive multi-constraint queries compose correctly: extract multiple constraints
(team / city / salary-threshold) + symbolic AND-filter over geometric resolutions. Already cleared the 0.85
bar at 0.95; the residual was a test-data error of mine, not a system failure (honest correction, not post-
hoc tuning — the system passed regardless). Conjunctive composition is another instance of the principle:
geometry/structure RESOLVES the field values, the symbolic layer ANDs the predicates. Genuinely uncertain
fork (does the parser find all constraints?) resolved positively.
