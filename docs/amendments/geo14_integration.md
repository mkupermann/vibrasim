# GEO-14 — LLM-prior + new-structure integration (PARTIAL: a real tension)

## Result (MiniLM-init roles, train a new reports_to hierarchy)
| setting | hits@1 |
|---------|--------|
| frozen-LLM reports_to | 0.00 |
| LLM-init + trained (anchored) | 0.00 |
| 2-hop skip | 0.38 (noisy, tiny set) |

**VERDICT: PARTIAL/NULL** — naive LLM-init + train did not cleanly learn the new hierarchy.

## Finding — a genuine tension: arbitrary new structure vs frozen LLM semantics
To encode a NEW arbitrary relational structure you must MOVE entity embeddings — but anchoring them to the
LLM prior (to keep semantics) fights that, and with few edges the learning is weak. So combining LLM prior
knowledge + newly-learned arbitrary structure in ONE entity space is hard: the two objectives conflict. The
honest resolutions (not yet demonstrated cleanly): (a) keep LLM entities frozen and learn a richer relation
OPERATOR (matrix) — needs more data (GEO-6 showed few-shot linear maps fail); (b) use SEPARATE stores —
LLM space for semantics + a trained structural space for new relations + memory for arbitrary facts, linked
by entity identity. The clean integration is an open engineering problem; the separate capabilities all
work (GEO-5–12).
