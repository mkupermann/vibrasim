# JEP-173 — 'why?' explains the reasoning chain across ALL relation types (is-a, part-of, causal)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 recording the last part-of/causal query + chain-explanation finders lets 'why?' explain part-of ('Because a
  cell is part of a heart, and a heart is part of a dog') and causal chains, completing explanation across all
  relation types. RISK: interaction with the existing is-a _last_query (must track which type was last).

## Result — PASS (HIT)
Previously 'why?' only justified is-a answers ('You haven't asked me a question I can justify yet' after part-of/
causal). Added: a generic _rel_chain(graph, x, z) BFS path finder; recording self._last_rel_query=(kind,x,z) on a
True part-of/causal answer (clearing _last_query, and vice-versa for is-a, so RECENCY is correct); and extending the
'why?' handler to render the chain. Now:
- 'is a cell part of a dog?' -> 'why?' -> 'Because a cell is part of a heart, and a heart is part of a dog.'
- 'does a virus cause a fever?' -> 'why?' -> 'Because a virus causes an infection, and an infection causes a fever.'
- 'is a dog an animal?' -> 'why?' -> 'Because a dog is a mammal, and a mammal is an animal.' (recency: is-a wins)
The engine now provides full reasoning TRANSPARENCY across all three relation types — it does not just answer, it
shows the multi-step chain, for taxonomy, mereology, AND causation. Completes the explanation capability; directly
serves 'communicating WITH me'. 55/55 regression tests green (+1). Prediction HIT; tally 65/89. Established (template
explanation from inference chains); named; no novelty.
