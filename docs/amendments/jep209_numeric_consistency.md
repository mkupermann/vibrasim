# JEP-209 — numeric consistency: detect conflicting quantities (consistency extends to numbers)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 detecting conflicting numbers for the same (entity, attribute) and surfacing them in consistency_audit/summarize
  extends consistency to quantities; consistent numbers don't flag. RISK: restating the same number shouldn't flag.

## Result — PASS (HIT)
read() now records a numeric conflict when 'X has N Y' gives a DIFFERENT N for an (entity, attribute) already known;
consistency_audit() reports these alongside the is-a contradictions (JEP-195/196):
- 'A dog has 4 legs. A dog has 6 legs.' -> audit: 'a dog is said to have both 4 and 6 legs'.
- 'A dog has 4 legs. A dog has 4 legs.' (restated same) -> no conflict (empty audit).
So the engine's CONSISTENCY checking now covers QUANTITIES too: a source that asserts conflicting counts for the same
attribute is flagged (and summarize() surfaces it via the same audit). Completes the quantitative thread's robustness
(JEP-207 extract -> 208 communicate -> 209 consistency). 77/77 regression tests green (+1). Prediction HIT; tally
98/125. Established (consistency checking over numeric attributes); named; no novelty.
