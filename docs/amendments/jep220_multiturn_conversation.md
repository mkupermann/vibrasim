# JEP-220 — multi-turn conversation regression guard (the conversational features compose across turns)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a multi-turn conversation (ask across domains, 'why?', 'what about X?') composes correctly across turns — a
  permanent guard. RISK: a recency-tracking interaction across turns.

## Result — PASS (HIT)
test_multiturn_conversation verifies a realistic multi-turn dialogue composes:
- 'is a dog an animal?' -> 'Yes. A dog is a mammal, a mammal is an animal.'
- 'what about a cat?' -> 'Yes, a cat is an animal too.' (follow-up CONTEXT, reusing the 'animal' category)
- 'why?' -> 'Because a cat is a mammal, and a mammal is an animal.' (why of the FOLLOW-UP, correct recency)
- 'is an elephant bigger than a cat?' -> 'Yes.' (switch to the comparison domain)
- 'why?' -> 'Because an elephant is bigger than a dog, and a dog is bigger than a cat.' (ORDER why, recency updated)
- 'what are all the mammals?' -> 'A cat and a dog.' (enumeration still works)
The recency tracking (`_last_query` / `_last_rel_query`) is updated correctly at each turn so 'why?' and 'what about'
always refer to the MOST RECENT relevant query across domains. A permanent guard for the conversational ability
(follow-up context + why-across-all-chains + multi-domain Q&A composing across turns). NOTE: the initial run failed
on MY OWN test assertion ('count(",") >= 1' — but a 2-item list joins as 'A cat and a dog' with NO comma); fixed the
assertion to membership (the engine was correct). 87/87 regression tests green (+1). Prediction HIT; tally 109/136.
Established (dialogue-context regression testing); named; no novelty.
