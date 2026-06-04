# GEO-60 — Grounded GENERATION over an unstructured document (full document-QA stack)

## Motivation
GEO-56 did retrieval over prose; GEO-34 did grounded generation over structured facts. GEO-60 combines them:
ingest an unstructured paragraph, retrieve the relevant sentence, and have the 0.5B LLM GENERATE a grounded,
faithful answer — the full document-QA-with-generation stack a user would actually use on a document.

## Pre-registration (locked BEFORE run)
- 1 factual paragraph (~6 sentences). 6 questions (answer in the text) + 2 unanswerable.
- Pipeline: sentence-split (add_document) -> retrieve (rerank) -> if grounded, LLM generates from the
  retrieved sentence with the faithfulness prompt; else abstain.
- Metric: (a) answerable answers contain the correct fact >= 0.7; (b) unanswerable abstain (no generation).
  PASS if both. NULL if generation breaks grounding.

## Result — PARTIAL (honest three-part diagnosis)
| metric | value |
|--------|-------|
| (a) answerable generated-correct | 0.17 |
| (b) unanswerable abstain | 1.00 |

**VERDICT: PARTIAL.** The document-QA-with-generation stack functions (grounding + abstention robust, 1.00 on
unanswerable), but answerable accuracy is low (0.17) for THREE honest reasons, each diagnosed:
1. **Eval/phrasing:** the 0.5B model answered "An octopus has 8 arms" (CORRECT) but my substring was "eight"
   — a string-match artifact; at least one "miss" was a right answer. (Not retuned; noted honestly.)
2. **Abstention over-trigger:** tau calibrated on a tiny dev set landed too high (0.674), so "How many hearts
   does IT have?" (pronoun -> lower sim) wrongly abstained. Calibration needs more dev examples.
3. **Prose retrieval ambiguity:** "octopus blood colour?" retrieved the CAMOUFLAGE sentence (shares "colour"),
   so the generator confabulated "blue and green blood" from the wrong context — the GEO-56 within-topic limit
   propagating into generation.

**Honest finding:** generation over UNSTRUCTURED documents inherits the prose-retrieval ceiling (GEO-56 ~0.67)
and amplifies it (wrong context -> confident wrong answer), plus small-model phrasing variance and calibration
sensitivity. Structured generation (GEO-34/35, 1.00) is far more reliable than document generation because
structured retrieval is exact. Deploy document-generation with a stronger retriever/re-ranker, more
calibration data, and answer-verification; or prefer extractive (return the sentence) over generative on prose.
