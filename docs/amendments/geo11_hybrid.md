# GEO-11 — The honest hybrid: MEMORY (new facts) + GEOMETRY (known relations)

## Result (MiniLM; new person→city facts + known city→language)
| component | accuracy |
|-----------|----------|
| memory lookup (person→city, new facts) | 1.00 |
| pure geometry (person→city, new facts) | 0.00 (confirms GEO-10) |
| HYBRID (person→language: memory then geometry) | 0.88 |

**VERDICT: PASS** — memory + geometry together answer multi-hop queries that neither does alone.

## Finding — the coherent architecture for learning+understanding
- LEARNING new arbitrary facts → explicit key-value MEMORY (geometry can't, GEO-10).
- UNDERSTANDING / reasoning over KNOWN structure → geometric operations on LLM embeddings (GEO-5–9).
- Multi-hop queries that mix new facts + known relations → the HYBRID (memory step → geometry step).
This is honest and works on the PC. Open limitation it does NOT solve: learning new STRUCTURE that
GENERALIZES (memory only stores, it doesn't generalize; geometry needs pre-existing structure). That gap
is what TRAINING a model addresses — enabled by the GPU. Next (GEO-12): train a small model to learn new
compositional structure and generalize to held-out facts.
