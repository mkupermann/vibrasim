# JEP-473 — Temporal sequences: "then" chains + first/last endpoints

## Motivation
JEP-472 added before/after. Narrative text is SEQUENCES ("first X, then Y, then Z") and asks "what
happened first/last?". JEP-473 adds the "then" connective and the endpoint queries — the next rung of
narrative understanding.

## Method (`world/conversation.py`, `world/brain_query.py`, runner)
- Parse "X, then Y" / "First X, then Y" / "X then Y" → `(X, before, Y)`; chained "X, then Y, then Z" →
  both edges. (`conversation.py`.)
- `brain_query`: "what happened/came first?" → the SOURCE of the before-graph (a node with outgoing
  `before` and no incoming); "what happened/came last?" → the SINK (incoming, no outgoing).

## Pre-registered PREDICTION + bars (BEFORE the run, via live Conversation)
World: "First sunrise, then noon, then sunset." (chained "then")
- **J473a (then-chain stored + transitive):** "is sunrise before sunset?" → yes (sunrise→noon→sunset),
  both seeds.
- **J473b (endpoints):** "what happened first?" → sunrise; "what happened last?" → sunset, both seeds.
- **J473c (no regression):** JEP-472 before/after still works; substrate_memory + conversation suites
  pass.

PASS = the brain ingests "then" sequences and answers first/last endpoints. NULL if parsing/queries
fail. Bars locked; no retuning. Established (transitive relation + graph source/sink), named; a new
capability, not new science. No transformer.

## RESULT (2026-06-05): **PASS** — 'then' sequences + endpoints work
Both seeds: "First sunrise, then noon, then sunset." -> (sunrise,before,noon),(noon,before,sunset);
"is sunrise before sunset?" -> **Yes** (transitive); "what happened first?" -> **Sunrise** (source);
"what happened last?" -> **Sunset** (sink). JEP-472 before/after intact; substrate_memory 14/14 +
conversation 10/10 green. J473a/b ✓ -> PASS. Another rung of narrative understanding (the books wall):
the brain now reads 'then' sequences and finds their start/end. Established (transitive relation + graph
source/sink), named; new capability, not new science.
