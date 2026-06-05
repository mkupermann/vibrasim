# JEP-452 — Integrated capability audit: do all subsystems work together without interference?

## Motivation
This session added a complete affect/energy layer (predict, generalize, perceptual grounding, memory
enhancement, taxonomy inheritance) on top of the existing reasoning brain (multi-hop is-a, property
inheritance, exceptions, parts, attributes, abduction, abstention). They have never been exercised
TOGETHER in one coherent brain. JEP-452 teaches a single mini-world and runs a battery spanning ALL
capabilities at once, verifying they compose without cross-feature interference and without confident
falsehoods — a regression check and an honest capability snapshot. Established methods; integration
audit, no new science. No transformer.

## Method (`tools/run_jep452_integration_audit.py`)
Teach one coherent world (animal taxonomy + properties + an exception + parts + affect on a class +
an attribute + an emotional fact), then run a ~12-item battery covering: multi-hop is-a, property
inheritance, defeasible exception, part count, taught affect, INHERITED affect (+ explanation),
abstention on the untaught, an attribute, and emotional-fact survival under interference. Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J452a (capabilities compose):** ≥ 11/12 battery items correct, both seeds.
- **J452b (no confident falsehoods):** zero items where the brain asserts a FALSE answer (a wrong
  "Yes/No" or a fabricated value); permitted failure mode is honest abstention only, both seeds.
- **J452c (suites green):** `tests/test_substrate_memory.py` + `tests/test_conversation.py` pass.

Predicted PASS: the affect/energy layer composes cleanly with the reasoning brain. NULL if J452a < 11
(a phrasing or interference gap — report which) or J452b fails (a confident falsehood slipped in —
serious, report it). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL/partial — the audit caught a CONFIDENT FALSEHOOD

11/12 battery items pass on both seeds (multi-hop is-a, property inheritance, part count, taught
affect, INHERITED affect + explanation, attribute, direct is-a, negative is-a, abstention, emotional
recall all ✓). **J452a ✓ (≥11/12) but J452b ✗** — one confident falsehood:

> "can a penguin fly?" → **"Yes."** (should be No)

J452c (suites): green. → **NULL/partial** (a confident falsehood is a hard fail, correctly).

**Root cause (found).** The affect/energy layer composes cleanly — the failure is a PRE-EXISTING
normalization bug the audit surfaced. Storage:
- "Birds can fly" → `(bird, hasprop, fly)` ("can VERB" → property).
- "A penguin cannot fly" → `(penguin, cannot, fly)` — stored under a bogus `cannot` relation instead
  of `not_hasprop`.

So the defeasible-exception machinery (which overrides `hasprop` with `not_hasprop`, most-specific
wins — JEP-305/398) never fires, and the penguin inherits bird's `hasprop fly`. The query path is
correct; the negation normalization is wrong. **This is exactly what an integration audit is for** —
the energy work is sound; a latent reasoning bug (classic penguin example!) was hiding. Fixed in
JEP-453: normalize "X cannot/can't/can not VERB" → `(X, not_hasprop, VERB)` so the exception overrides.
Recorded NULL against locked bars; no retuning.

**Post-fix confirmation (after JEP-453):** the audit re-runs at **12/12, falsehoods=[]** on both seeds.
JEP-452's value stands as recorded — the audit CAUGHT a real latent falsehood the per-feature tests
missed; the NULL verdict is honest (it was NULL when it ran). The affect/energy layer is now verified
to compose cleanly with the reasoning brain.
