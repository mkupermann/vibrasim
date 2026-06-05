# JEP-322 — A unified query interface over the durable brain (+ CLI)

## Motivation
The reasoning operations (JEP-298..321) each have their own call shape. Consolidate them behind ONE interface,
`world/brain_query.BrainQuery`, that wraps a loaded `SubstrateMemory`, auto-calibrates the gate once, and answers
the common question types — is-a (multi-hop, DAG, with negation/exception), has-property (defeasible inheritance),
why/abduction, and "what does X VERB" (open relation) — plus a tiny string parser so a persisted brain can be ASKED
questions from a CLI (`tools/ask_brain.py`). Makes the whole durable-reasoning stack usable end-user. No transformer.

## Pre-registered bars (BEFORE the run)
- **J322a (interface correctness):** on a persisted store reloaded fresh, `BrainQuery` answers a mixed question set
  (is-a multi-hop incl. negative, defeasible property incl. exception, abduction, open relation) matching ground
  truth ≥ 0.95, both seeds (0, 7).
- **J322b (string parser):** parses and correctly answers the natural forms "is a poodle an animal?",
  "can a penguin fly?", "what causes cancer?", "what does a cat eat?" — ≥ 0.95.
- **J322c (CLI + persistence):** `tools/ask_brain.py` imports and answers from a saved brain folder (no shared RAM).
- **No-regression:** the substrate test gate (`tests/test_substrate_memory.py`) still green; new BrainQuery tests added.

Predicted most-likely failure: the single auto-gate may not fit every relation's fan-out simultaneously (per JEP-300
it did at small scale); if one question type misses, report which relation's gate was off — don't hand-tune.

## Result (seeds 0, 7): **PASS** (after a surface-form fix)
- **J322a:** interface answers (is-a multi-hop incl. negative, defeasible property incl. exception, abduction,
  open relation) = **1.0**, both seeds. **PASS.**
- **J322b:** string parser — **first cut 0.83** (5/6): "what does a cat **eat**?" missed because the stored relation
  is "**eats**" (calibration lesson #1, surface form). Fixed `what()` to try morphological variants (eat→eats).
  → **1.0**, both seeds. **PASS.**
- **J322c:** `tools/ask_brain.py` imports AND answers end-to-end from a saved brain folder
  ("is a poodle an animal?"→True; "what causes cancer?"→['smoking']). **PASS.**
- **No-regression:** substrate gate now 10 tests (added BrainQuery), all green.

## Verdict: **PASS**
One interface (`BrainQuery`) answers is-a / property / why / what over the durable brain, auto-calibrating the gate,
with a natural-question parser and a CLI — so a persisted, taught brain can be ASKED questions directly. Makes the
whole durable-reasoning stack usable. Honest note: the parser handles a fixed set of question templates + simple
verb morphology; richer NL parsing is the Understanding Engine's job (this routes to substrate ops). No transformer.

