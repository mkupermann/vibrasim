# JEP-449 — Deploy affective memory into the live brain

## Motivation
JEP-448 proved affect-derived encoding weight makes emotional facts survive interference. JEP-449
wires it into the live `SubstrateMemory` / `Conversation` so a fact gains durability when its entity
carries strong valence — in BOTH storage orders (affect taught before OR after the fact). Established
(weighted VSA superposition; Cahill-McGaugh emotional memory), named. No transformer.

## Method (`world/substrate_memory.py`, `tools/run_jep449_live_affective_memory.py`)
- In `add_fact`, scale the first-experience binding by `1 + |valence[entity]|` (neutral entities
  unchanged, so existing tests/behaviour are untouched — the boost only fires when affect is taught).
- In `learn_valence`, reinforce the entity's ALREADY-stored facts by adding `|valence|·binding`
  energy (covers "X is evil" taught AFTER "X has horns").
- **Live test (via `Conversation`):** teach an emotional fact + a neutral fact, bury both under
  interference, and verify the emotional one is recalled when the neutral one is lost.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J449a (live affect enhances durability):** in a live Conversation under interference, the
  emotionally-tagged fact is recalled AND the matched neutral fact is NOT (emotional recall = 1,
  neutral recall = 0), both seeds.
- **J449b (no regression):** `tests/test_substrate_memory.py` + `tests/test_conversation.py` stay
  green (the boost is inert for neutral entities).
- **J449c (order-independent):** the boost works whether affect is taught BEFORE or AFTER the fact,
  both seeds.

Predicted PASS. NULL if J449a fails (the live boost is too weak at conversational scale). Bars locked;
no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | affect-first (emo / neu) | affect-after (emo / neu) |
|------|--------------------------|--------------------------|
| 0 | kept / lost | kept / lost |
| 7 | kept / lost | kept / lost |

J449a ✓ · J449c ✓ · **J449b ✓** (substrate_memory 14/14 + conversation 10/10 = 24/24 green) →
**PASS, both seeds.**

## Verdict: affective memory enhancement is live and order-independent
In the live store an emotionally-tagged fact (`dragon has fire`, valence −3) survives 300 interfering
facts and is recalled, while a matched neutral fact (`table has wood`) is lost — and this holds
whether the affect was taught BEFORE the fact (`add_fact` scales the binding by `1+|valence|`) or
AFTER it (`learn_valence` reinforces the entity's already-stored facts). The boost is inert for
neutral entities, so all prior behaviour is preserved (24/24 tests green). Michael's "strong-energy
connections grow stronger" is now a deployed capability of the conversational brain. Established
methods (weighted VSA superposition; emotional-memory enhancement), named — integration only, NOT new
science.
