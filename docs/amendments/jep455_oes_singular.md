# JEP-455 — Fix -oes plural singularization (heroes → hero, not heroe)

## Motivation
JEP-454's audit found "energy of a knight?" → neutral: "Heroes are good" tagged valence on **heroe**
(not hero), so a knight (is-a hero) inherited nothing. Two bugs compounded: (1) `_singular` had no
`-oes` rule (heroes → heroe), and (2) the plural is-a regex `([A-Z][a-z]+)s` peels the trailing 's'
before `_singular`, handing it "heroe" rather than "heroes".

## Fix (`world/conversation.py`)
- Add a small irregular `-oes → -o` table (`_OES_SINGULAR`: heroes→hero, potatoes→potato, tomatoes→
  tomato, echoes→echo, volcanoes→volcano, …). -o nouns that take a bare 's' (shoe/photo/piano) still
  fall through to the general rule.
- In the plural is-a rule, reconstruct the full plural (`group(1)+"s"`) before `_singular`, so it sees
  "heroes" not "heroe".

## RESULT (2026-06-05): **PASS**
- `_singular("heroes")` → "hero"; "Heroes are good" tags valence on **hero**; "energy of a knight?"
  → **"bright (positive energy) (inherited from hero)"**.
- JEP-454 audit re-runs at **20/20, falsehoods=0** on both seeds (was 19/20).
- substrate_memory 14/14 + conversation 10/10 green.

The audit→fix loop again did its job: JEP-454 (no falsehoods, but an abstention miss) surfaced a quiet
morphology correctness bug; JEP-455 fixed it and the integrated brain now answers the full battery
correctly. Established rule-based normalization (irregular-plural table, like `_VERB_LEMMA` /
`_SINGULAR_KEEP`), named; no new science. No transformer.