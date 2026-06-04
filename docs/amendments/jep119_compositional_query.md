# JEP-119 — compositional queries: compose relation + taxonomy reasoning (systematic generalization)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: "is what the dog chases an animal?" resolves the relation (dog chases cat) THEN the taxonomy (cat is-a
  animal) -> Yes; a false composition -> No; unknown relation -> "I don't know what the X Vs." The engine COMPOSES
  capabilities it was never explicitly built to combine. MOST-LIKELY MISS: the nested compositional-query parse.

## Acceptance
- PASS: compositional battery = 100%. Established (query composition over a KB), named; no novelty.

## Result — capability PASS; calibration MISS (the a/an bug recurred AGAIN)
First run 2/4: "is what the dog chases an animal?" -> No. Same a/an alternation bug (the optional `(?:a|an|the)?`
matched "a" inside "an", leaving "n animal" as the category). I have fixed this EXACT bug 5+ times (JEP-92/94/95/
100) and STILL wrote the bare buggy form in a fresh regex. Fixed -> 4/4. The engine composes relation-resolution +
IS-A for novel queries ("is what the dog chases an animal?" -> Yes). CALIBRATION: MISS (predicted generic nested-
parse risk; the actual bug was the recurring a/an alternation). DURABLE LESSON (escalated): NEVER hand-write a bare
optional-article regex; always use `(?:(?:an|a|the)\s+)?` (longest-first, required space). The fact that it
recurred proves a mental rule is insufficient — the safe form must be the ONLY form used. Tally 19/33. Established
(query composition), named; no novelty.
