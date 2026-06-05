# JEP-230 — mass-noun article heuristic ('gravity', '-ness' abstracts) with countable exceptions

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a '-ness' suffix is a reliably-uncountable abstract marker; adding it as a morphological rule (plus a few
  physics mass nouns) fixes 'a gravity'/'a kindness' without breaking countable nouns. RISK: '-ity'/'-tion' are
  NOT safe (countable), so restrict to '-ness'.

## Result — PASS, with a CALIBRATION (predicted risk under-stated)
Closed the JEP-228 residue 'a gravity'. Added clearly-uncountable physics/abstract mass nouns to _MASS_NOUNS
(gravity, friction, electricity, momentum, radiation, steam, smoke, dust, air, heat, sunlight, magnetism, humidity)
AND a morphological '-ness' rule in _art.

CALIBRATION (the predicted risk was real AND bigger than I scoped it): '-ness' is NOT *reliably* uncountable.
The first cut wrongly made 'business' -> 'business' and 'witness' -> 'witness' (both COUNTABLE: 'a business',
'a witness'; also 'an illness', 'a likeness', 'a wilderness', 'a harness'). Fix: a _COUNTABLE_NESS exception set.
I also initially mis-listed 'fairness' as countable (it is uncountable) and corrected it. Lesson: a morphological
suffix rule needs its exception set enumerated and TESTED against counter-examples in the same rung, not assumed.

Final: mass abstracts/physics + true '-ness' abstracts (kindness, darkness, happiness) -> no article; countable
'-ness' (business/witness/illness) + ordinary nouns (city/entity/function/dog) -> a/an. All correct.
93/93 -> 94/94 regression tests green (+1). PASS but logged as a calibration (risk under-scoped); tally 117/145
(this rung does not add a clean HIT — the prediction's 'reliably uncountable' claim was falsified mid-rung and fixed).
Established (English count/mass article agreement, suffix heuristic + exception list); named; no novelty.
