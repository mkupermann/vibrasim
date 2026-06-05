# JEP-468 — Affective ambivalence: detect conflicting energy (Heider imbalance)

## Motivation
JEP-467 propagates affect through signed relations. Heider's theory also says a node reachable as BOTH
positive and negative (e.g., a friend of a hero AND a friend of a villain) sits in an IMBALANCED, tense
position — real ambivalence / cognitive dissonance. JEP-468 adds detection of this conflicting energy: a
new, theory-grounded capability that ties to the substrate's existing contradiction handling.

## Method (`world/substrate_memory.py`, `world/brain_query.py`, runner)
- `SubstrateMemory._signed_valence_set(entity)`: BFS over signed relations collecting ALL reachable
  propagated valences (sign-product × each valenced target). Returns the set of signs reached.
- A concept is AMBIVALENT iff that set contains both +1 and −1.
- `brain_query`: "does X feel conflicted?" / "is X conflicted?" → yes iff ambivalent. `predict_valence`
  is unchanged (returns the nearest path); ambivalence is a separate query.

## Pre-registered PREDICTION + bars (BEFORE the run, via live Conversation)
- **J468a (ambivalence detected):** "Heroes are good." + "Villains are evil." + "A spy is a friend of a
  hero." + "A spy is a friend of a villain." → "is a spy conflicted?" → yes, both seeds.
- **J468b (no false ambivalence):** a concept with only same-sign paths (e.g., a sidekick, friend of a
  hero only) is NOT conflicted, both seeds.
- **J468c (no regression):** substrate_memory + conversation suites pass; JEP-467 propagation still
  correct (villain dark, rebel bright).

PASS = the brain detects conflicting energy (Heider imbalance) and does not over-fire. NULL if J468a
fails (ambivalence missed) or J468b/c fail (false positive / regression). Bars locked; no retuning.
Established theory (Heider 1946), named — new substrate integration, not new science. No transformer.

## RESULT (2026-06-05): **PASS** — conflicting energy detected (Heider imbalance)

Both seeds, via live Conversation (spy is a friend of a hero AND a friend of a villain):
- "is a spy conflicted?" → **Yes** (reachable as both + and −)
- "is a sidekick conflicted?" (friend of a hero only) → **No**; "is a villain conflicted?" → **No**
- propagation intact: villain → dark, sidekick → bright (via relationships)

J468a ✓ · J468b ✓ · J468c ✓ (substrate_memory 14/14 + conversation 10/10 green) → **PASS, both seeds.**

## Verdict: the affect system now models ambivalence
`SubstrateMemory._signed_valence_set` collects all valences reachable through signed relations;
`is_ambivalent` flags a concept reachable as BOTH positive and negative — Heider's imbalanced/tense
position (cognitive dissonance). "is/does X (feel) conflicted/ambivalent/torn?" answers it. Combined with
JEP-467, the energy model now has FIVE affect modes: taught, inherited (is-a), signed-propagated
(Heider), statistically generalized, and AMBIVALENCE detection — a rich, theory-grounded realization of
Michael's "energies interact through relationships". Established theory (Heider 1946), named; new
substrate integration, not new science. No transformer.
