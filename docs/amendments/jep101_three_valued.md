# JEP-101 — three-valued comprehension: Yes / No / I-don't-know (epistemic humility)

## Why
A human distinguishes "no" from "I don't know". Add assess(x,c) -> yes/no/unknown: yes (path), no (explicit
negative OR category KNOWN but no path = closed-world over known concepts), unknown (category never heard of).
Sets up learning-through-dialogue (know what to ask).

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%. MOST-LIKELY MISS: the no/unknown boundary - deciding when a category is KNOWN (appears as child/parent/
  negative/prototype). Predicted edge: a leaf concept never used as a parent. Mitigated by _known_concepts() over
  all roles.

## Result — PASS (HIT)
Three-valued battery 6/6: assess(poodle,animal)=yes, (poodle,fish)=no [fish known], (whale,fish)=no [explicit
negative], (poodle,vegetable)=unknown [never heard of]. Natural responses: "I don't know whether a poodle is a
vegetable.", "No. A poodle is not a fish as far as I know.", "Yes. A poodle is a dog, a dog is an animal." HIT;
tally 8/13. The GATE caught a regression (the improved "No" wording broke JEP-95's hard-coded expected string -
capability intact, only the template changed; runner updated) - exactly why we gate. Established (open-world vs
closed-world reasoning, three-valued logic), named; no novelty. HONEST: closed-world over KNOWN concepts is a
heuristic (a human may still answer "no" to a known-impossible even if unstated); good enough for the dialogue tier.
