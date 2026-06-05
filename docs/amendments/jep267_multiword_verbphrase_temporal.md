# JEP-267 — multi-word verb phrase in temporal order ('the treaty was signed before the peace')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 history QA showed 'The treaty was signed before the peace' NOT captured (the temporal pattern allowed only ONE
  optional word before 'before/after', but 'was signed' is TWO) -> broke the transitive war->treaty->peace chain.
  Relaxing the verb-phrase to (?:\w+\s+)* (zero or more words) captures it; transitive order follows.

## Result — PASS (HIT)
The temporal pattern `^{np}\s+(?:\w+\s+)?(before|after)\s+{np}$` allowed only ONE word between subject and
before/after ('started before' OK, 'was signed before' NOT). Relaxed to `(?:\w+\s+)*` (a multi-word verb phrase).
- 'The war started before the treaty. The treaty was signed before the peace.' -> war->treaty, treaty->peace (was
  dropped before). 'did the war happen before the peace?' -> Yes (TRANSITIVE war->treaty->peace). Reverse -> No.
- 'The Renaissance came before the Enlightenment.' -> captured. No regression (106/106 tests green; +1 added = 107).
Prediction HIT; tally 146/182. Established (temporal order extraction, verb-phrase tolerance), named; no novelty.
Honest residue from the history pass (the NER/multi-word-entity wall): multi-word named entities ('World War 2',
'World War 1') in temporal questions; the superlative-order enumeration over those is messy. Bounded by no-NER.
