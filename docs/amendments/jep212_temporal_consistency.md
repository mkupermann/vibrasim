# JEP-212 — temporal consistency: detect an impossible timeline (cycle) — consistency across ALL domains

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 detecting a cycle in the 'before' order ('X before Y' and 'Y before X') flags a temporal contradiction in
  consistency_audit; a consistent timeline doesn't flag. RISK: cycle detection cost — keep to direct-edge checks.

## Result — PASS (HIT)
consistency_audit() now also detects TEMPORAL cycles: for each direct 'a before b' edge, if the transitive closure
also has 'b before a', that is an impossible timeline. 'The war happened before the treaty. The treaty happened
before the war.' -> 'a war is said to be before a treaty and also after it'; a consistent timeline (war->treaty->
peace) -> empty audit. This COMPLETES the engine's CONSISTENCY checking across ALL its order/relation domains:
TAXONOMY (inherited is-a negatives, JEP-195/196), QUANTITIES (conflicting numbers, JEP-209), and TEMPORAL (cycles,
JEP-212). A source that contradicts itself in any of these ways is detected and explained — robust learn-from-sources.
79/79 regression tests green (+1). Prediction HIT; tally 101/128. Established (cycle detection in a transitive order);
named; no novelty.
