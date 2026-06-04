# JEP-95 — engine tier 4: COMMUNICATING in English (explain the reasoning, no transformer)

## Why (Michael: "human-like ... communicating with me")
The engine answered True/False; human-like communication EXPLAINS in English. Add explain(): render the answer
AND the inference chain as a natural sentence ("Yes. A poodle is a dog, a dog is an animal, an animal is a living
thing."). Template/grammar generation over the structured reasoning — substrate-legal, NO transformer.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100% on a generation battery (is-a true with chain, is-a false, relation true/false). MOST-LIKELY MISS: a/an
  article agreement IN GENERATION ("a animal" vs "an animal") — the SAME surface-form class, now in output. Per the
  logged meta-lesson, handle a/an (vowel-initial -> "an") explicitly from the start, in ONE helper used everywhere.
  Also verb agreement in output ("chases"). Predict 100%.

## Acceptance
- PASS: every generated answer is correct in content AND grammatical (article + verb agreement) = 100%.
- Established (template NL generation over a reasoning chain), named; no novelty. Honest: this COMMUNICATES the
  engine's reasoning in English on its domain; open-ended dialogue/generation remains the frontier.

## Calibration (after) — HIT (lesson applied proactively)
🔮 predicted 100% with a/an-in-generation as the risk; handled article agreement in ONE helper (_art) used
everywhere, from the start. ACTUAL 5/5 = 100%. HIT — the surface-form meta-lesson (JEP-94) was applied PROACTIVELY,
not after a miss. Tally 4/7; recent hits all come from anticipating the surface-form class.

## Result — PASS (100%)
The engine COMMUNICATES its reasoning in correct English:
- "is a poodle a living_thing?" -> "Yes. A poodle is a dog, a dog is an animal, an animal is a living thing."
- "is a poodle a fish?" -> "No. I was not told anything that makes a poodle a fish."
- "does the dog chase the cat?" -> "Yes, the dog chases the cat."
Content + article (a/an) + verb agreement all correct. A genuine step toward human-like COMMUNICATING (Michael's
goal): it explains WHY, not just yes/no, with NO transformer (template generation over the inference chain).
HONEST: domain-bound, scripted templates; open-ended dialogue/free generation remains the frontier. Established
(template NL generation), named; no novelty.
