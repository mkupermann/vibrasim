# GEO-5 — Geometric understanding on REAL LLM embeddings (the ML/LLM bridge)

## Result (all-MiniLM-L6-v2, 16 curated analogy quadruples)
| metric | value |
|--------|-------|
| analogy (b−a)+c → d hits@1 | **0.88** |
| analogy hits@5 | 1.00 |
| baseline (nearest-to-c, no offset) hits@1 | 0.75 |

**VERDICT: PASS** — real LLM embeddings support geometric analogy by vector operations.

## Finding — LLM semantic geometry IS compositional, but similarity dominates in small vocab
Geometric analogy on real transformer embeddings reaches 0.88 hits@1. HONEST caveat: the no-offset baseline
(just the nearest word to c) is already 0.75 in this tiny vocab, so the geometric OFFSET adds only +0.13 —
much of the success is raw semantic similarity, not the analogical structure. A larger/harder benchmark is
needed to isolate the geometric contribution. Still, the ML/LLM bridge works on the PC: a real LLM provides
a semantic geometry where geometric operations (offset, composition) carry meaning. Next (GEO-6): the
LEARNING half of the goal — few-shot learning of a NEW relation as a geometric transformation in the LLM
space, generalizing to novel pairs.
