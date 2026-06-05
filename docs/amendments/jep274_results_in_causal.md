# JEP-274 — active causal verb 'X results in Y' -> X causes Y

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a causal-connectives QA pass showed 'Cancer results in death' NOT captured (the active causal verbs were
  'causes'/'leads to' only; 'results in' missing) -> broke smoking->cancer->death. Adding 'X results in Y' -> X
  causes Y + excluding it from read_open fixes it; transitive follows.

## Result — PASS (HIT)
Added 'results in' to the active causal-verb alternation ('causes'/'leads to'/'results in') and to read_open's
is_fixed (so it is not redundantly induced as open). Complements the passive 'results from' (JEP-255).
- 'Smoking leads to cancer. Cancer results in death.' -> cancer causes death (results in); 'does smoking cause
  death?' -> Yes (TRANSITIVE smoking->cancer->death). No redundant open 'results in'.
112/112 regression tests green (test added). Prediction HIT; tally 153/189. Established (causal lexical verbs),
named; no novelty. Residue from this pass: 'X reduces Y' (a non-causal relation, 1 occ -> not induced); conditionals
'if X then Y' (the genre wall). Article residue 'a death' (mass-noun-as-object, the usage-countability limit).
