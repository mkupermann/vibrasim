# JEP-474 — Timeline reconstruction (topological sort of before-edges)

Small deterministic extension of the temporal arc (JEP-472/473). "what is the sequence/order/timeline?"
-> Kahn topological sort of the `before` graph -> the full ordered event list. Pre-registered bar
(deterministic): the reconstructed order equals the taught chain.

## RESULT (2026-06-05): **PASS**
- "First sunrise, then noon, then sunset." -> "what is the sequence?" -> **"sunrise, noon, sunset"**;
  "what is the order?" -> same.
- "Breakfast before lunch / lunch before dinner" -> "what is the timeline?" -> **"breakfast, lunch, dinner"**.
- substrate_memory 14/14 + conversation 10/10 green.

Caps the temporal/narrative sub-arc (472 before/after -> 473 then-chains+endpoints -> 474 full timeline):
the brain now reads event sequences and reconstructs their order. Established (transitive relation +
topological sort), named; new capability, not new science. No transformer.
