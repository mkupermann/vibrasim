# Pattern: building a capability engine developmentally, with predict-calibrate (JEP-92..107)

How the EQMOD-4 understanding engine (world/understanding.py) was built — the METHOD, which is the transferable
output, not the toy domain. A 100%-working engine on simple input, grown one tier at a time, each gated.

## The method
1. **Consolidate proven pieces into ONE tested module**, then grow it. Scattered experiment scripts become a
   single engine + a regression suite (tests/) that locks every capability.
2. **One capability tier at a time, each held at 100%** on its target domain. Don't add tier N+1 until tier N is
   green. Tiers here: parse->ground->bind->infer -> Boolean -> parse-robustness -> communicate -> learn-by-
   correction -> learn-from-examples -> multi-word -> WH-questions -> three-valued -> dialogue-learning -> DAG ->
   induction -> coreference.
3. **Predict before every run** (the predict-calibrate skill): write the expected outcome AND the single most-
   likely failure mode, THEN run, THEN diagnose every miss into a checkable lesson. Calibration ~10/18 — the value
   is the diagnosed misses, not the hit-rate (you keep entering new territory with new failure modes).
4. **Gate every commit on a green test run.** (Learned the hard way: JEP-98 committed a failing test by chaining
   git after pytest unconditionally. Never again.)
5. **Demos find what unit tests assume away.** The dialogue demo found a Boolean-routing gap (JEP-106); the
   "living thing" demo found multi-word parsing (JEP-98). Exercise on NATURAL/INTEGRATED input, not the test-
   friendly encoding.

## The recurring bug families (predict THESE first)
- **Surface-form classes**: article a/an is PHONETIC not orthographic (a unicorn, an hour — 3 sub-forms across
  alternation/generation/phonetics); noun plurals; verb agreement (chase/chases). Handle each in ONE normalizer.
- **Propagate every fix to EVERY parser**: a fix in the fact-parser but not the question-parser is not a fix
  (recurred JEP-94, 99). Grep for all sites.
- **A data-structure TYPE change breaks EVERY reader**: changing parents str->set broke tests/runners that read it
  (JEP-104). Grep all readers (logic + tests + runners) before predicting green.
- **Defeasible reasoning must SURVIVE exceptions**, not be blocked by them (JEP-105: a counterexample should
  override per-instance, not cancel the general rule).
- **Predicted boundaries that don't materialize in-scope** (JEP-76 permutation, JEP-107 coreference): the failure
  you predict may need syntax/structure your domain doesn't produce — then it's out-of-scope, not a live bug.

## Honest scope discipline
Every tier states what it does NOT cover. The engine is 100% on simple-to-natural controlled language; the frontier
(real-prose parse JEP-89, unsupervised structure JEP-69/70, open generation, rich grounding) is named, not crossed.
Boole is the final exam, not the primer. All methods established and named; the engine claims no novelty - the
transferable output is the working foundation + this disciplined method.
