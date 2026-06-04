# GEO-78 — Does semantic matching extend to ABSTRACT concepts (emotions, ideas)?

## Motivation
Prior semantic-matching tests used CONCRETE entities (countries, animals, tools, elements). Abstract concepts
(emotions, ideas, abstract nouns) are harder — less grounded in concrete features. GEO-78 tests whether
description->abstract-concept resolution works as well as concrete entity resolution (GEO-25b 0.80).

## Pre-registration (locked BEFORE run)
- ~12 abstract concepts (emotions/ideas) each with a DESCRIPTION sharing no token with the concept word
  (e.g. "the bittersweet longing for the past" -> nostalgia).
- Retrieve the concept from its description (geometric) vs lexical baseline.
- Metric: hits@1. Bar: geometric >= 0.6 AND >> lexical. Compare to concrete-entity 0.80 (GEO-25b).
  Honest: if abstract << concrete, semantic matching is weaker for abstract concepts (a real boundary).
