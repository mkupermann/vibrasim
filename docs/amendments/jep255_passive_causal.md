# JEP-255 — passive causal extraction ('X is caused by Y' -> Y causes X)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 real-usage QA surfaced 'Rust is caused by oxygen' NOT extracted (only active 'X causes Y' was handled). Adding a
  PASSIVE pattern 'X is caused by Y' / 'X results from Y' -> tell_cause(Y, X) (subject = EFFECT, swap) captures it; the
  is-a handler rejects 'caused by oxygen' via _bare_np and read_open excludes it (the 'caused' keyword is fixed), so
  no spurious is-a/open leak; active causal + is-a unaffected.

## Result — PASS (HIT)
Added the passive causal forms after the active pattern in read(): 'X is caused by Y' and 'X results from Y' ->
tell_cause(Y, X) with the cause/effect SWAP (the grammatical subject is the effect). Surfaced by the JEP-254 QA pass.
- 'Rust is caused by oxygen.' -> oxygen causes rust; 'Erosion results from water.' -> water causes erosion;
  'Oxygen causes corrosion.' (active) -> oxygen causes corrosion. causal count = 3, NO spurious open relation
  ('caused' excludes it from read_open), NO is-a leak ('caused by oxygen' fails _bare_np). Directional, not symmetric
  (causes_effect(rust, oxygen) = False). Active causal + is-a unaffected. 96/96 -> 97/97 tests green (+1).
Prediction HIT; tally 134/170. Established (passive-voice causal pattern, surface extraction), named; no novelty.
Honest residue (still open, logged): mass-noun rendering in causal/open output ('Oxygen causes A RUST' -- rust/
corrosion/erosion are mass nouns; the EXTRACTION is correct, only the article rendering is off) + polysemous
mass-noun-as-countable-category in taxonomy ('a metal is an element').
