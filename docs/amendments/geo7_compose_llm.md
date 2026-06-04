# GEO-7 — Compositional understanding on LLM embeddings (chain learned relations)

## Result (MiniLM; learn country→capital and country→language from 6 examples, test held-out)
| inference | hits@1 |
|-----------|--------|
| direct (country + r_language) | 1.00 |
| COMPOSE (capital − r_capital + r_language) — multi-hop, never trained | **1.00** |

**VERDICT: PASS** — learned relations compose: from a capital, infer the language by chaining
inverse-capital → language, never trained as a composite.

## Finding — a learning+understanding loop works on real semantics
The geometric+LLM substrate (a) learns relations from few examples (GEO-6) and (b) COMPOSES them for novel
multi-hop inferences (GEO-7), on real meaning, at 1.00 held-out. This is the core of understanding —
chaining learned transformations — realized on the user's PC with a small LLM + geometric operations.
(Bug note: first run excluded the target word from ranking → 0.00; fixed to exclude only the query
sources.) Honest scope: clean ~linear relations + small curated vocab; the boundary (distractors,
non-linear relations) is the next stress test (GEO-8).
