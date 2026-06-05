# JEP-475 — Temporal 'between' query (events on the path between two points)

Extension of the temporal arc (JEP-472/473/474). "what (happens|comes|is) between X and Z?" -> the
events e with X before e before Z (on the timeline path), returned in temporal order. Pre-registered
bar (deterministic): correct intermediate events, temporally ordered; adjacent pair -> none.

## RESULT (2026-06-05): **PASS**
- "First sunrise, then noon, then sunset." -> "between sunrise and sunset?" -> **noon**.
- breakfast<lunch<dinner<bedtime -> "between breakfast and bedtime?" -> **"lunch, dinner"** (temporal order).
- "between breakfast and lunch?" (adjacent) -> none ("don't know"). substrate_memory 14/14 + conversation 10/10 green.

Rounds out the temporal/narrative sub-arc (472 before/after -> 473 then+endpoints -> 474 timeline -> 475
between): the brain reads event sequences and answers order, endpoints, timeline, and what lies between
two events. Established (transitive relation + path queries), named; new capability, not new science.
