# JEP-345 — Conversational robustness on messier real phrasings

## Motivation
Talking feels human only if it tolerates messy input. Handle: filler/politeness ("so", "um", "please"), negated
question forms ("isn't a poodle a dog?"), plural subjects ("do poodles bark?"), multi-sentence turns that MIX teach
and ask ("A poodle is a dog. Is it a mammal?"), and "what about X?" follow-ups (re-ask the last question with a new
subject). No transformer.

## Method
`Conversation`: `_preprocess` strips leading filler and normalizes negated auxiliaries (isn't→is, doesn't→does);
`say` splits a turn into sentences and processes EACH (teach or answer), combining replies; tracks the last
question template for "what about X?"; `BrainQuery` falls back to the singular when a plural subject isn't found.

## Pre-registered bars (BEFORE the run)
- **J345a (messy phrasings):** a battery — "isn't a poodle a dog?", "do poodles bark?", "so, is a poodle an
  animal?", a mixed multi-sentence turn "A poodle is a dog. Is it a mammal?", and "what about a cat?" after "is a
  dog a mammal?" — answered correctly ≥ 0.90, both seeds (0, 7).
- **J345b (no regression):** JEP-340/342/344 still PASS; substrate gate green.

Predicted most-likely failure: the multi-sentence split mis-routes a clause (a teach treated as a question), or
"what about X" binds to a stale template. If J345a misses, report the clause and its routing.

## Result (seeds 0, 7): **PASS**
- **J345a:** messy-phrasing battery = **1.0** — "isn't a poodle a dog?" (negation→base), "do poodles bark?"
  (plural→singular), "so, is a poodle an animal?" (filler strip, fixed to handle "so,"), mixed turn "A beagle is a
  dog. Is it a mammal?" (split → learn + answer), "what about a cat?" (re-ask last template with new subject), both
  seeds. **PASS.**
- **J345b:** JEP-340/342/344 still PASS. **PASS.**

## Verdict: **PASS**
The conversation tolerates messier real input — filler/politeness, negated/contracted auxiliaries, plural subjects,
multi-sentence turns mixing teaching and asking, and "what about X?" follow-ups. Honest: first cut 4/5 — the filler
stripper matched "so " but not "so," (comma); fixed with a word-boundary regex, bar unchanged. Makes talking feel
less templated. No transformer.

