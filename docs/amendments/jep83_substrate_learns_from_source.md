# JEP-83 — the substrate LEARNS FROM A SOURCE and communicates (retrieval), no transformer

## Why (Michael: "eventually our solution will learn from sources and with understanding communicate in English")
Ground the vision in what the substrate does TODAY. world.knowledge (VSA/HDC: deterministic hash-seeded
hypervectors + distributional Random Indexing + char-n-gram morphology + IDF + an online local-update re-ranker)
learns word/passage meaning from text with NO transformer, NO pretrained embeddings.

## Pre-registration (locked BEFORE run)
Ingest a small 2-topic source corpus; then:
- (a) distributional learning: within-topic word similarity exceeds cross-topic by >= 0.05 AND related>unrelated
  for >= 3/4 probe pairs (meaning learned from co-occurrence).
- (b) retrieval QA: the top-ranked passage contains the answer word for >= 0.75 of in-source questions.
- (c) online local learning: a feedback update improves the target passage's rank.
- PASS = all three. HONEST CEILING declared up front: this RETRIEVES/RE-RANKS; it does NOT generate novel fluent
  English, multi-hop inference, or grounded understanding. Established (HDC/VSA, Random Indexing - Kanerva,
  Sahlgren; distributional semantics), named; no novelty.

## Result — PASS
- (a) distributional: within-topic 0.359 vs cross-topic 0.163 (gap +0.196); related>unrelated 4/4.
- (b) retrieval QA: 3/4 (0.75).
- (c) online learning: target passage rank 1 -> 0 after local feedback.

**VERDICT: PASS** — step ONE of "learn from sources and communicate" runs on the substrate, no transformer.
**HONEST CEILING (the part that matters):** the system retrieves and re-ranks passages from the source. It does
NOT generate novel fluent English, perform multi-hop inference, or demonstrate grounded understanding. Learned,
generative, grounded language WITHOUT a transformer is the open multi-year frontier — not this result. The honest
map: distributional meaning (PASS) + retrieval (PASS) + online local learning (PASS) are real building blocks;
understanding + generation remain unproven under the no-transformer constraint.
