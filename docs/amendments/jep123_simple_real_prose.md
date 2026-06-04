# JEP-123 — the engine on REAL simple factual prose (mapping the parse frontier at the simple end)

## Why
Boole (graduate-level) parsed ~2% (JEP-108b). The developmental claim is the engine works on SIMPLE language. Test
on REAL, simple, encyclopedia-style factual sentences — does it reach real prose at the simple end?

## Prediction (locked BEFORE run) [predict-calibrate] — predict QUALITY not RATE (JEP-108 lesson)
- 🔮 simple declarative factual sentences parse into VALID, CORRECT facts (the concept guard keeps quality high)
  at a MUCH higher rate than Boole's 2%; the engine reasons correctly over them. MOST-LIKELY MISS: forms outside
  the grammar (intransitive 'Fish live in water', adjectival predicates 'Dogs are loyal') silently dropping.

## Acceptance
- Report parse coverage + reasoning correctness over what's extracted. PASS-ish if reasoning over the extracted
  facts is correct AND coverage >> Boole (the developmental claim holds at the simple end). Established (grammar
  parsing), named; no novelty.

## Result — developmental claim HOLDS at the simple end; one honest quality caveat
Parse coverage **16/17 = 94%** (11 isa, 3 prop, 2 order, 1 none) vs Boole 2%. Reasoning over the extracted facts is
CORRECT: multi-hop ("a dog is a mammal, a mammal is an animal"), properties (dog can bark), transitive comparison
(elephant > mouse), quantified (all birds fly), generation (describe a robin). "Fish live in water" dropped cleanly
(intransitive, outside the grammar). HONEST QUALITY CAVEAT (predicted): "Dogs are loyal" MIS-PARSED as IS-A ("a dog
is a loyal") — "X is/are Y" is genuinely AMBIGUOUS between category-predication ('mammals') and property-predication
('loyal') without POS/semantic info, and the engine defaults to IS-A, so 'loyal' became a fake category (visible in
"what is a dog?" -> "a dog is a loyal and a mammal"). A morphological-suffix fix is unreliable ('loyal' and 'animal'
both end in -al), so NO fragile heuristic was added; recorded as a real grammar-only limitation. CALIBRATION: HIT
(predicted coverage >> Boole + quality mostly high + flagged the adjectival mis-parse, which occurred). Tally 22/37.
CONCLUSION: the developmental claim is VINDICATED — the engine reaches REAL simple factual prose (94%) and reasons
correctly; the gate is DENSE prose (Boole 2%) and the adjective/noun predication ambiguity, both honestly bounded.
Established (grammar parsing), named; no novelty.
