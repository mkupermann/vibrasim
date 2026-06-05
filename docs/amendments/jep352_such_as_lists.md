# JEP-352 — "such as" lists → is-a extraction (a clean, general encyclopedic form)

## Motivation
"X such as A, B, and C" is one of the most common encyclopedic constructions and is CLEANLY interpretable: A, B, C
are instances of X. Extract is-a facts from it ("Mammals such as dogs and cats" → dog/cat is-a mammal). General, not
overfit to one paragraph. No transformer.

## Method
Normalizer rule: "X(,)? such as A, B(,) and C" → for each instance, add (singular(instance), isa, singular(X)).

## Pre-registered bars (BEFORE the run)
- **J352a:** "Mammals such as dogs and cats are warm-blooded." → is_a(dog,mammal) ∧ is_a(cat,mammal); "Pets such as
  dogs, cats, and birds are common." → dog/cat/bird is_a pet — all true, both seeds (0, 7).
- **J352b (no regression):** JEP-347/348/349/350 + conversation/substrate gates still PASS.

Predicted most-likely failure: the list splitter mis-handles the Oxford comma or trailing words ("and birds are
common" → instance "birds are common"); restrict instances to single nouns and stop at the first non-list token.

## Result (seeds 0, 7): **PASS** (after an Oxford-comma fix)
- **J352a:** "Mammals such as dogs and cats…" → dog/cat is-a mammal; "Pets such as dogs, cats, and birds…" →
  dog/cat/**bird** is-a pet (Oxford comma) = **1.0**, both seeds. **PASS.**
- **J352b:** JEP-347/349/350 + conversation gate still PASS. **PASS.**
- First cut dropped "birds" (non-greedy capture stopped at the first comma); fixed to capture the full list up to
  the predicate. Bar unchanged.

## Verdict: **PASS**
"such as" lists — a common, clean encyclopedic construction — now extract is-a facts (incl. Oxford comma), engine
untouched, no regression. A legitimate general widening of real-prose reading. No transformer.

