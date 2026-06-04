# GEO-31 — Clean NON-LEXICAL multi-hop: descriptive cue resolved by real LLM knowledge

## Motivation
GEO-26 tried descriptive multi-hop but restated the description inside a fact (lexical leak). GEO-31 does it
cleanly: the cue is a real-world EPITHET ("the composer of the Ninth Symphony") that shares NO token with the
person's name, and the link is resolved by the LLM's OWN knowledge geometry (no persona fact). Then chain
person -> country -> continent. If geometry completes the chain where lexical fails at hop-0, multi-hop
reasoning genuinely rests on semantic geometry, not string overlap — closing the GEO-26 gap.

## Pre-registration (locked BEFORE run)
- 10 well-known people with an epithet sharing no name token, + "<Person> was born in <Country>." +
  "<Country> is in <Continent>." facts.
- Query: "On which continent was <epithet> born?" Hop-0: epithet -> person fact (SEMANTIC). Hop-1: person ->
  country. Hop-2: country -> continent.
- Compare geometric vs lexical (token-overlap) at hop-0 and end-to-end.
- Bars: geometric end-to-end >= 0.6 AND lexical hop-0 < geometric hop-0 by >= 0.3 (geometry genuinely needed).
  Honest: if geometry also fails, multi-hop on non-lexical cues is a boundary.
