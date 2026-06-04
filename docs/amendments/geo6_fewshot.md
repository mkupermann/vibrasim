# GEO-6 — Few-shot relation LEARNING in LLM space (geometry as inductive bias)

## Result (all-MiniLM-L6-v2; learn relation from 4 examples, test held-out pairs)
| relation | 4-shot OFFSET hits@1 | linear-map hits@1 |
|----------|----------------------|--------------------|
| country→capital | 0.94 | 0.00 |
| singular→plural | 1.00 | 0.00 |
| verb→past | 0.94 | 0.00 |

**VERDICT: PASS** — geometric few-shot relation learning generalizes to unseen pairs (0.94–1.00).

## Finding — the GEOMETRIC inductive bias ENABLES few-shot learning (and it's NOT decorative here)
Learning a relation as a single translation OFFSET from 4 examples generalizes at 94–100% to held-out
pairs on real LLM embeddings. The unconstrained linear map (384x384 ridge) FAILS at 0.00 — 4 examples can't
fit it. So the geometric structure (relation = translation) is a STRONG INDUCTIVE BIAS that makes few-shot
learning possible where flexible parametric learning fails. This is the opposite of the EQMOD substrate
result (where geometry was decorative): in the LLM embedding space, geometric structure is REAL and
load-bearing. Honest scope: these relations (capital/plural/past) are known to be ~linear in word-embedding
space; non-linear relations are the boundary (to be probed). Next: COMPOSE learned relations for multi-hop
inference (GEO-7) — the core of understanding.
