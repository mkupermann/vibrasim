# JEP-282 — subordinate causal connectives 'X because of Y' / 'X due to Y' -> Y causes X

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a causal-connectives QA pass showed 'Flooding happens because of rain' / 'Disease spreads due to bacteria'
  induced as generic OPEN relations, not causal. These are causal with the EFFECT as subject -> add 'X <verb>
  because of/due to Y' -> Y causes X (the swap, like passive 'is caused by') + exclude from open.

## Result — PASS (HIT)
Added 'X <verb phrase> because of Y' / 'X <verb phrase> due to Y' to the passive/subordinate causal handler ->
tell_cause(Y, X) (Y is the cause, X the effect), and excluded 'because of'/'due to' from read_open's is_fixed.
- 'Flooding happens because of rain.' -> rain causes flooding; 'Disease spreads due to bacteria.' -> bacteria causes
  disease; 'Rain leads to flooding.' (active) -> rain causes flooding. 'does rain cause flooding?' -> Yes; 'does
  bacteria cause disease?' -> Yes. Directional (not symmetric). Active causal + is-a unaffected.
119/119 regression tests green (test added). Prediction HIT; tally 161/197. This completes comprehensive CAUSAL
CONNECTIVE coverage: ACTIVE (causes / leads to / results in), PASSIVE (is caused by / results from), SUBORDINATE
(because of / due to). Established (causal connectives, passive-voice swap), named; no novelty. Residue: 'a flooding'/
'a bacteria' (mass/abstract-noun-as-object article long tail) -- answer correct, only the article.
