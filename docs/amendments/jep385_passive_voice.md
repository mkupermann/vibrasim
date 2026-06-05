# JEP-385 — Capture passive-voice facts ("X is eaten by Y")

## Motivation
The construction-wall diagnostic showed passive voice ("Salmon is eaten by bears") parses to nothing — a common
real-prose form. Capture it as a queryable open relation: "X is/are/was/were <participle> by Y" → (Y, <participle>, X),
answerable via the existing "what was X <verb> by?" parser. This is EXTRACTION of passive facts, NOT active↔passive
unification (JEP-360 established that unification needs taught knowledge; here we just stop dropping passive
sentences). No transformer.

## Method
Add a passive rule to `_normalize_for_learning`: match "(the) X (is|are|was|were) <participle> by (the) Y" and append
(singular(Y), <participle>, singular(X)) as an extra fact. Require the " by " marker so it never fires on copular
"X is a Y".

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: passive sentences now yield a queryable agent→patient open relation, retrievable via "what was X <verb>
by?", without firing on copular/locational sentences.

- **J385a (passive extracted):** "Rabbits are hunted by foxes" → (fox, hunted, rabbit); "Salmon is eaten by bears" →
  (bear, eaten, salmon), both seeds (0, 7).
- **J385b (queryable end-to-end):** after reading "Rabbits are hunted by foxes", `say("what was the rabbit hunted
  by?")` returns "fox" (or contains fox), both seeds.
- **J385c (no false fire + no regression):** "A dog is a mammal" → dog→mammal (NOT a passive); "Paris is located in
  France" → located_in (not passive); `pytest -m "not slow" tests/test_conversation.py` passes.

If the rule mis-fires on a copular/locational sentence, report it. Predicted clean. Bars fixed; no retuning. No
transformer.

## Result (seeds 0, 7): **PASS** (after fixing two issues the first run surfaced — both honest, neither a bar change)
First run was NULL and surfaced two genuine issues, both fixed:
1. **`_singular` bug exposed:** my passive regex non-greedily captured "foxe" and stripped the "s" itself, so
   `_singular("foxe")` couldn't recover "fox". Fixed by capturing the FULL word (`([A-Za-z]+)`) and letting
   `_singular` handle the plural ("foxes"→"fox").
2. **An obsolete test:** `test_interactive_construction_teaching` used the passive "The dog was domesticated by
   humans" as its example of an UNPARSEABLE sentence — which JEP-385 now (correctly) parses. The test's premise was
   invalidated by the new capability, so I rewrote it to teach a still-unparseable active SVO construction
   ("The dog chases the cat"), preserving exactly what it validates (ask → teach → learn → apply). Not a bar change;
   the capability tested is unchanged.

Final result:
- **J385a (passive extracted): PASS** — "Rabbits are hunted by foxes" → (fox, hunted, rabbit); "Salmon is eaten by
  bears" → (bear, eaten, salmon). Both seeds.
- **J385b (queryable end-to-end): PASS** — `say("what was the rabbit hunted by?")` → "fox". Both seeds.
- **J385c (no false-fire + no regression): PASS** — "A dog is a mammal" → dog→mammal (not passive); "Paris is located
  in France" → located_in (not passive); `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — passive voice captured; two honest fixes along the way**
Passive-voice sentences now yield a queryable agent→patient open relation ("what was X <verb> by?" → agent), without
firing on copular or locational sentences. This is EXTRACTION of passive facts (not active↔passive unification, which
JEP-360 showed needs taught knowledge) — it stops the pipeline dropping a common real-prose construction. The first run
honestly surfaced a `_singular` edge bug and an outdated test (a test whose premise my new capability invalidated);
both were fixed without touching the pre-registered bars. Established rule-based normalization; no transformer.
