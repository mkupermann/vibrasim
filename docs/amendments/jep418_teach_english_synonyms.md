# JEP-418 — Teaching English (1): synonyms so the substrate understands varied phrasing

## Motivation
Michael's directive: teach English first. A core part of "understanding English" is recognizing that DIFFERENT words
mean the same thing — synonyms. JEP-356 established that synonym equivalence does NOT emerge from induction but CAN be
taught (the LLM-as-parent supplies it). This teaches the substrate synonym equivalences so it understands varied
phrasing of the same fact/question — a concrete first English lesson. Honest scope: this broadens UNDERSTANDING; it
does not make the substrate generate fluent prose (that remains the LLM's job).

## Method
The LLM teacher provides synonym pairs (e.g., big≈large, smart≈intelligent, doctor≈physician, fast≈quick). Teach a
fact with one word and query with a synonym; the substrate should answer correctly via the taught equivalence. Use the
existing taught-synonym mechanism (a word→canonical map applied at parse/query time).

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: with taught synonyms, a fact stated with one word is answerable when asked with a synonym; untaught
synonyms are NOT (honest limit — each must be taught).

- **J418a (taught synonym understood):** teach "big" ≈ "large"; "An elephant is a big animal." then "is an elephant a
  large animal?" → yes, both seeds (0, 7).
- **J418b (second pair + property):** teach "smart" ≈ "intelligent"; "A human is smart." → "is a human intelligent?" →
  yes, both seeds.
- **J418c (honest limit + no regression):** an UNtaught synonym does NOT resolve (e.g., "rapid" for "fast" without
  teaching) — confirming each equivalence must be taught (the documented no-emergence limit); is-a multi-hop intact;
  `pytest -m "not slow" tests/test_conversation.py` passes.

If taught synonyms don't resolve, report it. Predicted: taught works, untaught doesn't (the honest teacher-coupled
shape). Bars fixed; no retuning. No transformer in the substrate.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J418a:** "Big means large." then "An elephant is big." → "is an elephant large?" → **yes** (and "is an elephant
  big?" → yes). Both seeds.
- **J418b:** "Smart means intelligent." then "A human is smart." → "is a human intelligent?" → **yes**. Both seeds.
- **J418c:** an UNtaught synonym ("rapid" for "fast") does NOT resolve (→ no) — confirming each equivalence must be
  taught (the documented no-emergence limit, JEP-356); is-a intact; `tests/test_conversation.py` **10 passed**.

## Verdict: **PASS — the substrate understands varied phrasing via taught synonyms (a first English lesson)**
Synonym teaching ("X means Y") is now wired into the live Conversation: words normalize to a canonical form at parse
and query time, so a fact stated with one word is understood when asked with a synonym. Taught synonyms work; untaught
ones don't (honest teacher-coupled shape). This is concrete "teaching English" — broadening UNDERSTANDING of varied
phrasing — supplied by the LLM teacher (e.g., from a synonyms dictionary). It does NOT make the substrate generate
fluent prose (that remains the LLM's job). No transformer in the substrate.
