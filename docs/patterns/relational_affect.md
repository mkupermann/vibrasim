# Pattern — Relational affect (signed-relation valence propagation + balance)

**Surfaced:** JEP-467/468/469 (2026-06-05). **Status:** built, live in the GUI, tested.

## The mechanism
Affect is not only a per-concept scalar — it FLOWS through relationships and creates structure. Built on
the energy-cloud valence (`[[affective_energy_generalization]]`), with no transformer:

1. **Signed relations.** Relations carry a sign: `enemy_of` = −1, `friend_of` = +1 (parsed from "X is a/an
   enemy/friend of Y"). Established: Heider's balance theory (1946).
2. **Valence propagation** (`SubstrateMemory._signed_valence`). BFS to the nearest valenced target;
   valence = ∏(edge signs) × target valence. So enemy-of-good = bad, **enemy-of-enemy-of-good = good**
   (multi-hop sign product). Slots into `predict_valence` after own-taught and is-a inheritance, before
   the statistical fallback. The energy query honestly tags the source: "(via relationships)".
3. **Ambivalence** (`_signed_valence_set` / `is_ambivalent`). A concept reachable as BOTH + and − is in
   Heider's imbalanced/tense position — "conflicting energy". Queried by "is X conflicted?".
4. **Emergent group structure.** A signed-affect network driven toward balance (greedy de-frustration:
   flip the most-frustrating edge) self-organizes into TWO antagonistic camps — the Cartwright-Harary
   structure theorem (1956), demonstrated (JEP-469: 110 imbalanced triads → 0, perfect 2-clustering).

## The full affect stack (five modes)
`predict_valence` resolves affect in priority order, each honestly tagged: **taught** → **inherited**
(is-a ancestor) → **propagated** (signed relations, this pattern) → **generalized** (statistical, gated
to avoid hallucination) → neutral; plus **ambivalence** detection as a separate query.

## Honest scope
All established theory (Heider 1946; Cartwright-Harary 1956) and methods (graph BFS, sign products),
named — the contribution is the substrate-native integration that realizes Michael's "energies interact
through relationships", from individual valence up to emergent collective structure. NOT new science.
The WEAK-balance / multi-faction regime (Davis 1967) is a different objective (allow all-negative triads)
and was NOT built — flagged as out-of-core social-network theory (JEP-470).

## Reuse
Any time a graded property should flow through typed/signed relations (affect, trust, alignment,
reward-shaping over a relation graph), this is the shape: tag relations with a sign, propagate the
product to the nearest grounded source, detect conflicting paths, and (optionally) drive toward balance
for emergent grouping. Never dress the established theory as novel.
