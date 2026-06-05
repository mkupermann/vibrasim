# JEP-210 — temporal-order reasoning from prose ('X before/after Y')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a 'X (is/was/happened) before/after Y' pattern routed to the order relation lets the engine answer transitive
  temporal questions ('did the war start before the peace?' via war->treaty->peace). RISK: before/after inverse.

## Result — PASS (HIT)
Added temporal-order extraction + Q&A, reusing the order-relation machinery (_orders/_order_holds, as comparison does):
- read() detects 'X (verb) before/after Y' -> the 'before' order relation; 'after' is stored as the INVERSE
  ('X after Y' == 'Y before X'). 'The war started before the treaty. The treaty came before the peace. The famine
  happened after the war.' -> 3 temporal facts.
- respond() answers 'did/was/is X (verb) before/after Y?': 'did the war happen before the peace?' -> 'Yes.' (TRANSITIVE
  war->treaty->peace); reverse -> 'Not that I can tell.'; 'is the famine after the war?' -> 'Yes.' (inverse); 'is the
  war after the famine?' -> 'Not that I can tell.'
So the engine now does TEMPORAL SEQUENCING from prose — ordering events and answering before/after questions with
transitive closure, a genuinely-distinct domain (narratives/history) that reuses the existing transitive-order
inference. HONEST LIMIT: relative order only ('before/after'); absolute dates/durations/arithmetic are out of scope.
77/77 regression tests green (+1). Prediction HIT; tally 99/126. Established (transitive temporal order / Allen-style
before relation, simplest form); named; no novelty.
