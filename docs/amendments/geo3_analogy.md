# GEO-3 — Geometric ANALOGY (a:b::c:d by offset)

## Result (grid TransE embedding, held-out quadruples)
| metric | hits@1 (chance ~0.028) |
|--------|------------------------|
| analogy (b−a)+c → d | 0.25 |
| control: random embedding | 0.02 |
| control: wrong-offset | 0.04 |

**VERDICT: PARTIAL** — analogy is present and real (0.25 ≫ chance, controls collapse) but weak (< 0.5 bar).

## Finding — relation-composition is strong, entity-offset analogy is embedding-noisy
Composition (GEO-1/2) uses the learned RELATION vectors (clean) and is strong; analogy uses ENTITY-pair
offsets, which are noisy in a margin-trained TransE space, so exact hits@1 is only 0.25 (consistent with
how hard exact analogy is even in real word embeddings). The geometric understanding is real but limited by
EMBEDDING QUALITY. Next (GEO-4): a distance-preserving (metric/force-directed) embedding should recover the
clean 2D geometry and make BOTH composition and analogy strong — testing whether geometric understanding is
robust given the right embedding method.
