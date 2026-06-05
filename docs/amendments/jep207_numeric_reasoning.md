# JEP-207 — quantitative reasoning: numeric attributes from prose + 'how many' Q&A + numeric comparison

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine can extract numeric attribute facts ('X has N Y') from prose and answer 'how many Y does X have?' +
  numeric comparisons. RISK: number parsing (digits vs words) and attribute extraction guarding.

## Result — PASS (HIT)
Added quantitative reasoning, a genuinely-distinct new capability domain (the engine previously had NO numbers):
- read() detects 'X has N Y' (N a digit '4' or a number-word 'eight', via _parse_num) BEFORE the has-part pattern,
  storing a numeric attribute self.num_attrs[(entity, attribute)] = N — so 'A dog has 4 legs' is a QUANTITY, not a
  part-of '4 leg' (the prior mis-parse, now fixed). 'A dog has 4 legs. A spider has eight legs. A bird has 2 wings.'
  -> num_attrs {(dog,leg):4, (spider,leg):8, (bird,wing):2}; 'A heart is part of a dog' still part-of (no interference).
- respond() answers: 'how many legs does a dog have?' -> 'A dog has 4 legs.'; 'how many legs does a spider have?' ->
  'A spider has 8 legs.' (word 'eight' parsed); 'does a spider have more legs than a dog?' -> 'Yes.' (8>4); reverse
  -> 'No.'; unknown -> 'I don't know how many legs a cat has.'
So the engine now understands and reasons about QUANTITIES from prose — counting attributes and comparing them.
HONEST LIMIT: the simple 'X has N Y' pattern + small number lexicon (0-20 + digits); complex quantitative prose
(ranges, units, arithmetic, 'millions') is out of scope. 75/75 regression tests green (+1). Prediction HIT; tally
96/123. Established (numeric attribute extraction, quantitative comparison); named; no novelty.
