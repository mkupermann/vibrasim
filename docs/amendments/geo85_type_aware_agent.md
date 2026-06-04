# GEO-85 — Type-aware agent: auto-kind-routing eliminates cross-type confusion

## Motivation
GEO-83/84: cross-type retrieval confusion ("the pipe fixing person" -> a 'fix' TASK over the plumber CONTACT)
is the recurring personal-KB miss. Fix: a TYPE-aware layer that detects the query's target kind and scopes
retrieval (kind-scoped retrieval shipped in GEO-83). GEO-85 adds auto-kind-routing and verifies it removes
the cross-type miss end-to-end on the personal KB, including the vague queries.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes). A kind-router: keyword/semantic cues map a query to its target kind
  (who/person/role -> contact; task/due/when/fix -> task; note/about -> note); fall back to unscoped.
- Re-run the GEO-83 + GEO-84 queries with kind-scoped retrieval driven by the router.
- Metric: accuracy with auto-kind-routing vs without (GEO-83 0.90, GEO-84 vague 0.88). Bar: >= 0.95 combined
  (the cross-type misses are removed). NULL if routing mis-detects and hurts.
