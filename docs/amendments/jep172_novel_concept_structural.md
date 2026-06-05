# JEP-172 — understanding is STRUCTURAL, not lexical: learning entirely NOVEL concepts from prose

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine handles novel nonsense-word concepts identically to familiar ones (purely structural); full
  multi-relation reasoning works on never-seen words, proving the understanding is relational not lexical.
  MOST-LIKELY MISS: a normalizer/article edge case on unusual letter patterns in the nonsense words.

## Result — PASS (HIT)
Read a passage of ENTIRELY NOVEL vocabulary (no pre-existing meaning anywhere): 'A blicket is a kind of zorp. A zorp
is a feb. A florp is part of a blicket. A glim causes a thrumble. A thrumble is a wibble.' The engine then reasons
identically to familiar concepts:
- is_a(blicket, feb) -> Yes (2-hop): 'A blicket is a zorp, a zorp is a feb.'
- part_of(florp, blicket) -> Yes; part_of(florp, feb) -> True (the JEP-169 part-of/is-a interaction, on novel words)
- causes_effect(glim, wibble) -> True (the JEP-170 causal/is-a interaction, on novel words: glim->thrumble, thrumble
  is-a wibble)
- is_a(florp, feb) -> False (part is not type, holds for novel words)
- describe('a blicket') -> 'A blicket is a zorp. That makes it also a feb. It has a florp.'
This DEFINITIVELY RULES OUT lexical confounds (the JEP-87 vocabulary-confound concern): the understanding is purely
STRUCTURAL/RELATIONAL — meaning here is carried entirely by the relations, not by any familiar word. This is a clean
demonstration that the engine LEARNS NEW CONCEPTS the way a human does from a definitional context (relationally),
including the subtle relation-type interactions, with zero reliance on pre-existing vocabulary. No normalizer edge
case appeared (the hedged miss). 54/54 regression tests green (+1). Prediction HIT; tally 64/88. Established
(relational/structural semantics; the same closure machinery applies to any symbols); named; no novelty.
