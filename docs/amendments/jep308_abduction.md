# JEP-308 — Abductive "why?" reasoning in the durable substrate (reverse causal lookup)

## Motivation
The engine answers "what could cause this?" — `abduce(cancer) → {smoking, radiation}` — by reverse causal lookup.
Directed binding stores cause→effect one-way (JEP-298), so the substrate can't reverse it directly. The
substrate-native fix: store the INVERSE relation explicitly (effect→caused_by→cause) and answer abduction with
`query_all(effect, "caused_by")`. Multi-cause via set-valued retrieval (JEP-303). No transformer.

## Method
Bridge each causal fact both ways: `add_fact(cause, "causes", effect)` AND `add_fact(effect, "caused_by", cause)`.
`abduce(effect)` = {c for (c, _) in `query_all(effect, "caused_by", gate)`}. Ground truth = engine `abduce`.

## Pre-registered bars (BEFORE the run)
- **J308a (abduction matches engine):** for every effect (incl. multi-cause: cancer←{smoking,radiation},
  headache←{poor diet,stress}), the substrate's abduced cause SET equals the engine's, exact-set accuracy ≥ 0.95,
  both seeds (0, 7).
- **J308b (no hallucinated cause + forward intact):** a non-effect (sunburn) abduces to ∅ (matches engine); the
  forward direction `contains(cause, "causes", effect)` still holds for all causal facts.
- **J308c (persists):** abduction identical after a fresh reload, both seeds.
- **No-regression:** JEP-307 (routed multi-hop at scale) still PASS.

Predicted most-likely failure: multi-word causes ("poor diet") as a single atom should be fine (any string →
`atom_vector`); the risk is a multi-cause effect whose two causes both sit just under the gate after superposition
— if J308a misses on multi-cause effects, report the cause-count at which set retrieval degrades (a fan-in
capacity finding), don't tune.

## Result (seeds 0, 7): **PASS**
- **J308a:** abduced cause SET == engine = **1.000** over 4 effects incl. multi-cause (cancer←{asbestos,
  radiation,smoking}, headache←{dehydration,poor diet,stress}, flooding←{heavy rain,storm}), both seeds. **PASS.**
- **J308b:** sunburn (non-effect) → ∅ matching engine; forward `contains(cause, causes, effect)` intact. **PASS.**
- **J308c:** identical after reload. **PASS.** **No-regression:** JEP-307 still PASS. **PASS.**

## Verdict: **PASS**
The substrate answers "why? / what could cause this?" by reverse lookup over a stored INVERSE relation
(effect→caused_by→cause) + set-valued retrieval — matching the engine, multi-cause included, durably. The
prediction held: multi-word causes ("poor diet", "heavy rain") work as single atoms, and fan-in up to 3 causes
stayed cleanly above the gate. (Cosmetic: engine lemmatizes "asbestos"→"asbesto"; the substrate faithfully mirrors
whatever the engine stored.)

