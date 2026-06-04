# GEO-12 — Genuine learning of NEW structured knowledge (trained from scratch)

## Result (family tree, 63 people; train on PARENT edges only, grandparent facts HELD OUT)
| inference | hits@1 |
|-----------|--------|
| parent (trained, sanity) | 0.82 |
| **held-out grandparent via composition (2·r_parent)** | **0.63** |
| single-parent control (should miss grandparent) | 0.00 |

**VERDICT: PASS** — training learns the structure; composing the learned parent relation infers held-out
grandparent facts; single-relation control collapses.

## Finding — the resolution of the GEO-10 boundary: STRUCTURE is learnable+generalizable, arbitrary facts are not
GEO-10 failed because its facts were ARBITRARY (no rule to generalize). GEO-12 succeeds because the family
tree has STRUCTURE (grandparent = parent∘parent): training from scratch learns the parent relation as a
clean translation, and COMPOSING it infers grandparents never seen (0.63), not by memory but by learned
compositional rule. So the honest, complete picture of learning in EQMOD-3:
- ARBITRARY new facts → store in MEMORY (GEO-11); no generalization possible (nothing to generalize).
- STRUCTURED new knowledge → TRAIN embeddings; generalizes to derived facts by composition (GEO-1/2/12).
- KNOWN concepts/relations → read out the LLM's geometry (GEO-5–9).
A genuine learning+understanding method, on the PC, no LLM required for the structured-learning part.
