# JEP-327 — Perceive a written WORD → reason about it from the durable store

## Motivation
Perception so far grounds single LETTERS (JEP-287..293). Connect word-level vision to the durable reasoning brain:
render a word as a sequence of letter glyphs, recognize the letters, assemble + lexicon-clean the word, then ASK
the durable store about it (is it a mammal? an animal?). Closes see→read→understand on real (home-made) pixels into
the persistent substrate. Established (per-letter prototype recognition + edit-distance lexicon cleanup + VSA
reasoning), named as such. No transformer.

## Method
Teach the alphabet to an `ActiveLearner` (scale-normalized glyphs). Teach concept facts into a
`SubstrateMemory` (dog isa mammal, …). Render held-out word images; recognize each letter; join; snap to the nearest
lexicon word by edit distance; then `BrainQuery.is_a(word, target)` over the reloaded store.

## Pre-registered bars (BEFORE the run)
- **J327a (word recognition):** held-out word images recognized correctly after cleanup ≥ 0.90 over the vocabulary,
  both seeds (0, 7). Report raw (pre-cleanup) accuracy for contrast.
- **J327b (perceive → reason):** for each perceived word, the durable store's answer to "is it a mammal/animal?"
  matches ground truth ≥ 0.90, both seeds — vision feeding durable reasoning end to end.
- **J327c (persists):** the store is reloaded (fresh) before reasoning; answers identical to pre-save.

Predicted most-likely failure: a single mis-recognized letter changes the word; edit-distance cleanup should fix
1-letter errors if the vocabulary is well-separated, but near-neighbor words (cat/cot) could snap wrong. If J327a
misses, report whether it's letter-recognition or cleanup-collision (and the raw-vs-cleaned gap).

## Result (seeds 0, 7): **PASS**
- **J327a:** word recognition after cleanup = **1.0**, both seeds. Notably the RAW letter-join was already **1.0** —
  the scale-normalized per-letter recognition (JEP-293) is good enough that lexicon cleanup was a no-op here.
- **J327b:** perceive→reason ("is the perceived word a mammal?") matches ground truth = **1.0** (incl. poodle→dog→
  mammal multi-hop), both seeds — vision feeding durable reasoning end to end.
- **J327c:** store reloaded fresh before reasoning; answers identical.

## Verdict: **PASS**
A written WORD is perceived from home-made pixels, its letters recognized and assembled, and then reasoned about
from the DURABLE substrate store — see → read → understand, end to end, into the persistent brain. Honest scope:
letter recognition was strong enough that edit-distance cleanup wasn't exercised here (it would matter with noisier
glyphs / a denser vocabulary — the JEP-290 redundancy-cure regime); the words are a small clean vocabulary; this is
home-made vision, not a real camera. No transformer, no pretrained model.

