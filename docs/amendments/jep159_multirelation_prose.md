# JEP-159 — multi-relation learn-from-prose: is-a + part-of + causal extracted, cross-relation reasoning

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 pattern extractors per relation hit different precisions on encyclopedic prose — is-a highest (~0.85, fixed
  'X is a Y'), part-of moderate (~0.75, 'has' ambiguous: 'has bark' property vs 'has a heart' part), causal lower/
  sparser (~0.7, varied phrasing) — and the engine composes correctly ACROSS relations wherever facts are correctly
  extracted (faculties sound), incl. the correct NON-composition (a heart is part-of an animal but is NOT an animal).
  MOST-LIKELY MISS: part-of/causal patterns more ambiguous than expected; or a cross-relation composition bug.

## Acceptance (characterization)
- Report per-relation extraction precision/recall vs known ground truth + cross-relation query correctness. Extending
  learn-from-prose to the engine's full relational repertoire is the finding. Established (pattern extraction, the
  engine's existing mereology/causal faculties JEP-141..150); named; no novelty.

## Result — MISS on the predicted mechanism; headline WORKS; a real bug fixed
### Extraction (after fixing a singularization bug)
| relation | precision | recall |
|----------|-----------|--------|
| is-a | 1.00 | 1.00 |
| part-of | 1.00 | 1.00 |
| causal | 1.00 | 1.00 |
Cross-relation reasoning: 8/8 (multi-hop is-a, multi-hop part-of, causal chain, AND correct NON-composition:
is_a(heart,animal)=False, is_a(engine,vehicle)=False, part_of(engine,vehicle)=False). 41/41 regression tests green.

### Honest calibration (MISS on mechanism + precisions)
I predicted an AMBIGUITY-driven precision spread (is-a ~0.85, part-of ~0.75, causal ~0.70). WRONG: on clean
controlled prose with fixed patterns there is NO ambiguity, so precision is uniformly 1.00. The apparent pre-fix
shortfall (is-a 0.83, causal 0.75) was NOT pattern ambiguity but a SINGULARIZATION BUG: _norm over-stripped
trailing -s from 'virus' -> 'viru' (and would mangle bus/lens/basis/species). FIX: _NOT_PLURAL exception set +
skip -ss/-us/-is endings in _norm (world/understanding.py). The bug was MASKED in cross-relation queries because the
mangling is consistent on store+query sides — it only surfaced against external ground truth (a real latent defect).
DURABLE LESSON: on CLEAN controlled prose don't predict pattern-ambiguity precision spreads (no ambiguity); predict
BUGS instead — the -s over-stripping family (now guarded). HEADLINE (right): multi-relation learn-from-prose +
cross-relation reasoning incl. correct non-composition WORKS — extends the positive learn-from-sources result to the
engine's full relational repertoire (is-a/part-of/causal, each with distinct correct semantics). Prediction MISS
(mechanism+precisions); tally 52/75. Established (pattern extraction + the engine's mereology/causal faculties); named.
