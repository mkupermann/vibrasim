# EQMOD-3 Geometric programme — summary (GEO-1 → GEO-18)

## The new approach
Substrate redefined as a learnable GEOMETRIC concept space: relations = transformations, understanding =
composition/retrieval/inference. ML/LLM allowed, PC-scale. (EQMOD physics abandoned — computationally empty.)

## What WORKS (pre-registered, controlled)
| capability | rung | result |
|------------|------|--------|
| Compose relations (grid) | GEO-1 | PASS 0.52 (ctrl 0.00) |
| Inverses + multi-hop | GEO-2 | PASS (5-hop 0.38 vs chance 0.03) |
| Clean geometry via metric embedding (MDS) | GEO-4 | PASS (analogy 0.76, comp 1.00) |
| Analogy on REAL LLM word embeddings | GEO-5 | PASS 0.88 |
| Few-shot relation learning (geometry = inductive bias) | GEO-6 | PASS 0.94–1.00 (linear-map 0.00) |
| Compose LEARNED relations multi-hop on LLM | GEO-7 | PASS 1.00 |
| Survives distractor vocab | GEO-8 | PASS 0.97 |
| Learn NEW structured knowledge + infer derived facts | GEO-12 | PASS 0.63 (control 0.00) |
| Hybrid memory(new facts)+geometry(known) | GEO-11 | PASS 0.88 |
| **Relational geometry lifts to SENTENCES** | **GEO-15** | **PASS (retrieval 1.00, analogy 1.00)** |
| **Multi-hop reasoning by iterative retrieval (generator-free)** | **GEO-16** | **PASS 1.00 (chain necessary)** |
| **3-hop robust to 100 distractors + paraphrase** | **GEO-17** | **PASS 1.00** |
| **Aggregation via retrieval + symbolic layer** | **GEO-18** | **PASS 1.00 (pure geometry 0.00)** |

## Honest BOUNDARIES
- Antonyms weak (GEO-9, 0.54). Arbitrary unstructured new facts: geometry can't generalize (GEO-10) -> need MEMORY.
- Composition depth decays gracefully (GEO-2); linear chains degenerate for normalized TransE (GEO-13 inconclusive).
- Clean LLM-prior + new-arbitrary-structure integration is an open tension (GEO-14).
- Pure geometry CANNOT aggregate/count/synthesize (GEO-18) -> needs a thin symbolic layer.

## The honest METHOD (a working learning+understanding system on a PC, no generator)
1. **Concept space** = a real LLM's embeddings (MiniLM) — prior semantic knowledge, free.
2. **Understand** = geometric retrieval: single-fact QA, multi-hop chaining (robust to distractors +
   paraphrase, GEO-15–17), generator-free.
3. **Aggregate/synthesize** = a thin SYMBOLIC layer over geometric resolutions (count/collect, GEO-18).
4. **Learn new STRUCTURED knowledge** = train embeddings (TransE), generalize by composition (GEO-12).
5. **Store arbitrary new facts** = key-value MEMORY (GEO-11).
6. **Inductive bias for relations** = few-shot mean-offset (GEO-6).

All established methods (TransE/MDS/word-analogy/RAG-style retrieval/key-value memory) named as such; the
contribution is the honest synthesis + a precise boundary map (what geometry does alone vs what needs
symbolic/memory/training layers). This is a genuine, working, PC-scale learning+understanding substrate —
a real positive result, unlike the EQMOD physics dead-end. Open: clean LLM+structure integration (GEO-14),
generation (needs a generator), harder NLU (negation/temporal/comparison).
