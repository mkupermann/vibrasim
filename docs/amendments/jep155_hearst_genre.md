# JEP-155 — Hearst-pattern hypernym extraction on Boole: is the parse gate the EXTRACTOR or the TEXT GENRE?

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 Hearst patterns ('X is a kind of Y', 'Y such as X', 'X and other Y') extract VERY FEW genuine is-a pairs from
  Boole, because Boole is logic/math prose with few definitional taxonomic statements — most matches will be
  SPURIOUS (variable/logic language: 'x is a symbol', theorems). So for THIS text the gate is the GENRE, not merely
  the extractor; the right move is an encyclopedic corpus. MOST-LIKELY MISS: Boole's philosophical passages yield
  more genuine taxonomy than expected.

## Acceptance (characterization)
- Report Hearst yield on Boole: total pattern matches, how many pass the engine's _valid_concept guard, and a manual
  read of whether they are GENUINE natural-kind taxonomy vs logic/variable artifacts. Locating WHERE the difficulty
  lives (extractor vs genre) is the finding. Established (Hearst 1992 lexico-syntactic patterns); named; no novelty.

## Result — PASS (HIT, with a precision nuance + a recurring-lesson catch)
- raw Hearst matches: 1201; pass _valid_concept guard: 357; unique candidate pairs: 326.
- BUT manual read of the pairs: almost ALL are CLAUSE FRAGMENTS or PROPERTY/IDENTITY/PHILOSOPHICAL predications, NOT
  genuine natural-kind taxonomy:
    - fragments: 'and IS-A found also in a', 'above example IS-A of slight value' (loose 'X is/are Y' grabs mid-clause)
    - properties not hypernyms: 'all men IS-A mortal', 'all men IS-A fallible'
    - philosophical predication: 'absolute evil IS-A included in reputed evil'
    - genuine natural-kind taxonomy ('a sun is a fixed star'): a TINY handful (<~5).
- VERDICT: the parse gate for Boole is the GENRE, not merely the extractor. Hearst patterns do NOT rescue it — Boole
  is logic/philosophy prose (variables, theorems, definitions-of-symbols, ethical argument), not encyclopedic
  description, so there is almost no 'X is a kind of Y' natural-kind taxonomy to extract. Confirms JEP-89/90/123: the
  developmental claim (simple/encyclopedic prose parses ~94%, dense Boole ~2%) stands; the RIGHT move for
  learn-from-sources is an encyclopedic corpus + Hearst, NOT a better extractor on Boole.
- PRECISION NUANCE + RECURRING-LESSON CATCH: the raw count (326) is HIGHER than JEP-89's 46 triples, which would look
  like progress — but PRECISION for genuine taxonomy is near-zero. This is the 'predict QUALITY not RATE' lesson
  (JEP-108) recurring; I predicted few GENUINE pairs (correct) but should have anticipated the raw count would look
  deceptively high. _valid_concept (<=4 words, no punctuation) is necessary but NOT sufficient — it passes 4-word
  noun-ish CLAUSE FRAGMENTS that are not bare NPs. Pattern-only extraction on complex prose needs sentence-level
  constituency (subject must be a bare NP), which the no-transformer constraint makes hard. Prediction HIT; tally
  50/70. Established (Hearst 1992 lexico-syntactic patterns); named; no novelty.
