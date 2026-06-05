# JEP-414 — Singular copular is-a with a modified noun ("The cheetah is a large cat")

## Motivation
The JEP-413 junk guard (reject multi-word entities) exposed a gap: "The cheetah is a large cat" produced a multi-word
value "large cat" that the guard rejected, so the cheetah→cat→...→animal chain was lost ("is a cheetah an animal?" →
No). Factual reference prose is full of adjective-modified classes. Fix: extract the HEAD noun ("cat") before storing,
so the value is single-word and survives the guard. No transformer.

## Method
Add a singular copular is-a rule: "(The) X is a/an <modifiers> <head> [that/of …]" → (X, isa, head), stripping a
relative/prepositional tail and taking the last word of the noun phrase as the head.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J414a (modified-noun is-a):** "The cheetah is a large cat." → "is a cheetah a cat?" yes AND (with "A cat is a
  mammal. Mammals are animals.") "is a cheetah an animal?" → yes, both seeds (0, 7).
- **J414b (prepositional head):** "An eagle is a bird of prey." → "is an eagle a bird?" → yes (head "bird", not
  "prey"), both seeds.
- **J414c (no regression):** "A dog is a mammal." → "is a dog a mammal?" yes; attribute/SVO unaffected; `pytest -m
  "not slow" tests/test_conversation.py` passes.

If head extraction mis-fires (wrong head), report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result: **PASS** (both seeds)
- **J414a:** "The cheetah is a large cat." → (cheetah, isa, cat); "is a cheetah a cat?" yes, "is a cheetah an animal?"
  yes (multi-hop restored).
- **J414b:** "An eagle is a bird of prey." → (eagle, isa, bird); "is an eagle a bird?" / "is an eagle an animal?" yes.
- **J414c:** is-a/attribute/SVO intact; `tests/test_conversation.py` **10 passed**.

## Verdict: **PASS — factual prose with modified-noun classes parses again**
Extracting the head noun before the junk guard restores the legitimate is-a facts that adjective/prepositional modifiers
would otherwise turn into rejected multi-word values — so "The cheetah is a large cat" correctly yields cheetah→cat and
the full multi-hop chain. This recovers factual-reference coverage the JEP-413 guard had inadvertently dropped, while
keeping "never wrong capture". No transformer.