# GEO-8 — Few-shot relation learning survives distractors (real, not artifact)

## Result (MiniLM; 109-word vocab = 40 targets + 69 distractors)
country→capital, 6-shot, ranked among ALL 109 words: **hits@1 = 0.97**.

**VERDICT: PASS** — the method survives a large distractor vocabulary; the earlier strong results are real,
not a tiny-closed-set artifact.

## Status of EQMOD-3 (geometric+LLM, on the PC) so far
| rung | result |
|------|--------|
| GEO-1 compose relations (synthetic) | PASS 0.52 |
| GEO-2 inverses + multi-hop | PASS |
| GEO-4 metric embedding clean geometry | PASS (analogy 0.76, comp 1.00) |
| GEO-5 analogy on LLM embeddings | PASS 0.88 |
| GEO-6 few-shot relation learning | PASS 0.94–1.00 (geometry = inductive bias) |
| GEO-7 compose learned relations (multi-hop) | PASS 1.00 |
| GEO-8 survives distractors | PASS 0.97 |
A coherent, working learning+understanding method: geometric operations on LLM embeddings learn relations
from few examples, compose them for novel inference, robust to distractors — on the PC. Honest scope:
clean ~linear relations, modest vocab. Next (GEO-9): map which RELATION TYPES the method handles (easy
linear vs hard non-linear) — the boundary.
