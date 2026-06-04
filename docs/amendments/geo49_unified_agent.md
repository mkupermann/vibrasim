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

## Result — PASS (1.00 end-to-end on mixed workload)
| intent | correct |
|--------|---------|
| FACTOID | 4/4 |
| COUNT | 4/4 |
| TEMPORAL | 4/4 |
| JOIN | 4/4 |
| **overall** | **16/16 = 1.00** |

**VERDICT: PASS.** The UnifiedReasoner (tools/unified_reasoner.py) answers a MIXED query workload end-to-end
at 1.00: it symbolically ROUTES each query to the right intent, GEOMETRICALLY resolves entities, and applies
the SYMBOLIC operator (retrieve / count / time-filter / join) — one agent for all reasoning types. The
capstone assembly of the architecture.

**Honest scope.** The operator implementations are SCHEMA-SPECIFIC (person/team/city) — this demonstrates the
auto-dispatch PATTERN works end-to-end, not a fully schema-general agent. A general version would need schema-
agnostic operators (e.g., generic group-by/join over arbitrary meta fields). The pattern (route->resolve->
operate) generalizes; the wiring is per-schema. Clean small entities, so resolution is reliable.
