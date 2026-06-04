# JEP-77 — systematic generalization on a tiny command language (SCAN-style), substrate-legal (no LLM)

## Motivation (honest gap #4: language as compositional interface)
Human language is systematically compositional: knowing "walk" and "jump twice" you understand "walk twice"
(Lake & Baroni 2018, SCAN). Standard seq2seq FAILS this; the question is whether a COMPOSITIONAL (factored)
representation succeeds where a HOLISTIC (memorization) one fails - using established methods, NO transformer/LLM.

## Task
Command = (verb in {walk,run,jump,look}, count in {1,2,3,4}); output sequence = [verb] repeated count times.
Two models: FACTORED (separate verb head + ORDINAL count head, count as a scalar) vs HOLISTIC (joint
(verb,count) index -> memorized output). Two generalization splits:
- SPLIT-COMBO (primitive recombination): hold out 4 of 16 (verb,count) combos; all verbs & counts seen elsewhere.
- SPLIT-LENGTH (productivity): train count in {1,2}; TEST count in {3,4} - outputs LONGER than any trained.

## Pre-registration (locked BEFORE run)
- Metric: exact-sequence accuracy on held-out.
- PASS: FACTORED >= 0.90 on BOTH splits AND HOLISTIC <= 0.30 on SPLIT-LENGTH (the baseline MUST fail to make the
  result defensible - per CLAUDE.md negative-control discipline). PASS => compositional representation is what
  yields systematic generalization on a language interface; holistic memorization cannot extrapolate.
- Honest bound stated up front: the compositional structure (slots + ordinal count) is BUILT IN; this shows that
  structure YIELDS systematicity (replicating SCAN's lesson substrate-legally), it does NOT learn the structure
  unsupervised (gap #1, still open). Tiny toy. Established (SCAN/Lake-Baroni, factored representations), named.

## Result — PASS
| model | SPLIT-COMBO | SPLIT-LENGTH |
|-------|-------------|--------------|
| FACTORED (compositional) | 1.00 | 1.00 |
| HOLISTIC (memorization)  | 0.00 | 0.00 |

**VERDICT: PASS.** A factored/compositional representation generalizes systematically on a language interface —
held-out combinations AND longer-than-trained sequences (1.00) — while the holistic baseline cannot extrapolate
(0.00, the required negative control). Compositional STRUCTURE is what yields systematicity; replicates SCAN
(Lake-Baroni 2018) substrate-legally, NO transformer/LLM. HONEST BOUND: the structure (slots + ordinal count) is
BUILT IN — this shows structure yields systematicity, it does NOT learn the structure unsupervised (gap #1, open).
Tiny toy. Established, named; no novelty.
