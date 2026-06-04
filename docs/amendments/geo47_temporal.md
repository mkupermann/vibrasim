# GEO-47 — Temporal reasoning: time-scoped queries over versioned facts

## Motivation
Real knowledge changes over time. A store should answer time-scoped queries ("what team was X on in 2023?")
over versioned facts. Hybrid: geometric retrieval gathers the entity's facts; symbolic temporal filter picks
the one valid at the queried time. GEO-47 tests this genuinely-different (temporal) dimension.

## Pre-registration (locked BEFORE run)
- 8 people, each with 2-3 TIME-STAMPED team assignments (valid-from year). E.g. Alice: Analytics from 2020,
  Platform from 2023.
- Query: "Which team was <P> on in <year>?" -> answer = the assignment with the latest valid-from <= year.
- Method: retrieve all facts about P (geometric, by subject) -> symbolic: filter valid-from <= year, take
  latest. 12 (person, year) test cases spanning before/between/after changes.
- Metric: accuracy. Bar: >= 0.8 (the hybrid handles temporal scoping). Compare to a NON-temporal baseline
  (latest fact only) which should fail on past-year queries. NULL if retrieval can't gather a person's facts.

## Result — PASS
| method | accuracy |
|--------|----------|
| temporal hybrid (gather + time-filter) | **1.00** |
| non-temporal baseline (latest fact) | 0.50 |

**VERDICT: PASS.** Time-scoped queries over versioned facts work at 1.00: geometric gather of an entity's
facts + symbolic temporal filter (latest valid-from <= queried year). A non-temporal baseline (latest fact,
ignoring year) gets only 0.50 — failing all past-year queries. Temporal reasoning is another instance of the
unifying principle (GEO-18/20/41/42/47): geometry RESOLVES/GATHERS, the symbolic layer OPERATES (here, a
time filter). The system handles versioned/temporal knowledge stores.
