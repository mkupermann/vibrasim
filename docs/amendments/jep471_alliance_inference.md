# JEP-471 — Inferred alliances: "the enemy of my friend is my enemy" (signed-path reasoning)

## Motivation
JEP-467/469 gave the substrate signed affect relations and showed 2-camp structure. Deploy it as a
usable capability: INFER the alignment between two concepts through the signed-relation chain, even when
not directly stated — "the enemy of my friend is my enemy", "the enemy of my enemy is my friend". The
alignment is the PRODUCT of edge signs along the path (Heider transitivity).

## Method (`world/substrate_memory.py`, `world/brain_query.py`, runner)
- `SubstrateMemory._alignment(x, y)`: BFS over signed relations (enemy_of=−1, friend_of=+1) from x; the
  first path reaching y returns the product of its edge signs (+1 = ally/same side, −1 = enemy/opposite).
  None if no signed path.
- `brain_query`: "is X an ally of Y?" / "is X on the same side as Y?" → alignment > 0; "is X an enemy of
  Y?" → alignment < 0. (Direct stored facts still answer first; this adds the INFERRED chain.)

## Pre-registered PREDICTION + bars (BEFORE the run, via live Conversation)
World: "A villain is an enemy of a hero." + "A rebel is an enemy of a villain." + "A knight is a friend of
a hero." + "A spy is a friend of a villain."
- **J471a (enemy of enemy = ally, inferred):** "is a rebel an ally of a hero?" → yes (rebel→villain→hero,
  −1·−1 = +1), both seeds.
- **J471b (friend of enemy = enemy, inferred):** "is a spy an enemy of a hero?" → yes (spy→villain→hero,
  +1·−1 = −1), both seeds; and "is a knight an ally of a hero?" → yes.
- **J471c (no spurious + suites green):** "is a table an ally of a hero?" → no/abstain; substrate_memory
  + conversation suites pass.

PASS = the brain infers alliances/enmities through signed chains (Heider transitivity). NULL if the
inference is wrong or over-fires. Bars locked; no retuning. Established theory (Heider 1946), named; new
substrate integration, not new science. No transformer.

## RESULT (2026-06-05): **PASS** — alliances/enmities inferred through signed chains

Both seeds, via live Conversation: "is a rebel an ally of a hero?" → **Yes** (rebel→villain→hero,
−1·−1=+1); "is a spy an enemy of a hero?" → **Yes** (spy→villain→hero, +1·−1=−1); "is a knight an ally
of a hero?" → **Yes** (direct friend); "is a table an ally of a hero?" → **No** (no signed path).

J471a ✓ · J471b ✓ · J471c ✓ (substrate_memory 14/14 + conversation 10/10 green) → **PASS, both seeds.**

## Verdict: Heider transitivity deployed as a usable capability
`SubstrateMemory._alignment(x, y)` returns the signed-path product between two concepts; `brain_query`
answers "is X an ally/enemy of Y?" / "is X on the same side as Y?" by inferring through the chain — "the
enemy of my enemy is my ally", "the friend of my enemy is my enemy" — even when the relationship was
never directly stated. This deploys the relational-affect graph (JEP-467/469) into usable alliance
reasoning, live in the GUI. Established theory (Heider 1946 transitivity), named; new substrate
integration, not new science. No transformer.
