# JEP-298 — Directed edges via permutation-protected binding → multi-hop inference works

## Motivation
JEP-297 NULL: commutative self-inverse Hadamard binding gives UNDIRECTED is-a edges, so transitive climbing
wanders into children. Fix (established — Kanerva permutation binding): store the parent **permuted**,
`fact = bind(child*ROLE, ρ(parent))`. Forward query recovers `ρ(parent)` then `ρ⁻¹` → clean parent; a backward
probe yields `ρ(x)·x`-type noise the cleanup rejects. `ρ` = circular shift (`np.roll`), non-commutative and
non-self-inverse — exactly the asymmetry direction needs. Added as `SubstrateMemory(directed=True)` so the
symmetric key→value path (JEP-294/295/296) is untouched.

## Pre-registered bars (BEFORE the run)
- **J298a (multi-hop correct):** with the JEP-297 depth-5 chain + distractors under DIRECTED binding,
  `is_a(poodle, organism)`=True, `is_a(poodle, fish)`=False, `is_a(dog, mammal)`=True, `is_a(rock, mammal)`=False
  — all four correct, both seeds (0, 7). (This is the exact set JEP-297 failed.)
- **J298b (directionality):** `query(organism, "isa")` returns NO confident parent (sim below the calibrated gate)
  — the child-retrieval that broke JEP-297 is gone; `query(poodle, "isa")` = dog (forward still clean). Both seeds.
- **J298c (persists):** save → load fresh → the four answers identical, both seeds.
- **No-regression:** JEP-296 (symmetric multi-module) still PASS under the modified code.

Predicted most-likely failure: the forward retrieval's extra `ρ⁻¹` step adds no noise, but if `ρ` interacts badly
with the bipolar `sign()` bundle the forward sim could drop below the gate (false "no"). If J298a fails on the
forward edges, report whether it's forward-sim collapse vs residual backward leakage.

## Result (seeds 0, 7): **PASS**
- **J298a:** `(is_a(poodle,organism), is_a(poodle,fish), is_a(dog,mammal), is_a(rock,mammal))` =
  **(True, False, True, False)** both seeds — the exact set JEP-297 got wrong. **PASS.**
- **J298b:** `query(organism, "isa")` sim = **0.008** (was 0.205 under symmetric binding) → below gate, rejected;
  `query(poodle, "isa")` = **dog** (forward still clean). The backward child-leak is gone. **PASS.**
- **J298c:** save → load fresh → answers identical **(True, False, True, False)** both seeds. **PASS.**
- **No-regression:** JEP-296 symmetric multi-module re-run still **PASS**. **PASS.**

## Verdict: **PASS**
Permutation-protected binding (`ρ` = `np.roll`, non-commutative) gives one-way is-a edges, so the substrate now
performs **transitive multi-hop inference over its persistent, growing memory** — answering "is a poodle an
organism?" by chaining four stored facts it was never told directly, and the reasoning survives close+reopen.
This closes the JEP-297 NULL with the established Kanerva fix (named as such, not novel). Arc complete:
store (294) → persist (295) → grow unbounded (296) → reason across hops (298).

