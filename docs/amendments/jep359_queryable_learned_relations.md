# JEP-359 — Queryable learned relations: ask about facts from taught constructions (forward + reverse)

## Motivation
JEP-358 stores facts from taught constructions (e.g. (farmers, domesticated, cat)), but the demo showed "who
domesticated the cat?" wasn't answerable. Close the loop: add open-relation question forms — reverse "who VERB the
Y?" (find the subject) and forward "what did X VERB?" (find the object) — over any stored relation, with stem-based
verb matching (domesticate↔domesticated). No transformer.

## Method
`BrainQuery`: `who_did(verb, obj)` = subjects s of stored (s, ~verb, obj); `what_did(subj, verb)` = objects.
Stem-match the verb (first 5 chars) so morphology varies. Parser templates: "who VERB (the) Y", "what was Y VERB
by", "what did X VERB".

## Pre-registered bars (BEFORE the run)
- **J359a (reverse + forward):** with (farmers, domesticated, cat) and (humans, domesticated, dog) in the store —
  "who domesticated the cat?" → farmers; "what did humans domesticate?" → dog; "what was the cat domesticated by?"
  → farmers — all correct, both seeds (0, 7).
- **J359b (end-to-end via teaching):** teach the construction interactively (JEP-358), then the reverse/forward
  questions answer correctly, both seeds.
- **J359c (no regression):** conversation gate + BrainQuery (JEP-322) still PASS.

Predicted most-likely failure: stem-matching collides two different verbs sharing 5 chars; rare in a small taught
store — if J359a returns a wrong subject, report the collision and tighten to full-stem.

## Result (seeds 0, 7): **PASS**
- **J359a:** reverse "who domesticated the cat?" → ["farmers"]; forward "what did humans domesticate?" → ["dog"];
  passive "what was the cat domesticated by?" → ["farmers"] = **1.0**, both seeds. **PASS.**
- **J359b:** end-to-end — teach the "X was domesticated by Y" construction interactively (JEP-358), then "who
  domesticated the cat?" → farmers, both seeds. **PASS.**
- **J359c:** conversation gate + JEP-322 still PASS. **PASS.**

## Verdict: **PASS**
The learn→store→ask loop closes: a relation taught via construction induction (JEP-357/358) is now fully queryable
in both directions — reverse "who VERB the Y?", forward "what did X VERB?", passive "what was Y VERB by?" — with
stem-based verb matching (domesticate↔domesticated). So you can teach the brain a new sentence form by example and
then ask about the facts it read with that form. Closes the gap the JEP-358 demo surfaced. No transformer.

