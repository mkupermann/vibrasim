# JEP-228 — real-usage QA on a natural encyclopedic passage surfaces (and fixes) two genuine bugs

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine handles a realistic natural encyclopedic passage at high accuracy; any surfaced issue is a genuine
  real-prose handling bug worth fixing (the real-usage QA mode finds real issues). RISK: natural phrasings the
  patterns don't cover (recall dips, not crashes).

## Result — PASS (HIT). Two genuine bugs surfaced and fixed; no crash.
Ran a Simple-Wikipedia-register passage (Sun/Earth/Moon/planets/states-of-matter) NOT constructed for the engine.
Core extraction + multi-hop + superlatives + temporal all worked. The QA surfaced TWO genuine real-prose bugs:

1. **Multi-word is-a PARENT leaked into open relations.** 'A star is a celestial body' was correctly captured as
   is-a (parent = 'celestial body'), but read_open ALSO induced a spurious open relation 'is celestial' (recurring
   2x across Sun and Earth), because is_fixed only excluded the bare 'is'. FIX: is_fixed now treats any copula form
   ('is', 'is celestial', 'are warm-blooded') as IS-A — UNLESS a relational preposition (of/in/at/by/to/on/with/from)
   makes it a genuine OPEN relation. This excludes adjective-copula parents while KEEPING 'is capital of',
   'is located in', etc. (verified: 'is capital of' still induces at 2+ instances -> 'Paris.'; scale test 8/8).

2. **Numeric Q&A didn't singularize for one.** 'how many moons does the Earth have?' -> 'Earth has 1 moons.' FIX:
   use the singular unit when the count is exactly 1 -> 'Earth has 1 moon.' (plural otherwise: '8 legs').

Honest residue (logged, NOT fixed this rung — real limitations, not crashes): mass-noun 'gravity' renders 'a gravity'
(not in _MASS_NOUNS); multi-word attributes ('4 large moons', 'more large moons than') aren't captured by the
single-word numeric/comparison regex. Both are bounded recall gaps, not errors.

91/91 -> 92/92 regression tests green (+1). Prediction HIT; tally 116/143. The real-usage-QA mode (demos, scale,
realistic prose) keeps earning its keep: it surfaces genuine bugs that constructed unit tests miss. Established
(NP-copula vs prepositional-relation disambiguation; English number agreement); named; no novelty.
