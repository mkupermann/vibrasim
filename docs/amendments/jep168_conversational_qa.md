# JEP-168 — conversational Q&A over read knowledge: respond() answers part-of + causal questions

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 adding part-of + causal question patterns to respond() lets the engine answer the full multi-relation question
  range over read knowledge, closing the conversational loop. RISK: new patterns interfering with is-a parsing
  (must match 'is X part of Y' before 'is X a Y').

## Result — PASS (HIT)
respond() previously handled is-a questions but MIS-PARSED part-of ('is a heart part of a dog?' -> wrong) and could
not parse causal ('does a virus cause a fever?' -> 'I cannot parse'). Added five question handlers (ordered before
the generic WH/explain fallback): 'is X part of Y?', 'what is part of X?', 'does X cause Y?', 'what causes Y?',
'what does X cause?'. Now, over knowledge learned via read():
- 'is a heart part of a dog?' -> 'Yes. A heart is part of a dog.'  ('is a cell part of a dog?' -> Yes, multi-hop)
- 'is a heart part of a cat?' -> 'No. A heart is not part of a cat as far as I know.'
- 'does a virus cause a fever?' -> 'Yes. A virus causes a fever.'
- 'what causes a fever?' -> 'A virus causes a fever.'  ;  'what does a virus cause?' -> 'A virus causes a fever.'
No interference with is-a parsing (part-of matched before is-a; causal 'does X cause' before universal 'does all').
Also fixed a capitalization bug (.capitalize() flattens the whole string -> 'Yes. a heart...'/'as far as i know';
now sentence-cased properly). This closes the conversational Q&A loop: the engine LEARNS from a passage and CONVERSES
about it across is-a/part-of/causal in English, no transformer. 51/51 regression tests green (+1); wired into the
demo. Prediction HIT; tally 60/84. Established (template NL question parsing); named; no novelty.
