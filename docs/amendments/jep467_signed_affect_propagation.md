# JEP-467 — Affect propagates through SIGNED relations (Heider balance theory)

## Motivation
Affect currently inherits through is-a (JEP-451) but does not propagate through SIGNED relations. Michael's
vision is energies INTERACTING through relationships: the enemy of a good thing feels bad, the enemy of a
bad thing feels good ("the enemy of my enemy is my friend" — Heider's balance theory, 1946, signed social
networks). JEP-467 adds this: relations tagged with a sign (enemy/opposes/against → −1; friend/ally/likes
→ +1) propagate valence multiplicatively, including multi-hop sign products. New to the substrate,
grounded in an established theory (Heider), named.

## Method (`world/substrate_memory.py`, `world/conversation.py`, runner)
- Parse "X is a/an <enemy|rival|opponent|foe> of Y" → `(X, enemy_of, Y)`; "<friend|ally> of" → `(X,
  friend_of, Y)`. (`world/conversation.py`.)
- `SubstrateMemory.predict_valence`: order = own taught → inherited (is-a ancestor) → SIGNED-relation
  propagation (BFS over enemy_of/friend_of, valence = ∏signs × the target's valence, nearest valenced
  target) → gated energy fallback → None. (`_signed_valence`.)
- `brain_query` "is X good/bad?" routes through `predict_valence` (already does), so it picks up
  propagation automatically.

## Pre-registered PREDICTION + bars (BEFORE the run, via live Conversation)
- **J467a (enemy of good = bad):** "Heroes are good." + "A villain is an enemy of a hero." → "is a
  villain bad?" → yes (energy of villain dark), both seeds.
- **J467b (enemy of enemy = friend, multi-hop sign product):** + "A rebel is an enemy of a villain." →
  energy of a rebel is BRIGHT (−1 × −1 × good), both seeds.
- **J467c (no spurious propagation + suites green):** an unrelated concept with no signed path stays
  neutral; substrate_memory + conversation test suites pass.

PASS = affect propagates through signed relations with correct sign products (Heider balance) and does
not over-fire. NULL if J467a/b fail (propagation wrong) or J467c fails (spurious/regression). Bars
locked; no retuning. Established theory (Heider 1946), named — new substrate integration, not new
science. No transformer.

## RESULT (2026-06-05): **PASS** — Heider-balance affect propagation works

Both seeds, via live Conversation: "Heroes are good." + "A villain is an enemy of a hero." + "A rebel is
an enemy of a villain." + "A sidekick is a friend of a hero.":
- villain (enemy of good) → **dark (via relationships)**; "is a villain bad?" → **Yes**
- rebel (enemy of enemy of good) → **bright (via relationships)** — multi-hop sign product (−1·−1·+1)
- sidekick (friend of good) → **bright (via relationships)**
- table (no signed path) → **neutral** (no spurious propagation)

J467a ✓ · J467b ✓ · J467c ✓ (substrate_memory 14/14 + conversation 10/10 green) → **PASS, both seeds.**

## Verdict: energies now interact through relationships (a genuinely new substrate capability)
Affect propagates through SIGNED relations with correct sign products: enemy-of-good = bad,
enemy-of-enemy = friend, friend-of-good = good — Heider's balance theory (1946) realized in the
substrate. `predict_valence` order is now: own taught → inherited (is-a ancestor) → SIGNED-relation
propagation → gated statistical fallback → neutral; the energy query honestly tags the source
("(via relationships)" vs "(inherited from X)" vs "(generalized)"). This directly realizes Michael's
"energies interact through relationships" — a new capability for the substrate, grounded in an
established theory (Heider 1946), named. New integration, not new science. No transformer.
