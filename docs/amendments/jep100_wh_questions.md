# JEP-100 — conversational WH-questions ("what is X?", "what does X do?")

## Why
Advance COMMUNICATION toward dialogue: answer WH-questions, not just yes/no. "what is a poodle?" -> "A poodle is a
dog."; "what does the dog chase?" -> "The dog chases the cat." (object retrieval from stored facts).

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%. MOST-LIKELY MISS: verb-form mismatch between stored fact ("chases") and query verb ("chase") in the
  object lookup; mitigated by normalizing both via _norm_rel.

## Result — MISS then fixed (HONEST: wrong-location prediction again)
Initial 5/6. The verb agreement I predicted WORKED. The actual miss: "what is a unicorn?" -> "an unicorn" — the
a/an article rule is LETTER-based, but 'unicorn' has a consonant SOUND (/juː/) so it takes 'a'. The a/an class has
now surfaced in THREE sub-forms across the engine: alternation order (JEP-92), generation (JEP-95), and now
PHONETICS (JEP-100). A letter rule cannot capture a/an; full correctness needs a pronunciation dictionary. FIX
(standard pragmatic partial): letter rule + an exception set (a unicorn/university/European...; an hour/honest/
heir...). After fix: 6/6 = 100%, suite 11/11, tiers 95/96 still 100% (gated). CALIBRATION: MISS (predicted wrong
location); tally 7/12. LESSON: a/an is phonetic not orthographic — a known hard sub-case; the exception-list is a
documented PARTIAL, not full coverage. Established (template generation, a/an heuristic+exceptions), named; no novelty.
