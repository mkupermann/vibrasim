# JEP-462 — Final integration + durability audit (all session features, across a reload)

## Motivation
This session added many cognition features on top of the reasoning brain: energy/affect + generalization
(436–440), affect inheritance + honest source tags (450/451), ability negation (453), -oes morphology
(455), proper nouns + superlatives (424). They've been verified piecemeal and live in the GUI, but never
ALL together AND across a save/reload. JEP-462 is the closing audit: teach one coherent world using every
feature, run a full battery, then SAVE → RELOAD and re-run the battery — confirming the whole integrated
brain is correct, composes without interference, has zero confident falsehoods, and is DURABLE.

## Method (`tools/run_jep462_final_audit.py`)
Teach a coherent world (multi-branch taxonomy, properties, a flightless exception via ability-negation,
parts, an attribute, affect on a class, a proper noun with a count, a superlative, an -oes plural). Run a
~16-item battery covering ALL features. Then `save()` to a temp dir, `load()` a fresh brain, and re-run
the SAME battery. Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J462a (everything composes):** ≥ 15/16 battery items correct BEFORE reload, both seeds.
- **J462b (no confident falsehoods):** zero items asserting a FALSE yes/no or fabricated value, both seeds.
- **J462c (durable):** AFTER reload, the battery score and falsehood count are IDENTICAL to before (the
  whole integrated brain — facts, taxonomy, affect, energy model, source tags — survives the round-trip),
  both seeds.

PASS = the full session's cognition work composes cleanly and survives a reload with no loss and no
falsehoods — a clean, durable closing state. NULL if a feature breaks in combination (report which) or
something is lost on reload. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** — clean, durable closing state

| seed | before reload | after reload |
|------|---------------|--------------|
| 0 | 16/16, 0 falsehoods | 16/16, 0 falsehoods |
| 7 | 16/16, 0 falsehoods | 16/16, 0 falsehoods |

J462a ✓ (16/16 ≥ 15), J462b ✓ (zero confident falsehoods), J462c ✓ (identical after reload) → **PASS,
both seeds.**

## Verdict: the full session's cognition work composes and persists
All features added this session — multi-hop is-a, property inheritance, ability-negation exceptions
(penguin can't fly), parts, affect inheritance + honest "(inherited from X)" tag + "why" explanation,
proper nouns (Mars), proper-noun counts (moons=2), superlatives (largest planet), attributes (capital),
is-a directionality, and honest abstention on the untaught — answer correctly TOGETHER in one coherent
brain (16/16) with ZERO confident falsehoods, and the entire integrated state survives a save→reload
unchanged. Combined with the live-GUI end-to-end verification (same features served over HTTP), the
session's conversational/affect work is delivered, integrated, audited, and durable. Established
methods throughout, named; no transformer.
