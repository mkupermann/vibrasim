# JEP-111 — "why?" follow-up questions (conversational context + justification)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: "why?" after a yes-answer gives the reasoning chain ("Because a poodle is a dog, and a dog is an
  animal."); after no/unknown explains the absence; "why?" with no prior question says so. MOST-LIKELY MISS:
  tracking the last query across respond/explain calls, or the chain phrasing.

## Acceptance
- PASS: why-question battery = 100%. Established (dialogue state + explanation), named; no novelty.

## Result — PASS (HIT)
Why battery 4/4: no-prior -> "You haven't asked me a question I can justify yet."; after yes -> "Because a poodle
is a dog, and a dog is an animal, and an animal is a living thing."; after unknown -> "Because I was never told
whether a poodle is a vegetable."; after no -> "Because nothing I was told makes a poodle a fish." Prediction HIT;
tally 14/23; 22 tests gated green. The engine maintains dialogue context (_last_query) and justifies its answers -
conversational understanding. Established (dialogue state + explanation), named; no novelty.
