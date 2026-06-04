# JEP-117 — the fully self-taught engine: concepts, names, taxonomy from observation + ambient language (NO told facts)

## Why (toward human-like LEARNING from experience, not telling)
Capstone of the grounding thread: integrate structure-discovery (JEP-113 clustering) + cross-situational naming
(JEP-116) so the engine learns its ENTIRE named taxonomy from raw observation + ambient words, with ZERO tell() of
any explicit fact, then reasons with grounded words.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 >=0.8 end-to-end: observe instances with ambient sub- (dog) and super-class (animal) words; cluster at 2
  granularities; cross-situationally name both levels; wire IS-A from the cluster hierarchy; a never-labeled
  instance answers "is it an animal?" correctly. NO told facts. MOST-LIKELY MISS: superclass naming (heard less,
  more ambiguous) or the hierarchy->IS-A mapping.

## Acceptance
- PASS: >=0.8 of held-out instances correctly is-a their (learned) superclass, entirely self-taught. Established
  (clustering + cross-situational learning), named; no novelty. HONEST: needs ambient language at both
  granularities + clean-ish clusters; the hard perceptual/linguistic regimes remain the frontier.

## Result — PASS (HIT) — the learning-from-experience capstone
With NO tell() of any explicit fact, learned from observation + ambient language: sub-names (dog/cat/robin/eagle)
1.00, super-names (mammal/bird) 1.00, self-taught is-a-superclass 1.00; the engine then describes: "A dog is a
mammal." (learned, never told). Prediction HIT; tally 19/29; streak 116-117. The full pipeline is self-supervised:
perceive -> cluster (STRUCTURE) -> cross-situational naming (MEANING) -> wire taxonomy -> reason/describe. This is
the most "human-like learning from experience" demonstration of the programme: the engine builds its OWN named
conceptual structure from raw perception + ambient words, then reasons and communicates over it. HONEST BOUNDS:
favorable regime — clean-ish clusters (JEP-54 condition), ambient language at BOTH granularities (superclass words
heard 60% of scenes are the weak point), no synonymy/polysemy. The hard regimes (overlapping concepts, polysemy,
abstract words with no perceptual referent, relations beyond IS-A, real prose) remain the open frontier. Established
(agglomerative clustering + cross-situational word learning), named; no novelty.
