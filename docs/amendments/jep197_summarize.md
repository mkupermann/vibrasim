# JEP-197 — summarize() read knowledge (source summarization, generative communication)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a summarize() method generates a coherent multi-sentence overview of read knowledge (top categories, key
  relations) — genuine source summarization, distinct from per-concept describe(). RISK: coherence/selection.

## Result — PASS (HIT)
Added summarize(): finds the top categories (taxonomy roots, ranked by how many things fall under them) and the main
part-of / causal structure, and generates a coherent overview of the WHOLE knowledge base (not a single concept).
After reading a multi-relation passage:
  'I learned about an animal. Things like a bird and a mammal are kinds of animal. Some things have parts — for
   example, a heart is part of a dog. And some things cause others — for example, a virus causes a fever.'
Empty engine -> 'I haven't learned anything yet.' This is a genuine SOURCE-SUMMARIZATION communication capability —
after reading a source, the engine can give a coherent spoken overview of what it learned (the dominant categories,
the kinds of structure present), directly serving 'communicating WITH me'. Complements per-concept describe() (one
concept's profile) with a whole-source overview. Fixed a plural-agreement template artifact ('are an animal' ->
'are kinds of animal'). 66/66 regression tests green (+1). Prediction HIT; tally 86/113. Established (template NL
generation / extractive-structural summarization); named; no novelty.
