# JEP-410 — Yes/no verification questions for actions, causes, locations

## Motivation
The teaching side is broad, but asking yes/no about taught facts has gaps: "does Michael like coffee?", "is Paris in
France?", "does smoking cause cancer?" all return "I don't know" though the facts are stored. A GUI user naturally
verifies facts this way. Add verification queries that check the stored open/causal/locational relations. No transformer.

## Method
`BrainQuery.ask`:
- "does X <verb> Y?" → Y ∈ what_did(X, verb) (covers actions and causes), EXCEPT verb=="have" (kept on the existing
  part-of/count rule).
- "is X in Y?" → stored located_in(X) == Y.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J410a (action verify):** "Michael likes coffee." → "does Michael like coffee?" → yes; "does Michael like tea?" →
  no, both seeds (0, 7).
- **J410b (location verify):** "Paris is in France." → "is Paris in France?" → yes; "is Paris in Spain?" → no, both
  seeds.
- **J410c (cause verify + no regression):** "Smoking causes cancer." → "does smoking cause cancer?" → yes; "does a dog
  have a tail?" still yes (have rule intact); `pytest -m "not slow" tests/test_conversation.py` passes; both seeds.

If the new rule shadows the "have" rule or mis-verifies, report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (after a verb-stem fix)
- **J410a (action verify): PASS** — "does Michael like coffee?" → yes; "does Michael like tea?" → no. (First run gave
  "No" for coffee: `what_did`'s 5-char stem makes "like"!="likes"; fixed by trying verb variants like→likes, as `what()`
  does.) Both seeds.
- **J410b (location verify): PASS** — "is Paris in France?" → yes; "is Paris in Spain?" → no. Both seeds.
- **J410c (cause + no regression): PASS** — "does smoking cause cancer?" → yes; "does a dog have a tail?" still yes
  (have rule intact); `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — users can verify any taught fact yes/no**
"does X <verb> Y?" (actions and causes, with verb-variant matching), "is X in Y?" (locations) now verify against the
stored relations, complementing the existing is-a/property/part-of verification. The part-of "have" rule is preserved.
A GUI user can now confirm facts they taught, not just ask open questions. No transformer.
