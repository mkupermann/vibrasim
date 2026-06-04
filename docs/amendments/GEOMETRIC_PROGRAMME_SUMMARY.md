# EQMOD-3 Geometric programme — summary (GEO-1 → GEO-32)

## The new approach
Substrate redefined as a learnable GEOMETRIC concept space over a real LLM: relations = transformations,
understanding = composition/retrieval/inference. ML/LLM allowed, PC/CPU. (EQMOD physics abandoned —
computationally empty, see STRATEGIC_ANSWER.md.) Top-level deliverable: docs/GEOMETRIC_ANSWER.md. Usable
module: tools/geometric_reasoner.py (+ docs/patterns/geometric_reasoner.md).

## The GENUINELY-geometric core (no lexical shortcut — where geometry earns its name)
| capability | rung | result |
|------------|------|--------|
| Analogy on REAL LLM word embeddings | GEO-5 | PASS 0.88 |
| Few-shot relation learning (geometry = inductive bias) | GEO-6 | PASS 0.94–1.00 (linear-map 0.00) |
| LLM-prior = data-efficient for SEMANTIC-aligned structure (harmful for arbitrary) | GEO-24 | PASS +0.12@k4 / -0.06 arb |
| Semantic retrieval of DESCRIPTIONS (no shared token) | GEO-25b | PASS 0.80 vs lexical 0.10 |
| **Zero-shot relational transfer to UNSEEN entities** | **GEO-27b** | **PASS 0.81 vs random 0.51** |
| **Semantic MULTI-HOP over real-world epithets (non-lexical)** | **GEO-31** | **PASS 1.00 vs lexical 0.10** |
| Compose relations / learned relations (grid, LLM) | GEO-1/4/7 | PASS |

## The pipeline WORKS (but named-entity numbers are LEXICALLY solvable — GEO-25)
| capability | rung | result | caveat |
|------------|------|--------|--------|
| Relational geometry lifts to SENTENCES | GEO-15 | PASS 1.00 | lexical ties it |
| Multi-hop by iterative retrieval (generator-free) | GEO-16/17 | PASS 1.00, robust to 100 distractors+paraphrase | hop-1 lexical |
| Learn NEW structured knowledge + derived facts | GEO-12 | PASS 0.63 (ctrl 0.00) | genuine |
| Hybrid memory(new facts)+geometry(known) | GEO-11 | PASS 0.88 | genuine |
| LLM-prior + new-structure via ORTHOGONAL SUBSPACES | GEO-21 | semantics drift 0.00 (resolves GEO-14) | genuine |
| Aggregation via retrieval + symbolic layer | GEO-18 | PASS 1.00 (pure geometry 0.00) | architecture |
| Integrated learn->apply->chain->aggregate (held-out) | GEO-19 | PASS MILESTONE 1.00 | clean entities |

## Practical EDGES over a frozen LLM
- **Grounded abstention** (knows what it doesn't know): GEO-23 PASS (decision 1.00 calibrated; control confabulates 100%).
- **Updatability**: GEO-30 PASS — stored counterfactuals override prior 1.00, runtime edit flips answer; no retraining.
- **Integrated agent** on a mini-KB (dogfoods the module): GEO-32 PARTIAL — semantic/multi-hop/aggregate/update perfect; abstention needs per-KB CALIBRATION (2/3 at a fixed tau).

## Honest BOUNDARIES
- **Lexical caveat (GEO-25):** named-entity retrieval/QA/grounding 1.00s are solvable by string matching;
  they show the pipeline runs, not that geometry is necessary. Geometry's real value = the semantic core above.
- Antonyms weak (GEO-9, 0.54). Arbitrary unstructured new facts: geometry can't generalize (GEO-10) -> MEMORY.
- Pure geometry CANNOT aggregate/count (GEO-18 0.00), is weak on NEGATION (GEO-20 F1 0.50), BELOW chance on
  COMPARISON (GEO-20 0.29) -> thin SYMBOLIC layer for negate/compare/aggregate/arithmetic.
- Zero-shot transfer is per-SINGLE-relation; CONJUNCTIONS of zero-shot attributes collapse (GEO-28 0.53) but
  RECOVER as each attribute is cleanly encoded (GEO-29 0.69) — bounded by the weakest attribute, not fundamental.
- Composition depth decays gracefully (GEO-2); linear chains degenerate for normalized TransE (GEO-13 inconclusive).
- Scale (GEO-22): 1-hop 0.98, 2-hop 0.87 at 400 facts — usable to a few hundred facts / 2-3 hops on CPU.
- GEO-15-19 saturate at 1.00 on clean small entities: proves soundness + integration, NOT solved open NLU.

## The honest METHOD (a working, bounded learning+understanding system on a PC, no generator)
1. **Concept space** = a real LLM's embeddings (MiniLM) — prior semantic knowledge, free.
2. **Understand** = geometric retrieval + multi-hop chaining; genuinely semantic for descriptions/epithets
   (GEO-25b/31), lexically-aided for plain named entities.
3. **Aggregate/negate/compare** = a thin SYMBOLIC layer over geometric resolutions (GEO-18/20).
4. **Learn new STRUCTURED knowledge** = train embeddings (TransE), generalize by composition (GEO-12);
   zero-shot transfer to unseen entities when structure aligns with semantics (GEO-24/27b).
5. **Store arbitrary new facts** = key-value MEMORY (GEO-11); integrate with semantics via orthogonal subspaces (GEO-21).
6. **Ground** = abstain when unsupported (GEO-23, calibrate the threshold) + update by editing the store (GEO-30).

All primitives are ESTABLISHED methods (TransE/MDS/word-analogy/RAG-style retrieval/key-value memory/neuro-
symbolic split) named as such; the contribution is the honest synthesis + a precise boundary map + the
isolation of geometry's irreducible value (semantic matching, zero-shot transfer, aligned-structure learning).
A genuine, working, PC-scale learning+understanding system — real, but NOT human-level AI and NOT a new method:
it reads an existing LLM's understanding, generator-free, bounded. Open: generation (needs a generator),
robust composition, scale beyond hundreds of facts.
