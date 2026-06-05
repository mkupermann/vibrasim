# JEP-171 — validate the learn-from-prose -> reason -> communicate pipeline (ROBUST + SOUND)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 read() never crashes on adversarial prose (robust, like JEP-125 for the core); relation-interaction invariants
  hold (part-of transitivity/asymmetry, no spurious is-a, the up-then-down leak guard). MOST-LIKELY MISS: a fuzz
  crash from an unanticipated pattern in the newer complex read() handlers (copula/has/located-in).

## Result — PASS (HIT): ROBUST + SOUND
- FUZZ: 6000 adversarial/malformed passages (junk tokens, repeated connectives, control chars, 'a a a...', nested
  'part of part of', etc.) x read() + 5 queries (is-a/part-of/causal/what-causes/describe) -> 0 CRASHES. The
  learn-from-prose pipeline is ROBUST; bad prose is parsed, ignored, or answered cleanly, never an exception.
- SOUNDNESS (property-based): 400 random valid taxonomies x relation-interaction invariants -> 0 VIOLATIONS:
    * a part is part-of every ANCESTOR of its whole (interaction up), and part-of the whole itself;
    * a part is NEVER is_a anything (part is not type);
    * a cause causes every ANCESTOR of its effect (effect-up) and NO non-ancestor (the JEP-170 asymmetry, checked
      both ways);
    * asymmetry holds (whole is not part-of its part; effect does not cause its cause).
So the relation-interaction semantics (JEP-169/170) are PROPERTY-VERIFIED correct, not just example-tested. The new
learn-from-prose + relation-interaction capabilities now match the core engine's validation rigor (JEP-124/125 SOUND/
ROBUST). The hedged 'most-likely fuzz bug' did NOT appear — read() was built with bare-NP/valid-concept guards
throughout. Prediction HIT; tally 63/87. Established (fuzz testing, property-based testing); named; no novelty.
