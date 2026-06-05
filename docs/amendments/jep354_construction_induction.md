# JEP-354 — Construction induction: learn a new sentence pattern from a few examples (breakthrough attack A)

## Motivation
The breakthrough is self-extension: instead of hand-coding every sentence form, the system LEARNS a new construction
from 2-3 (sentence → fact) examples and applies it to unseen sentences. Established method: anti-unification /
template generalisation (name it as such). This attacks the messy-text wall by LEARNING, not coding. No transformer.

## Method
Given ≥2 examples (sentence, fact=(s,r,o)) of one construction, ALIGN them: tokens that are SAME across examples are
the template's fixed words; tokens that VARY are slots; record which slot fills each fact position. Apply: match the
template against a new sentence (fixed words must match in order, slots capture), build the fact via the learned
slot→fact mapping.

## Pre-registered PREDICTION + bars
Prediction: this WORKS for slot-templates (examples sharing fixed words, varying fillers) and generalises to unseen
sentences of the SAME template; it will NOT generalise across different templates (that's attack C). Expected ~PASS
on same-template held-out, ~0 false-fire on a different template.
- **J354a (induce + apply):** from 2 examples each of 3 constructions — passive "{x} was domesticated by {y}" →
  (y,domesticated,x); locational "{x} lives in {y}" → (x,lives_in,y); "{x} is the capital of {y}" →
  (x,capital_of,y) — correctly extract the fact from 2 HELD-OUT sentences of the same construction, ≥ 0.90 each,
  both seeds (0, 7).
- **J354b (honest boundary):** an induced template does NOT fire on a sentence of a DIFFERENT construction (no false
  facts), both seeds — and the limitation (needs matching fixed words) is reported.

Predicted most-likely failure: slot/fixed-word mis-alignment when two slots are adjacent, or a held-out sentence
whose fixed words differ slightly (a/the). If J354a misses, report the alignment failure; keep templates to clearly
separated slots.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J354a:** from 2 examples each, the inducer learns the template and extracts the correct fact from HELD-OUT
  sentences = **1.0** on all 3 constructions (passive "domesticated by", "lives in", "capital of"), both seeds.
  **PASS.**
- **J354b:** zero false-fire — a learned template does NOT extract from a different construction, both seeds.
  **PASS.**

## Verdict: **PASS — first breakthrough-attack result (honestly scoped)**
The system LEARNS a new sentence construction from just 2 (sentence → fact) examples (anti-unification: fixed words
vs varying slots, slot→fact-role mapping) and applies it to unseen sentences of that pattern — **self-extension
without an LLM**, the first real step of the breakthrough programme (attack A). Honest scope, named not hidden:
this is TEMPLATE-level (held-out sentences must share the fixed words; "a/the" or word-order changes break it), and
it does NOT yet generalise across different templates or abstract structure — that is attack C, where the real test
of "did it learn structure or just slots?" lives. A genuine, established method (template induction / ILP-lite),
applied substrate-legally; not yet "the breakthrough," but a concrete, measured rung toward it. No transformer.

