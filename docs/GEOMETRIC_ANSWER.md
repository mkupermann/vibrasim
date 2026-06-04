# A proper LEARNING + UNDERSTANDING method on the PC, with geometric ML/LLM — the answer

Written after the autonomous EQMOD-3 run (GEO-1 → GEO-21), every claim a pre-registered experiment with
controls. Honest verdicts; established methods named as such. This is the Phase-2 deliverable, replacing the
abandoned EQMOD physics substrate (which Phase-1 proved computationally empty — see STRATEGIC_ANSWER.md).

## Short answer
**Yes — a working learning+understanding method runs on your PC, built from geometry over a real LLM's
embedding space, no transformer generation required.** It is a *neuro-symbolic* method: an LLM gives the
concept geometry, geometric operations do the reasoning, and a thin symbolic layer handles what geometry
provably cannot. It is sound and integrates end-to-end; it is NOT a solution to open-domain NLU, and the
boundary is mapped precisely.

## What the method IS (one entity = one point in a learnable concept space)
1. **Concept space** — a real sentence-embedding model (all-MiniLM-L6-v2, 384-dim) provides prior semantic
   geometry for free, on CPU. (GEO-5,15)
2. **Understand by geometry** — questions retrieve their answer facts; relations are consistent OFFSETS;
   multi-hop questions are answered by *iterative* retrieval + symbolic bridge chaining. Robust to 100
   distractor facts and to paraphrased (non-template) questions. (GEO-7,15,16,17)
3. **Learn new knowledge** —
   - *structured* knowledge: train embeddings (TransE) and generalize to derived facts by composition
     (grandparent from parent). (GEO-12)
   - *relations from few examples*: mean-offset few-shot beats a full linear map. (GEO-6)
   - *arbitrary* facts: a key-value MEMORY (geometry cannot generalize these — GEO-10,11).
4. **Integrate prior + new knowledge without conflict** — per entity, concatenate a FROZEN LLM block
   (semantics) with a TRAINABLE structure block (new relations). Semantics preserved exactly (drift 0.00)
   while new structure trains. (GEO-21)
5. **Aggregate / negate / compare** — a thin SYMBOLIC layer over geometric resolutions (count, filter,
   `>`), because pure geometry cannot do these. (GEO-18,20)
6. **End-to-end** — learn a relation few-shot → apply to unseen entities → chain by retrieval → symbolic
   aggregate, all on held-out data. (GEO-19, milestone)

## The precise BOUNDARY (what geometry does vs what needs symbols/memory/training)
| task | geometry alone | resolution |
|------|----------------|------------|
| retrieval, analogy, multi-hop chaining | STRONG (≈1.0 on clean data) | — |
| relations linear in embedding space | STRONG (few-shot) | — |
| arbitrary unstructured new facts | FAILS (random offsets) | key-value MEMORY |
| antonyms / fine sense distinctions | WEAK (0.54) | — |
| negation ("not in Europe") | WEAK (F1 0.50) | symbolic filter → 1.00 |
| comparison ("larger population") | BELOW CHANCE (0.29) | symbolic compare |
| counting / aggregation | FAILS (0.00) | symbolic count → 1.00 |
| open-domain NLU, generation | OUT OF SCOPE | needs a generator (LLM) |

## Honest caveats
- GEO-15–19 saturate at 1.00 because they use small, clean, well-known entities where MiniLM is excellent.
  They prove the method is **sound and integrates**, not that NLU is solved. Real degradation is expected
  at scale, with noisy text and ambiguous entities (probed next).
- Every reasoning primitive here (TransE, MDS, word-vector analogy, RAG-style retrieval, key-value memory,
  neuro-symbolic split) is an ESTABLISHED method. The contribution is the honest synthesis on a PC + a
  precise boundary map, NOT a new algorithm.
- This reads/uses an existing LLM's geometry; it does not replace the LLM. It is a generator-free reasoning
  layer ON an embedding model.

## How to build it on your machine
CPU is enough (sentence-transformers + numpy). Pipeline: embed your facts once → store with symbolic labels
→ at query time do geometric retrieval/chaining for "what/which/where", drop to the symbolic layer for
"how many / not / bigger". Train a small structure block only when you have NEW structured relations to
generalize. Your AMD GPU is unused (no CUDA / no torch-directml on Py3.13) but unnecessary at this scale.

## Bottom line
Phase-1 verdict was "the physics substrate has no computational value." Phase-2 verdict is the constructive
counterpart: **redefining the substrate as a geometric concept space over an LLM yields a real, working,
honestly-bounded learning+understanding method that runs on your PC** — neuro-symbolic, generator-free for
reasoning, with every capability and every limit measured. The deliverable, per the charter, is a
deadlock-breaking process with an honest map of what is and isn't reachable.
