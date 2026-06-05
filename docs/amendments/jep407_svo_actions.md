# JEP-407 — Action facts: SVO ("Michael likes coffee") + "what does X have/verb?" queries

## Motivation
A GUI user naturally states actions: "Michael likes coffee", "Dogs eat meat", "Birds eat worms" — all currently store
NOTHING. And parts are stored ("A dog has a tail" → tail partof dog) but "what does a dog have?" isn't queryable. Add
simple SVO open-relation extraction and the corresponding queries, GUARDED so it captures only clean subject-verb-object
triples (miss > wrong, per JEP-401/402). No transformer.

## Method
- `_normalize_for_learning`: a FALLBACK rule "X <verb> Y" (exactly subject + verb + object after stripping articles;
  verb not a copula/auxiliary is/are/was/were/has/have/can/does/do/will; subject/object single clean words) →
  (singular(X), verb, singular(Y)) open relation. Last resort, so it never overrides is-a/property/causal/etc.
- `BrainQuery.ask`: "what does X <verb>?" / "what do X <verb>?" → forward open-relation (what_did); "what does X have?"
  / "what do X have?" → list things that are part-of X.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: action facts are captured and queryable; no wrong capture on non-SVO sentences; no regression.

- **J407a (SVO + query):** "Michael likes coffee." → "what does Michael like?" → coffee; "Dogs eat meat." → "what do
  dogs eat?" → meat, both seeds (0, 7).
- **J407b (parts query):** "A dog has a tail. A dog has legs." → "what does a dog have?" mentions tail AND leg, both
  seeds.
- **J407c (no wrong capture + no regression):** "A dog is a mammal." → (dog, isa, mammal) NOT an SVO triple; "The sun
  is hot." → still property; is-a multi-hop intact; `pytest -m "not slow" tests/test_conversation.py` passes; both
  seeds.

If the SVO fallback mis-captures a non-action sentence, report it (and tighten the guard). Predicted clean. Bars fixed;
no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (after updating an obsolete test)
- **J407a (SVO + query): PASS** — "Michael likes coffee." → "what does Michael like?" → coffee; "Dogs eat meat." →
  "what do dogs eat?" → meat. Both seeds.
- **J407b (parts query): PASS** — "A dog has a tail. A dog has legs." → "what does a dog have?" → "leg, tail". Both seeds.
- **J407c (no wrong capture + no regression): PASS** — "A dog is a mammal." stays is-a (NOT SVO); "The sun is hot."
  stays property; is-a multi-hop intact; dense-prose junk rate still **0.0** (the exactly-3-word SVO guard doesn't match
  long sentences); `tests/test_conversation.py` **10 passed**. Both seeds.

### Obsolete test updated (honest, like JEP-385)
The SVO rule made "The dog chases the cat" (the teaching test's deliberately-unparseable example since JEP-385) now
parseable — correct. Updated `test_interactive_construction_teaching` to teach a COMPARATIVE construction ("X is faster
than Y", still genuinely unparseable) — same ask→teach→learn→apply flow, verified.

## Verdict: **PASS — natural action statements now teachable**
Simple SVO action facts are captured as open relations and queryable ("what does X like?", "what do X eat?", "what does
X have?"). The SVO rule is a guarded last-resort fallback (exactly subject+verb+object, copulas/auxiliaries excluded),
so it never overrides is-a/property/causal and doesn't mis-capture dense prose (junk still 0.0). Closes a major everyday
GUI-teaching gap — actions, not just taxonomy/attributes. No transformer.
