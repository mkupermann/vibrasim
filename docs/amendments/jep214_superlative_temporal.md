# JEP-214 — superlative temporal queries ('what happened first/last?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'what happened first?' returns the event with nothing before it (a source in the before-order), 'last' the sink.
  RISK: ambiguity with a partial order (multiple sources).

## Result — PASS (HIT)
Added a superlative-temporal handler: 'what happened first?' -> the event with no predecessor in the before-order
('first'); 'what happened last?' -> the event with no successor ('last'); if multiple candidates (partial order) it
honestly reports 'Possibly ... (the order is not fully determined)'. On a linear timeline famine->war->treaty->peace:
'what happened first?' -> 'A famine happened first.'; 'what happened last?' -> 'A peace happened last.' Extends the
temporal domain (JEP-210) from yes/no before/after questions to superlative ordering. 82/82 regression tests green
(+1). Prediction HIT; tally 103/130. Established (source/sink of a transitive order); named; no novelty.
