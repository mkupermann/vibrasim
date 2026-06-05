# JEP-257 — '-ous/-less' adjectives end in -s but are NOT plural nouns (no spurious is-a)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 QA surfaced 'is a cobra venomous?' -> 'Yes. A cobra is a venomous.' — the JEP-162 adjective guard treats a bare
  predicate ending in -s as a PLURAL noun -> is-a, but '-ous' adjectives ('venomous','famous','dangerous') end in -s.
  Excluding '-ous/-less' endings from the plural-noun is-a heuristic stops the false is-a, without breaking genuine
  plural-noun is-a ('Dogs are mammals').

## Result — PASS (HIT)
The plural-noun predicate heuristic `re.fullmatch(r"[a-z]+s", item)` (a bare -s predicate -> is-a parent) misfired on
ADJECTIVES ending in -s: '-ous' (venomous/famous/dangerous) and '-less' (harmless). Added `not item.endswith(("ous",
"less","ss"))` to the heuristic.
- 'The cobra is venomous.' -> venomous NOT an is-a parent (was wrongly 'Yes. A cobra is a venomous.').
- 'A snake is harmless.' -> harmless NOT is-a.
- No regression: 'Dogs are mammals.' / 'Cats are felines.' still extract is-a.
98/98 -> 99/99 regression tests green (+1). Prediction HIT; tally 136/172. HONEST RESIDUE (separate follow-up): a bare
adjectival predicate 'X is <adj>' is now correctly SKIPPED (not is-a) but not yet CAPTURED as a property, so
'is a cobra venomous?' answers 'I don't know' rather than 'Yes' — adjectival-property extraction is JEP-258.
Established (adjective-suffix morphology, surface guard), named; no novelty.
