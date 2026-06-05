# JEP-218 — 'why?' explains comparison and temporal chains (full reasoning transparency)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 tracking the last comparison/temporal query and rendering its order chain closes the gap. RISK: interaction
  with the existing is-a/part-of/causal recency tracking.

## Result — PASS (HIT)
The full-Q&A demo (JEP-217) revealed that 'why?' justified only is-a/part-of/causal answers, not comparison/temporal.
Extended it: the comparison and temporal query handlers now record `_last_rel_query = ('order', x, z, comp)` (clearing
the is-a `_last_query`), and the 'why?' handler renders the order chain via `_rel_chain` over `_orders[comp]`:
- 'is an elephant bigger than a mouse?' -> 'why?' -> 'Because an elephant is bigger than a dog, and a dog is bigger
  than a cat, and a cat is bigger than a mouse.' (full transitive comparison chain).
- 'did the war happen before the peace?' -> 'why?' -> 'Because a war is before a treaty, and a treaty is before a peace.'
- is-a 'why?' still works with correct recency.
So 'why?' now explains the reasoning chain across ALL transitive/relational query types (is-a, part-of, causal,
comparison, temporal) — full reasoning transparency, completing 'communicate WITH me'. 85/85 regression tests green
(+1). Prediction HIT; tally 107/134. Established (template explanation from inference chains); named; no novelty.
