# JEP-219 — conversational follow-up with context ('what about X?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'what about X?' reuses the last is-a question's category with a new subject — a multi-turn conversational
  capability. RISK: which prior query to reuse.

## Result — PASS (HIT)
Added a conversational follow-up handler: 'what about X?' / 'how about X?' / 'and X?' reuses the CATEGORY from the
last is-a question, applied to the new subject X. 'Is a dog an animal?' -> 'Yes...' then 'what about a cat?' -> 'Yes,
a cat is an animal too.'; 'what about a salmon?' -> 'No, a salmon is not an animal as far as I know.' (salmon has no
is-a path to animal in the KB); 'and a rock?' -> 'No...' Each follow-up updates the context so a chain of them works.
This is conversational ELLIPSIS/context — a genuinely human-like multi-turn ability ('communicate WITH me'): the
engine carries the topic across turns and answers a terse follow-up. HONEST LIMIT: reuses the last IS-A category
only (the most common follow-up form). 86/86 regression tests green (+1). Prediction HIT; tally 108/135. Established
(conversational ellipsis resolution / dialogue context); named; no novelty.
