# GEO-87 — Complete integrated agent (LinearRouter + kind-scoping + operators + grounding) end-to-end

## Motivation
All best-practice components are validated and shipped (LinearRouter GEO-86, kind-scoped retrieval GEO-83,
operators, grounding). GEO-87 assembles them into ONE agent — train a kind-router, scope retrieval by routed
kind, apply operators, ground/abstain — and verifies it answers the personal-KB queries (incl. the cross-type
vague ones) end-to-end, the complete usable system.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes). Train a LinearRouter (kind). Agent: route kind -> kind-scoped retrieve
  -> answer; symbolic count/temporal where applicable; abstain out-of-KB.
- Test set: the GEO-83 + GEO-84 + GEO-85 queries (factoid/semantic/temporal/aggregation/vague/cross-type) +
  out-of-KB.
- Metric: overall accuracy. Bar: >= 0.9 (the complete agent fixes the cross-type miss end-to-end and handles
  the full mixed workload). PASS = the assembled best-practice agent works.
