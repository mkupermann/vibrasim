# JEP-85 — the parse bottleneck: substrate-legal relation extraction (Hearst patterns) from varied text

## Why (waypoint 2->3: feed the structure layer from real text, not hand-regex)
JEP-84's inference layer is fed by a single fixed regex. The true gate to "learn structured knowledge from
sources" is AUTOMATIC relation extraction from VARIED phrasings, no transformer. Classic non-ML method: Hearst
patterns (Hearst 1992) — lexico-syntactic templates for hypernymy ("X is a Y", "Y such as X", "X and other Y").

## Setup
- Corpus states IS-A facts in VARIED Hearst phrasings (not one template): "A poodle is a dog.", "Dogs such as
  poodles and collies...", "A salmon is a kind of fish.", "birds like sparrows and robins", "oaks and other trees".
- Extractor: a small set of Hearst patterns (NOT per-sentence regex) -> (hyponym, hypernym) pairs.
- Feed extracted pairs into the transitive-closure structure layer; answer 2-hop+ IS-A queries (JEP-84 style).

## Pre-registration (locked BEFORE run)
- (i) extraction F1 vs the gold IS-A pairs >= 0.80 on the varied corpus.
- (ii) end-to-end multi-hop IS-A accuracy on the AUTO-extracted graph >= 0.85.
- PASS = both. Shows source-text -> structured knowledge -> inference works without a transformer or per-sentence
  hand-coding. HONEST BOUND up front: Hearst patterns capture only EXPLICIT lexical-pattern hypernymy; implicit /
  contextual hypernymy is missed (the known ceiling, why modern systems use learned extractors). Established
  (Hearst 1992), named; no novelty. NULL valid if patterns miss too much (then the parse gap is the honest finding).

## Result — NULL/PARTIAL (the parse gate is real)
- Extraction: 12 pairs, precision 0.92, recall 0.79, **F1 0.85** (met the 0.80 bar).
- Missed: tree->plant, plant->living_thing, animal->living_thing (bare-plural "X are Y" phrasings the patterns
  don't catch); 1 spurious (colly<-collies, a stemming bug).
- End-to-end multi-hop IS-A accuracy on the auto-extracted graph: **0.650** (FAILED the 0.85 bar).

**VERDICT: NULL/PARTIAL.** Decent extraction F1 (0.85) but multi-hop inference collapsed (0.65) because ONE missing
edge breaks EVERY chain through it — multi-hop understanding needs HIGH-RECALL extraction, not just decent F1. The
missed links were exactly the implicit/bare-plural phrasings ("Plants are living things") outside the Hearst
templates — the known Hearst ceiling. HONEST FINDING: the parse bottleneck is the real gate between retrieval and
structured understanding; classic non-ML extraction does not clear it on varied phrasing. This is where "learn
structured knowledge from sources" actually breaks today. Established (Hearst 1992), named; no novelty. Bar NOT
moved.
