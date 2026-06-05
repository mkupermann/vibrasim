# JEP-453 — Fix the "penguin can fly" confident falsehood (ability negation)

## Motivation
The JEP-452 integration audit caught a confident falsehood: "can a penguin fly?" → "Yes". Root cause:
"X can VERB" was effectively stored as `(X, hasprop, VERB)`, but "X cannot VERB" fell through to the
SVO fallback and was stored as `(X, cannot, VERB)` — a bogus relation the defeasible-exception
machinery (`not_hasprop` overrides `hasprop`) never sees. So the penguin inherited "bird hasprop fly".

## Fix (`world/conversation.py`)
Add an ability-as-property rule before the SVO fallback: "X can VERB" → `(X, hasprop, VERB)`;
"X cannot / can't / can not VERB" → `(X, not_hasprop, VERB)`. Same relation for both polarities, so a
specific negation overrides an inherited ability. Excludes "X can cause Y" (causal, handled earlier).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J453a:** "Birds can fly" + "a penguin is a bird" + "a penguin cannot fly" → "can a penguin fly?"
  → No; "can an eagle fly?" (bird, no exception) → Yes; "can a bird fly?" → Yes. Both seeds.
- **J453b:** the JEP-452 audit now passes 12/12 with zero confident falsehoods, both seeds.
- **J453c:** `tests/test_substrate_memory.py` + `tests/test_conversation.py` stay green.

## RESULT (2026-06-05): **PASS**
- J453a ✓ — penguin → No, eagle → Yes, bird → Yes; stored facts `(bird,hasprop,fly)`,
  `(penguin,not_hasprop,fly)`.
- J453b ✓ — JEP-452 re-run: **12/12, falsehoods=[]**, both seeds.
- J453c ✓ — 24/24 green.

The integration audit (JEP-452) did exactly its job: surfaced a latent reasoning falsehood hiding
under the new affect work; JEP-453 fixed it. Defeasible ability now behaves like defeasible
properties. Established rule-based normalization, named; no new science. No transformer.