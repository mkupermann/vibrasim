# EQMOD-3 Geometric programme — summary (GEO-1 → GEO-14)

## The new approach
Substrate redefined as a learnable GEOMETRIC concept space: relations = transformations, understanding =
composition/inference. ML/LLM allowed, PC-scale. (The EQMOD physics was abandoned — computationally empty.)

## What WORKS (pre-registered, controlled)
| capability | evidence | result |
|------------|----------|--------|
| Compose relations | GEO-1 (grid) | PASS 0.52 (controls 0.00) |
| Inverses + multi-hop | GEO-2 | PASS (5-hop 0.38 vs chance 0.03) |
| Clean geometry via metric embedding | GEO-4 (MDS) | PASS (analogy 0.76, comp 1.00) |
| Analogy on REAL LLM embeddings | GEO-5 | PASS 0.88 |
| Few-shot relation learning (geometry = inductive bias) | GEO-6 | PASS 0.94–1.00 (linear-map fails 0.00) |
| Compose LEARNED relations (multi-hop) on LLM | GEO-7 | PASS 1.00 |
| Survives distractor vocab | GEO-8 | PASS 0.97 |
| Learn NEW structured knowledge from scratch + infer derived facts | GEO-12 | PASS 0.63 (grandparent, control 0.00) |
| Hybrid memory(new facts)+geometry(known) | GEO-11 | PASS 0.88 |

## Honest BOUNDARIES
- Antonyms weak (GEO-9, 0.54) — they sit close in embedding space.
- Arbitrary (unstructured) new facts: geometry CANNOT generalize them (GEO-10, 0.08); need MEMORY (GEO-11).
- Composition depth decays gracefully (GEO-2); linear chains degenerate for normalized TransE (GEO-13).
- Clean LLM-prior + new-structure integration is an open tension (GEO-14).

## The honest method (what to build for learning+understanding on a PC)
THREE linked stores: (1) a frozen LLM embedding space for prior semantic knowledge (reason by geometric
ops); (2) a TRAINED structural space for new STRUCTURED knowledge (generalizes by composition); (3) a
key-value MEMORY for arbitrary new facts. Understanding = composing relations/transformations across these.
All established methods (TransE/MDS/word-vector analogy/key-value memory) named as such; the contribution is
the honest synthesis + the boundary map. This is a genuine, working, PC-scale learning+understanding
substrate — a real result, unlike the EQMOD physics dead-end. Open work: clean integration (GEO-14),
sentence/text-level understanding, scaling.
