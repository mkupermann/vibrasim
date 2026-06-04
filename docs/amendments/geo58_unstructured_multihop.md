# GEO-58 — Multi-hop QA over UNSTRUCTURED text (bridge extracted from sentence text)

## Motivation
GEO-16/31 multi-hop used structured bridge entities (from meta). Real documents have no structured bridges —
the linking entity must be EXTRACTED from the retrieved sentence's text and used to retrieve the next. GEO-58
tests this harder case: hop-1 retrieves a sentence, a bridge entity is pulled from its text, hop-2 retrieves
via that bridge, then answer. Genuinely uncertain: does free-text bridge extraction + iterative retrieval work?

## Pre-registration (locked BEFORE run)
- ~16 sentences forming 6 two-hop chains: "<Person> leads the <Project> project." + "The <Project> project
  is based in <City>." (+ distractor sentences). Projects are the bridges, mentioned in BOTH sentences.
- Question: "Which city is <Person>'s project based in?" -> hop-1 retrieve person's sentence -> extract the
  Project (capitalized bridge token shared with a hop-2 sentence) -> hop-2 retrieve -> city.
- Bridge extraction: the capitalized project word common to a candidate hop-2 sentence.
- Metric: end-to-end accuracy. Bar: >= 0.7. Compare to single-hop (no chain) which should fail. NULL if
  text bridge extraction breaks the chain.
