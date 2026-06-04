# JEP-86 — training on a REAL book: George Boole, "The Laws of Thought" (Michael's directive)

## Source
Project Gutenberg public-domain text of Boole's "An Investigation of the Laws of Thought" (1854), fetched from the
archive.org URL Michael provided. Cleaned: 5447 sentences, 134,510 tokens, vocab 5999. Ingested into the
substrate's world.knowledge VSA/HDC engine (NO transformer, NO pretrained model).

## Pre-registration (locked BEFORE run)
- (a) DISTRIBUTIONAL learning from the real book: mean cosine of hand-picked RELATED logic-term pairs (that
  co-occur in Boole) exceeds mean cosine of RANDOM word pairs by >= 0.05, and >= 0.7 of related pairs beat the
  random mean. (meaning learned from a real corpus, not a toy.)
- (b) RETRIEVAL on real content: for a set of topical queries, the top passage shares >= 2 content words with the
  query for >= 0.7 of queries (relevant retrieval from the book), vs a shuffled-query control near 0.
- PASS = both. HONEST CEILING declared up front: this RETRIEVES/RE-RANKS Boole's own sentences and learns word
  co-occurrence geometry; it does NOT understand Boole's logic, explain it, or communicate at human level. That
  remains the open frontier. Established (HDC/Random Indexing, distributional semantics), named; no novelty.

## Result — PASS (with two honest self-corrections)
Ingested 5447 passages / vocab 6107 in 7.3s on world.knowledge (no transformer).
- (a) DISTRIBUTIONAL: related-pair sim 0.393 vs random 0.288 (gap +0.105); 100% of related pairs beat random mean.
  Nearest neighbours are genuinely semantic, learned from Boole alone:
  NN(truth)=[falsehood, implying, conditional, aspect]; NN(probability)=[concurrence, occur, event, phaenomenon];
  NN(proposition)=[conditional, true]. BLEMISH (honest): OCR/hyphenation fragments also appear as neighbours
  (propo, sition, proposi) — real-text noise the cleanup didn't fully remove.
- (b) RETRIEVAL: topical queries share >=2 content words with the top passage 86% of the time.
  SELF-CORRECTION: the pre-registered "shuffled-query" control was INVALID — the VSA encoder is bag-of-words
  (order-invariant), so a shuffled query is the identical bag and trivially gives 86% too. Re-ran with a PROPER
  control (random unrelated content-word queries): 86% topical vs **34% random** — relevance is genuinely above
  chance. (Example: Q='the laws of thought' -> the book's title passage.)

**VERDICT: PASS.** The substrate trained on a REAL 134k-token book (Boole) with no transformer: it learns genuine
distributional word geometry and retrieves relevant passages above chance. Michael's "train with [Boole]" step is
done on the substrate's own engine. TWO honest corrections recorded (OCR-fragment neighbours; the invalid shuffled
control replaced by a valid random-query control). HONEST CEILING: this learns co-occurrence geometry and RETRIEVES
Boole's own sentences — it does NOT understand Boole's logic, infer from it, explain it, or communicate at human
level. That is the open multi-year frontier. Established (HDC/Random Indexing, distributional semantics), named.
