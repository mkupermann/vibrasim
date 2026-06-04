# JEP-116 — cross-situational word grounding (meaning WITHOUT clean labels), the symbol-grounding mechanism

## Why
JEP-114 named clusters with explicit labels. Human word learning is CROSS-SITUATIONAL (Yu & Smith 2007): a word
co-occurs with its referent across many scenes amid referential ambiguity (other objects/words present); the
consistent statistics align word<->concept with NO clean "this is a dog" labels. Test it as the grounding bridge.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 >=0.8 of concepts correctly named: across many scenes (1-2 present objects, names + DISTRACTOR words),
  co-occurrence PMI aligns each cluster to its true name despite per-scene ambiguity; a never-labeled instance is
  then named correctly. MOST-LIKELY MISS: high ambiguity (many distractors) drowning the signal.

## Acceptance
- PASS: >=0.8 cluster->word naming accuracy via cross-situational stats (no explicit labels), then the engine
  reasons with the learned names. Established (cross-situational word learning, Yu-Smith 2007; PMI), named; no novelty.

## Result — PASS (HIT)
600 ambiguous scenes (1-2 objects, names + distractor words like 'blicket'/'wug'): cross-situational PMI named
all 5 clusters correctly (1.00) with NO clean labels; a never-labeled perceived instance grounded to 'dog' and
reasoned about (is_a animal = True). Prediction HIT; tally 18/28. This completes a mostly-UNSUPERVISED grounding
pipeline: perceive -> cluster (STRUCTURE, JEP-113) -> cross-situational word learning (MEANING, this) -> named
taxonomy -> reason (engine). Bridges structure->meaning WITHOUT explicit labels (vs JEP-114 which needed them).
HONEST BOUNDS: needs many scenes + name-referent co-occurrence above the ambiguity; high ambiguity / synonymy /
polysemy degrade it; perception here is easy (well-separated prototypes); word forms remain arbitrary tokens, not
deep semantics. Established (cross-situational word learning, Yu & Smith 2007; PMI), named; no novelty. The residual
frontier: grounding in the HARD perceptual regime (overlapping concepts), polysemy/synonymy, and abstract words
with no perceptual referent.
