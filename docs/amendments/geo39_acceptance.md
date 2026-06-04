# GEO-39 — Final acceptance test of the hardened GroundedQA system (end-to-end, dogfoods the module)

## Motivation
After hardening (focus-verification GEO-33, faithfulness GEO-38, strong context prompt GEO-34), run the
SHIPPED GroundedQA module end-to-end on one coherent scenario exercising every capability together. This is
the acceptance/regression test for the deliverable: does the whole system work as one?

## Pre-registration (locked BEFORE run)
- Mini company KB via GroundedQA (generate=True): employees (team) + teams (city), with focus index = names.
- Checks (each PASS/FAIL):
  1. SEMANTIC answer (grounded) for an in-KB question -> correct & grounded.
  2. MULTI-HOP grounded generation (person -> team -> city) -> correct city in answer.
  3. ABSTAIN on out-of-KB question (focus absent) -> "I don't know".
  4. FAITHFUL: question asking for an absent detail (salary) -> does NOT invent a number.
  5. UPDATABLE: edit a team's city, re-query -> answer reflects the edit.
- Bar: >= 4 of 5 checks PASS (the hardened system works end-to-end). Report each.
