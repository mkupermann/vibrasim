# JEP-336 — Compact-on-save: corrections are physically applied to the persisted brain

## Motivation
JEP-335's rule: compact periodically so corrections are reliable (1.0) rather than ~95% gate-override. Act on it:
the teaching GUI compacts on close before the final save, so what Michael corrects is physically applied to the
durable brain. Only compacts when there are RESOLVABLE corrections (a negation with a matching direct positive),
so it's a no-op cost when nothing to clean. No transformer.

## Method
`SubstrateMemory.has_resolvable_corrections()` → bool. `teach_gui._on_close` calls `self.sm = self.sm.compact()`
when needed, then saves. Verified headlessly (no Tk): teach corrections → simulate close (compact+save) → reload →
corrections answered reliably regardless of load.

## Pre-registered bars (BEFORE the run)
- **J336a (corrections physically applied):** after compact-on-save, the reloaded brain answers ALL corrected
  facts correctly (False for the wrong fact, True for the right one) = 1.0 at a multi-module load where plain
  gate-override would be ~0.95, both seeds (0, 7).
- **J336b (no-op when clean):** `has_resolvable_corrections()` is False for a store with no resolved corrections,
  so close doesn't needlessly rebuild; True when a correction is pending.
- **No-regression:** substrate test gate + JEP-322/324 still green; teach_gui imports.

Predicted most-likely failure: compact() swaps `self.sm`; if `self.al`/learner isn't carried over, the GUI loses
taught letters. compact() sets `new.learner = self.learner`, so it should persist — if J336 breaks letter recall,
that's the wiring (learner not carried), reported not tuned.

## Result (seeds 0, 7): **PASS**
- **J336a:** after compact-on-save at a 3-module / 40-correction load (where gate-override is ~0.95), the reloaded
  brain answers ALL corrected facts correctly = **1.0**, both seeds. **PASS.**
- **J336b:** `has_resolvable_corrections()` = True when a correction is pending, False for a clean store (so close
  is a no-op when nothing to clean); `teach_gui` imports with the wiring. **PASS.**
- **No-regression:** 13 substrate tests green; JEP-322 PASS; GUI imports.

## Verdict: **PASS**
The teaching GUI compacts on close (only when there are resolvable corrections), so what Michael corrects is
PHYSICALLY removed from the durable brain and answered with 1.0 reliability — not left to ~95% per-query override
(JEP-335). Carries the learner across the compaction (taught letters survive). Acts on the JEP-335 conclusion;
makes the interactive teach-and-correct loop durable AND reliable. No transformer.

