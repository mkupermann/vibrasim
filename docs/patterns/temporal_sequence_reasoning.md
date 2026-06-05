# Pattern — Temporal / event-sequence reasoning

**Surfaced:** JEP-472→475 (2026-06-05). **Status:** built, live in the GUI, tested (clean-room).

## The mechanism
Narrative text is SEQUENCES of events; the brain needed to store and reason about order. Built on the
durable relational store as a single transitive relation `before`, no transformer:

1. **Ingest** (`world/conversation.py`): "X (comes/happens/…) before/after Y" → `(X, before, Y)`;
   "First X, then Y, then Z" → consecutive `before` edges.
2. **Forward / backward** (`world/brain_query.py`): "what comes after X?" → the Y with `(X, before, Y)`;
   "what comes before X?" → the Y with `(Y, before, X)`.
3. **Transitive** order: "is X before Y?" → `_before_reachable` BFS over `before` edges (X→…→Y).
4. **Endpoints**: "what happened first/last?" → SOURCE / SINK of the before-graph (no incoming / no
   outgoing edge).
5. **Timeline**: "what is the sequence/order/timeline?" → Kahn topological sort → the full ordered list.
6. **Between**: "what happens between X and Z?" → events e with X before e and e before Z, returned in
   temporal order.

## Honest scope
`before` is a standard transitive relation; the queries are standard graph ops (reachability, source/
sink, topological sort, path interior). Established, named — the contribution is the substrate-native
integration: the first concrete rung toward NARRATIVE (sequence) text, a core gap behind the books wall.
Events are still single-token nouns; extracting VERB-events from real prose ("the hero trained, then
fought") is the harder open step. Not new science.

## Reuse
Any ordered/precedence structure (event timelines, dependency chains, build steps, plot order) maps to a
`before` relation + these queries. Pair with the causal relation (`causes`) for cause-and-sequence
narrative. Test runners MUST use a fresh `brain_dir` (calibration lesson #16), never the persisted brain.
