# JEP-454 — Expanded adversarial audit: hunt remaining confident falsehoods

## Motivation
JEP-452's 12-item audit caught a confident falsehood the per-feature tests missed (penguin can fly,
fixed in JEP-453). The project's core promise is "never assert a falsehood — abstain instead." A
single catch implies more may lurk in feature INTERACTIONS. JEP-454 runs a larger (~20-probe)
adversarial battery over one richer mini-world, targeting known traps (is-a directionality, deep
chains, multiple flightless exceptions, two-level affect inheritance, affect NOT inherited from
neutral ancestors, abstention on the untaught, attribute-vs-is-a, reverse is-a) — to find any
remaining confident falsehoods. Established audit method; no new science. No transformer.

## Method (`tools/run_jep454_expanded_audit.py`)
Teach a richer world (multi-branch taxonomy, properties, TWO flightless exceptions, affect on two
classes with children, parts, an attribute, an emotional fact + interference), then run ~20 probes
each with a pre-classified expected answer. Each answer is scored correct / abstain / **falsehood**
(asserts the opposite of truth, or fabricates a wrong specific value). Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J454a (the core promise):** ZERO confident falsehoods across all probes, both seeds.
- **J454b (competence):** ≥ 85% of probes answered CORRECTLY (not merely abstained), both seeds.
- **J454c (suites green):** substrate_memory + conversation tests pass.

PASS = J454a–c → the integrated brain is competent AND never confidently wrong (abstains on the rest).
NULL if J454a fails (a falsehood remains — report it; it becomes the next fix) or J454b < 0.85 (a
real capability/phrasing gap). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** — zero confident falsehoods

| seed | correct | falsehoods |
|------|---------|------------|
| 0 | 19/20 (0.95) | 0 |
| 7 | 19/20 (0.95) | 0 |

J454a ✓ (ZERO confident falsehoods), J454b ✓ (0.95 ≥ 0.85), J454c ✓ (suites green) → **PASS, both seeds.**

The integrated brain answered 19/20 correctly and the one miss was an **abstention, not a falsehood**:
"what is the energy of a knight?" → neutral (should be bright: knight is-a hero, heroes are good).
Across is-a directionality (both reverse probes correct), deep chains, TWO flightless exceptions,
two-level affect inheritance (cobra/viper → dark ✓), cross-branch negatives, and abstention on the
untaught — **no confident falsehood**. The core promise holds: competent, and never confidently wrong.

**The lone miss is a recurring morphology bug, not a reasoning failure (found, fixed in JEP-455).**
"Heroes are good" singularizes "Heroes" → **"heroe"** (the simple -s strip), so valence is tagged on
`heroe` while "A knight is a hero" stores `hero` — they don't match, so knight inherits nothing. This
is the -oes/-es class (same family as the earlier foxe/viruse bugs, calibration lesson #15). The snake
branch worked because "snake" singularizes cleanly. Fixed in JEP-455 -> audit re-runs **20/20, falsehoods=0**.
