# JEP-360 — The deep-structure boundary: passive ↔ active

## Motivation
The deepest induction test: if the system learns the PASSIVE "X was domesticated by Y", does it understand the
ACTIVE "Y domesticated X" (same relation, different structure)? I predict NO from induction alone — passive and
active are different templates with no shared surface structure; nothing makes the system infer one from the other
without linguistic/world knowledge. But teaching BOTH forms (each a separate template) handles both surface forms.
This maps exactly where structural generalisation stops without an LLM. No transformer.

## Method
Induce the passive template only; test an ACTIVE sentence (the wall). Then also induce the active template; test
both forms map to the SAME relation.

## Pre-registered PREDICTION + bars
Prediction: passive-only does NOT parse an active sentence (0.0 — the deep-structure wall); teaching BOTH templates
parses BOTH surface forms to the same relation (handling surface variation by learning each form, not by inferring).
- **J360a (the wall):** with only the passive template, an active sentence yields the right fact at 0.0, both seeds
  (0, 7).
- **J360b (route = learn each form):** with both passive and active templates taught, both a held-out passive AND a
  held-out active sentence yield the correct same-relation fact, ≥0.90, both seeds.

Conclusion either way is the finding: the substrate handles surface-form variety by LEARNING each form (composable,
teacher-coupled), and does NOT infer unseen structures — the honest ceiling of construction induction without an LLM.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J360a (the wall):** passive-only template fires on an ACTIVE sentence = **0**, both seeds — induction does NOT
  infer active from passive. **PASS** (the deep-structure wall).
- **J360b (route = learn each form):** with BOTH passive and active templates taught, a held-out passive AND a
  held-out active sentence both yield the correct same-relation fact = **1.0**, both seeds. **PASS.**

## Verdict: **PASS — the breakthrough boundary, fully mapped**
The deepest honest finding: construction induction does NOT do structural generalisation (passive↔active does not
emerge — that needs the linguistic/world knowledge an LLM absorbs). The substrate handles surface-form variety by
LEARNING EACH FORM (composable, teacher-coupled), not by inferring unseen structures. Combined with JEP-355
(function words abstract, generalise) and JEP-356 (synonyms need taught equivalence), the boundary is now precise:
**the substrate self-extends at the template level (with function-word abstraction); every deeper generalisation —
synonyms, structure — requires taught knowledge or learning each form. No deep abstraction emerges without an LLM.**
That is the honest, complete map of what learning-to-understand reaches under the no-LLM rule. No transformer.

