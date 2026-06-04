# GEO-46 — Cross-lingual grounded retrieval (German queries -> English facts)

## Motivation
The whole programme used English. The user works in German. Multilingual embedding models map different
languages into ONE shared semantic space, so geometric retrieval should work CROSS-LINGUALLY: a German
question should retrieve the relevant English fact. GEO-46 tests this directly — a genuinely useful,
user-relevant capability.

## Pre-registration (locked BEFORE run)
- Model: paraphrase-multilingual-MiniLM-L12-v2 (multilingual).
- 12 English facts "The capital of <country> is <city>." + DESCRIPTIVE German queries that share NO token
  with the English fact (so it tests SEMANTIC cross-lingual matching, not lexical): e.g. "Welche Stadt ist
  die Hauptstadt des Landes mit dem Eiffelturm?" -> France fact.
- Metric: cross-lingual retrieval hits@1 (German query -> correct English fact). Compare to an
  English-monolingual model (all-MiniLM-L6-v2) on the same German queries (expected to fail cross-lingual).
- Bars: multilingual >= 0.7 AND >> monolingual. PASS if cross-lingual retrieval works. NULL otherwise.
