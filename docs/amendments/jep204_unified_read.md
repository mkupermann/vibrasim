# JEP-204 — unify read() to learn BOTH fixed and open relations in one call

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 having read() also run open-relation induction (after fixed extraction, same passage) makes one call learn both,
  no interference (read_open excludes fixed connectives). RISK: double-counting or a fixed sentence mis-inducing.

## Result — PASS (HIT)
read() now calls read_open() on the same passage after its fixed-relation extraction and merges the result under an
'open' key. A single read() call:
  read('A dog is a mammal. A mammal is an animal. Paris is the capital of France. London is the capital of England.
        A heart is part of a dog.')
-> {'is_a': 4, 'part_of': 1, 'causal': 0, 'open': {'is capital of': 2}} — fixed relations (is-a, part-of) AND the
auto-induced open relation, all from ONE call. is_a(dog,animal), part_of(heart,dog), and relation_true(paris,'is
capital of',france) all True. No interference (read_open's is_fixed excludes is-a/part-of/causal/spatial/comparison
connectives, so fixed sentences are not mis-induced as open) and no double-counting. 72/72 regression tests green
(the existing read() tests pass unchanged — the 'open' key is additive). The reading pipeline is now UNIFIED: a
single read() learns the full relational structure (5 fixed types + any recurring open relations) from a passage.
Prediction HIT; tally 93/120. Established (pipeline composition); named; no novelty.
