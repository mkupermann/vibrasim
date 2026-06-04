# GEO-2 — Inverses + multi-hop geometric reasoning (robustness of understanding)

## Result (grid, TransE trained on right/up only)
| test | hits@1 (chance ~0.028) |
|------|------------------------|
| INVERSE (left/down via −R, never trained) | 0.60 |
| 1-hop path | 0.60 |
| 2-hop | 0.55 |
| 3-hop | 0.47 |
| 4-hop | 0.51 |
| 5-hop | 0.38 |

**VERDICT: PASS** — inverses work untrained; multi-hop composition stays well above chance through 5 hops.

## Finding — geometric relational reasoning is robust
The learned space treats relations as transformations that INVERT (left = −right, never trained) and
COMPOSE over multi-step paths (graceful, slow decay, far above chance). Combined with GEO-1 (composition),
EQMOD-3's geometric substrate supports compositional relational reasoning — the structural core of
"understanding." Next: bridge to REAL semantics (geometric ML/LLM) — word/sentence embeddings + geometric
operations on the user's PC.
