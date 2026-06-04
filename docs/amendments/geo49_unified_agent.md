# GEO-49 — Unified auto-dispatching reasoner (route -> resolve -> operate), end-to-end on mixed queries

## Motivation
GEO-48b gave the architecture (symbolic router -> geometric resolver -> symbolic operator). GEO-49 ASSEMBLES
it into one UnifiedReasoner and tests it on a MIXED query workload spanning factoid/count/temporal/join, to
validate the full auto-dispatch pipeline works end-to-end as a single usable agent.

## Pre-registration (locked BEFORE run)
- KB: employees with team + (team->city) + time-stamped assignments (for temporal).
- UnifiedReasoner.answer(q): symbolic-route intent -> dispatch (FACTOID=retrieve, COUNT=resolve+count,
  TEMPORAL=gather+time-filter, JOIN=resolve+join) -> answer.
- Mixed test set (locked): 4 factoid, 4 count, 4 temporal, 4 join = 16 queries with known answers.
- Metric: end-to-end accuracy (correct answer). Bar: >= 0.8 across the mixed workload (the unified agent
  dispatches and answers correctly). Report per-type. NULL if routing/dispatch breaks it.
