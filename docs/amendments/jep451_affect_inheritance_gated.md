# JEP-451 — Affect inheritance with the statistical fallback gated (JEP-450 fixed)

## Motivation
JEP-450 found (a) valence inheritance through is-a works with an explanation, but (b) the
`predict_valence` energy-model FALLBACK hallucinates affect when valence data is sparse/one-sided (a
single negative example → predicts negative for everything, so an unrelated `desk` wrongly read
"dark"). JEP-451 gates the fallback: it generalizes only when valence training is rich enough (≥6
valenced concepts spanning BOTH polarities), else abstains (neutral). Then the inheritance test is
re-run with a real affect-lexicon word ("evil"), so valence is actually set.

## Method
- `predict_valence` order: own valence → inherited ancestor valence → (GATED) energy-model
  generalization → neutral. Gate = `len(valence) ≥ 6 and both signs present`.
- Live test (Conversation): "Snakes are evil" (lexicon word → sets valence) + taxonomy; a cobra/python
  inherit dark; "why is a cobra evil?" cites the ancestor; a `desk` (no valenced ancestor, sparse
  valence) is neutral — no hallucination.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J451a (affect inherits):** `energy(cobra)` and `energy(python)` are dark (inherited), both seeds.
- **J451b (explained):** "why is a cobra evil?" → cites the valenced ancestor (snake), both seeds.
- **J451c (no hallucination):** `energy(desk)` is neutral (the gated fallback abstains on sparse data),
  both seeds; substrate_memory 14/14 + conversation 10/10 + the JEP-436 rich-data generalization test
  stay green (the gate is inert when data is rich).

Predicted PASS. NULL if J451a fails (inheritance broken) or J451c fails (still hallucinating). Bars
locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

Both seeds: `energy(cobra)` and `energy(python)` → **"dark (negative energy) (inherited from snake)"**;
"why is a cobra evil?" → **"because cobra is a kind of snake"**; `energy(desk)` → **neutral**.

J451a ✓ · J451b ✓ · J451c ✓ → **PASS, both seeds.** substrate_memory 14/14 + conversation 10/10 green.

## Verdict: explainable affect inheritance, with honest sourcing and no hallucination
Affect now flows through the is-a taxonomy: a child inherits the nearest valenced ancestor's affect
and the brain explains it ("because cobra is a kind of snake"). The energy query honestly distinguishes
the SOURCE — taught (no tag) / **(inherited from X)** / **(generalized)** (statistical). The statistical
fallback is gated (≥6 valenced concepts spanning both polarities) so unrelated concepts on sparse data
stay neutral instead of hallucinating affect — while the JEP-436 rich-data generalization is unchanged
(gate inert there, 14/14 green). Energies now flow through concept relationships AND are explained,
combining the taxonomy reasoner with the affect model. Established methods (inheritance reasoning +
valence), named — integration only, NOT new science. No transformer.
