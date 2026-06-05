# JEP-394 — "is X <property>?" should check has_property, not only is_a

## Motivation
JEP-393 surfaced a parser gap: "is a dog warm-blooded?" routes to `is_a(dog, warm-blooded)` (→ False) instead of
`has_property`, even though the property is correctly stored. The "is X Y?" question is ambiguous between class
membership and property; it should answer yes if EITHER holds. Fix: "is X Y?" → `is_a(X,Y) or has_property(X,Y)`.
No transformer.

## Method
In `BrainQuery.ask`, change the generic "is X Y" rule to return `is_a(x, y) or has_property(x, y)`.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: property questions now answer correctly; is-a and negatives unaffected.

- **J394a (property + is-a both work):** after "A dog is a mammal. Mammals are animals that are warm-blooded." →
  "is a dog warm-blooded?" → yes; "is a poodle a dog?" → yes (is-a intact); "is a whale a fish?" → no (negative intact);
  "is a dog purple?" → no (no false-positive), both seeds (0, 7).
- **J394b (JEP-393 Q&A → 1.0):** re-running JEP-393, Q&A accuracy = 1.0 (the warm-blooded miss closed), both seeds.
- **J394c (no regression):** `pytest -m "not slow" tests/test_conversation.py` passes.

If `or has_property` causes a false-positive on a negative, report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (after the first run exposed a deeper hyphen-tokenization bug)
First run still failed (prop=False): the `is_a or has_property` routing was correct, but "warm-blooded" has a HYPHEN
and the parser token `(\w+)` doesn't match hyphens, so the question never parsed. Fixed by allowing hyphens in the
class/property token (`[\w-]+`). (Honest: two layered bugs — routing AND tokenization — the integration test caught the
symptom, the fix needed both.)

Final result:
- **J394a (property + is-a + neg + no-fp): PASS** — "is a dog warm-blooded?" → yes (via inherited has_property);
  "is a poodle a dog?" → yes (is-a intact); "is a whale a fish?" → no (negative intact); "is a dog purple?" → no (no
  false-positive). Both seeds.
- **J394b (JEP-393 Q&A → 1.0): PASS** — re-running the integration capstone, Q&A = **1.0** (the warm-blooded miss
  closed). Both seeds.
- **J394c (no regression): PASS** — `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — property questions answered; integration Q&A now perfect**
"is X Y?" now answers yes when X is-a Y OR X has property Y, and the parser accepts hyphenated terms ("warm-blooded"),
so property questions work without disturbing is-a or negatives. This closes the minor gap JEP-393 surfaced and lifts
the integration-capstone Q&A to 1.0 — confirming the test did its job (an isolated capability that failed only in
composition, now fixed). Established rule-based query routing; no transformer.
