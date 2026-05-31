# BET-141 — Versuchsreihe 1: source ingestion + written QA + online learning

Pre-registered: 2026-05-31 (BEFORE the run). First series toward a system you can
communicate with in writing that learns from sources. Tests world/knowledge.py: ingest
a factual corpus, answer written questions by retrieving the right passage, and improve
from feedback (online).

Method: a 40-sentence factual corpus across several topics; 20 written questions, each
paraphrased (NOT copied) from its answer sentence, so retrieval must match meaning via
shared content words, not exact string. Metrics: top-1 and top-3 retrieval accuracy.
Online: after giving feedback on 10 questions, held-out accuracy on the other 10 must
not drop and ideally rise.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T141a | Finds the answer | top-1 retrieval accuracy >= 0.70 |
| T141b | Answer in shortlist | top-3 retrieval accuracy >= 0.85 |
| T141c | Beats lexical chance | top-1 >> random (random top-1 ~ 1/40 = 0.025) |
| T141d | Online feedback helps | after feedback, top-1 on fed-back questions reaches >= 0.90 |

PASS = T141a-d. PASS = the substrate-native retrieval system genuinely answers written
questions from ingested sources and learns from feedback, on this machine, no LLM/
transformer. NULL/partial steers tuning (dim, IDF, re-ranker) for series 2.

## RESULT (2026-05-31): PASS — all bars

| metric | value | bar |
|--------|-------|-----|
| top-1 retrieval accuracy | 0.850 | T141a >=0.70 ✓ |
| top-3 retrieval accuracy | 1.000 | T141b >=0.85 ✓ |
| vs chance (~0.025) | 0.850 | T141c ✓ |
| fed-back top-1 after feedback | 0.700 → 1.000 | T141d >=0.90 ✓ |
| held-out top-1 (unchanged) | 0.900 | (stable) |

PASS. world/knowledge.py ingests a 40-passage corpus and answers PARAPHRASED written
questions (not string copies) by IDF-weighted HD retrieval; online feedback lifts the
fed-back questions to 1.000 without disturbing held-out. Substrate-native (VSA bundle +
IDF + online delta re-ranker), runs instantly on this machine, no LLM/transformer.

Self-correction for series 2 (BET-142): the weakness is purely LEXICAL — a paraphrase
that shares no content word with its answer cannot match. Add substrate-native semantic
expansion via WORD CO-OCCURRENCE association (words appearing together get related, so a
query word pulls in its associates), plus character n-gram fallback for morphological
variants, and test on a HARDER low-overlap question set + a larger ingested corpus.
