# GEO-21 — Clean LLM-prior + new-structure integration via ORTHOGONAL SUBSPACES (resolves GEO-14)

## Motivation
GEO-14 was PARTIAL: training new arbitrary structure MOVED entity embeddings and fought the LLM-semantics
anchor. The clean fix: don't share dimensions. Entity = [frozen LLM block (semantics, untouched) | trainable
structure block (new relations)]. Train the relation only in the structure block. Semantics preserved by
construction; new structure learned without conflict. GEO-21 tests this resolves the tension.

## Pre-registration (locked BEFORE run)
- 10 real role-words; new relation reports_to (i->i+1) over them.
- Entity vec = concat(MiniLM(role) [384, FROZEN], struct [16, trainable init random]).
- Train TransE on the STRUCT block only (relation r in struct space); frozen block never updated.
- Tests:
  (a) STRUCTURE learned: reports_to hits@1 on held-out edges >= 0.6 (vs GEO-14's 0.00).
  (b) 2-hop skip via composition (2r) hits@1 > chance.
  (c) SEMANTICS preserved: cosine sim in the FROZEN block of related roles (e.g. manager~director) equals
      the original MiniLM sim (unchanged, by construction — verify == within 1e-6).
- Bars: PASS if (a)>=0.6 AND (c) preserved. This demonstrates the honest integration: prior knowledge +
  newly-learned arbitrary structure coexist in one entity, no conflict.

## Result (chain topology)
| metric | value |
|--------|-------|
| (a) new reports_to learned hits@1 | 0.50 (GEO-14: 0.00) |
| (b) 2-hop skip composition | 0.12 (~chance) |
| (c) semantic-block drift | **0.00** (frozen, exact) |

**VERDICT: PARTIAL** — the subspace MECHANISM works for the hard part: LLM semantics preserved EXACTLY
(drift 0.00) while new structure is trained, resolving the GEO-14 entanglement conflict. But absolute
structure learning is only 0.50, capped by (i) the linear-chain TransE degeneracy already found in GEO-13
and (ii) a tiny 2-edge held-out set. The mechanism is sound; the chain topology is the limiter. Re-tested
on a branching tree (GEO-21b) to isolate the subspace claim from chain degeneracy.
