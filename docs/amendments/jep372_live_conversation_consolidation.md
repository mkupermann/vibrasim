# JEP-372 — End-to-end: the live Conversation auto-consolidates so deep questions are reliable

## Motivation
JEP-370/371 proved closure consolidation removes the within-domain deep-reasoning ceiling and shipped it to the durable
store. The last mile is the conversational brain Michael actually talks to: after reading a document (`read_text`), the
live `Conversation` should auto-consolidate so that DEEP questions ("is a poodle an animal?" across a long taxonomy)
are answered reliably through the normal `say()` path — not just in a harness. This wires it end-to-end and proves the
deployed talk loop benefits. No transformer.

## Method
Add `Conversation.consolidate()` (replaces `self.sm` with its closure-consolidated copy, same pattern as `compact()`
in `save()`), and auto-call it at the end of `read_text` when the read added is-a structure. Build a deep taxonomy as
a document, read it via `read_text`, then ask deep is-a questions through `Conversation.say()` and compare a control
Conversation (same facts, consolidation disabled) to the auto-consolidated one. Verify persistence (save→load keeps
the consolidated edges) and no regression in the conversation test suite.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: the auto-consolidated live brain answers deep is-a questions correctly at ≥0.95 where the un-consolidated
control is materially worse, exceptions are still respected, the consolidated store persists across save/load, and the
conversation suite stays green.

- **J372a (deep questions via say()):** through `Conversation.say()`, deep is-a questions on a ~300-fact taxonomy are
  answered correctly ≥0.95 after auto-consolidation, AND ≥ the un-consolidated control accuracy, both seeds (0, 7).
- **J372b (exceptions + negatives intact):** a "not" exception taught into the conversation is still respected after
  consolidation (no false ancestor bridged), and a non-ancestor question answers "no", both seeds.
- **J372c (persists + no regression):** save→load preserves the consolidated edges (deep question still ≥0.95 after
  reload); `pytest -m "not slow" tests/test_conversation.py` passes.

If the control already answers ≥0.95 (small/shallow read), J372a's ">= control" still holds but the benefit is small —
report the honest delta. If auto-consolidation breaks any conversation test, that is a real integration bug — fix it,
don't tune the bar. No transformer.

## Result (seeds 0, 7): **PARTIAL** (end-to-end deep reliability + persistence PASS; a dimension interaction surfaced)
- **J372a (deep questions via say()): PASS** — through the normal `Conversation.say()` path, deep is-a questions on a
  ~300-node taxonomy read via `read_text` are answered **1.0 / 1.0** after auto-consolidation, vs control (auto-
  consolidation disabled) **0.9 / 0.933**. Auto-consolidation measurably lifts deep reliability end-to-end. Both seeds.
- **J372c (persists + no regression): PASS** — after save→load the deep accuracy is still **1.0 / 1.0** (consolidated
  edges persist through the durable store), and `tests/test_conversation.py` is **10 passed**. Both seeds.
- **J372b (exceptions + negatives): PARTIAL** — exceptions are respected (a taught `not`-is-a is still answered "no"
  after consolidation, both seeds), but **negative-probe accuracy is 1.0 (seed 7) / 0.8 (seed 0)** — below the 0.90
  bar on seed 0. Diagnosis: consolidation multiplies stored edges ~6× (300 → ~1900 facts), and the live
  `Conversation` uses the **default vector dimension**, so cleanup crosstalk rises and ~20% of non-ancestor is-a
  probes false-positive on one seed. This is the storage↔dimension interaction that JEP-370/371 avoided by using
  D=8192; the deployed `Conversation` does not scale D with load.

## Verdict: **PARTIAL — the fix is end-to-end and persistent, but consolidation needs a bigger D in the live brain**
The within-domain reliability fix is now wired into the deployed talk loop: reading a document auto-consolidates, deep
questions asked through `say()` are answered reliably (1.0) and survive save/load, exceptions stay respected, and no
conversation test regresses. The honest miss: consolidation's ~6× storage interacts with the live brain's **default
dimension**, inflating negative-probe false-positives (seed 0: 0.8). The bar is **not** moved; the clean fix is to
scale the durable store's dimension with consolidated load — pre-registered next as JEP-373. The capability (auto-
consolidated deep reliability, end-to-end + persistent) is demonstrated; the dimension-scaling is the remaining piece.
No transformer.
