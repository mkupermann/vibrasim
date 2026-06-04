# JEP-148 — causal / means-ends planning (to achieve an effect, find the action that causes it)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: achieve(goal) returns root-cause ACTIONS whose causal consequences include the goal — achieve(slippery)
  -> [rain, sprinkler] (each -> wetgrass -> slippery). MOST-LIKELY MISS: multi-step / multiple valid actions.

## Acceptance
- PASS: planning battery = 100% (correct actionable causes for a goal effect). Established (means-ends / causal
  planning; Pearl + classical planning), named; no novelty.

## Result — PASS (HIT)
Planning battery 4/4: achieve(slippery) -> [press_button, rain] (actionable ROOT causes; sprinkler excluded because
press_button causes it, so the actionable root is press_button — handles the multi-step chain press_button ->
sprinkler -> wetgrass -> slippery); achieve(wetgrass) -> [press_button, rain]; achieve(rain) -> [] (a root, nothing
causes it); achieve(unknown) -> []. Prediction HIT; tally 43/62; 38 tests gated green. Causal/means-ends planning:
to bring about a goal effect, DO the actionable root cause whose consequences reach it. Completes a coherent CAUSAL
toolkit: inference (141), intervention/do-operator (141), abduction (146), diagnosis (147), planning (148) — Pearl
+ classical AI. Established (means-ends planning), named; no novelty. HONEST: returns root actions reaching the goal
(not optimized action sequences or preconditions/conflicts — a full classical planner tier).
