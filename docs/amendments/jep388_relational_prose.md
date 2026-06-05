# JEP-388 — Relational prose: queryable part-of + causal variants (plural/modal/"a part of")

## Motivation
The relational-prose diagnostic found gaps beyond taxonomy:
1. **Query gap (worst case):** "A wheel is part of a car" stores (wheel, partof, car) correctly, but "is a wheel part
   of a car?" returns "I don't know" — the `ask()` parser has no "is X part of Y" rule, so stored part-of knowledge is
   UNREACHABLE.
2. **Causal parse gaps:** "Viruses cause disease" (plural "cause") and "Smoking can cause cancer" (modal) → no facts.
3. **Part-of parse gap:** "The engine is a part of the car" ("is a part of") → no fact.
Fix the query rule and the parse variants so relational prose (not just is-a) becomes reliable knowledge. No transformer.

## Method
- `BrainQuery.ask`: add "is X part of Y" → `part_of(X, Y)`.
- `_normalize_for_learning`: a causal rule handling singular/plural/modal ("X causes/cause/can cause Y" →
  (X, causes, Y) + (Y, caused_by, X)); and rewrite "is a part of" → "is part of".

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: stored part-of becomes queryable; causal variants and "is a part of" parse; no regression.

- **J388a (part-of queryable):** after "A wheel is part of a car", `say("is a wheel part of a car?")` → yes, and
  `say("is a wheel part of a tree?")` → no, both seeds (0, 7).
- **J388b (causal variants):** "Viruses cause disease" → (virus, causes, disease); "Smoking can cause cancer" →
  (smoking, causes, cancer); "Smoking causes cancer" still works; `say("what causes disease?")` → virus, both seeds.
- **J388c (part-of variant + no regression):** "The engine is a part of the car" → (engine, partof, car); existing
  part-of forms ("A car has wheels" → wheel partof car) still work; `pytest -m "not slow" tests/test_conversation.py`
  passes.

If a new rule mis-fires (e.g. "part" treated as a class), report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (after fixing a repeat of the non-greedy `_singular` bug)
First run: J388a/J388c PASS, J388b FAILED — "Viruses cause disease" stored ("viruse", causes, disease): the SAME
non-greedy `([A-Za-z]+?)s?` capture bug from JEP-385 (captures "viruse", strips the "s" itself, so `_singular` can't
recover "virus"). Fixed by capturing the full word `([A-Za-z]+)` and letting `_singular` handle the plural
("viruses"→"virus"). (Lesson logged: never pair non-greedy `+?` with a trailing `s?` capture — let `_singular` do it.)

Final result:
- **J388a (part-of queryable): PASS** — "is a wheel part of a car?" → yes; "is a wheel part of a tree?" → no. The
  stored part-of knowledge is now reachable. Both seeds.
- **J388b (causal variants): PASS** — "Viruses cause disease" → (virus, causes, disease); "Smoking can cause cancer"
  → (smoking, causes, cancer); "Smoking causes cancer" still works; "what causes disease?" → virus. Both seeds.
- **J388c ('is a part of' + no regression): PASS** — "The engine is a part of the car" → (engine, partof, car);
  "A car has wheels" → wheel partof car; `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — relational prose beyond taxonomy is now reliable**
Two relational gaps closed: stored part-of knowledge is now QUERYABLE ("is X part of Y?" → part_of), and causal prose
parses in singular/plural/modal forms (and "is a part of"), all queryable via "what causes X?". The worst gap (knowledge
stored but unreachable) is fixed. This extends reliable capture from pure taxonomy to part-whole and causal
relationships — more of a real article's *relationships* become answerable. The repeated non-greedy/`s?` bug was caught
and fixed without touching the bars. Established rule-based normalization; no transformer.
