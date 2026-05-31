# BET-131 — Next-word generation in a templated micro-language (the language step)

Pre-registered: 2026-05-31 (BEFORE the run). First experiment pointing the proven
engine (analog VSA composition + online readout, BET-126→130) at actual written
SYMBOLS and GENERATION. A templated micro-language: sentences "<subject> <verb>
<object>" where each verb selects a canonical object (a real selectional
regularity, like English verbs selecting their objects). Vocabulary: 8 subjects,
6 verbs, 6 objects (20 written tokens).

Task: given the composed context code( bind(ROLE_subj,hv[subj]),
bind(ROLE_verb,hv[verb]) ), the online readout predicts the next word's hypervector;
CLEANUP (nearest vocabulary code, the substrate's content-addressable attractor)
emits the actual word. Train online on a subset of (subject,verb) sentences; TEST on
held-out sentences = subject+verb COMBINATIONS never seen together. Systematic
generalization = emit the correct object word for novel sentences.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T131a | Generates novel sentences | held-out next-word accuracy >= 0.85 |
| T131b | Learns online | held-out acc at full training > acc at 25% training by >= 0.15 |
| T131c | Uses the rule, not noise | shuffled verb->object control held-out < 0.40 |
| T131d | Uses the verb (linguistic regularity) | subject-only readout (verb masked) held-out < 0.40 |

PASS = T131a-d. PASS = the substrate GENERATES the correct written next word for
sentences it never saw, by composing known words and reading out online — concrete
movement toward written-language communication that generalizes and learns per
interaction, with NO LLM / transformer. NULL bounds where the toy language breaks.

## RESULT (2026-05-31): NULL/partial — perfect generation, but one control was mis-designed

| metric | value | bar |
|--------|-------|-----|
| held-out next-word acc @25% train | 0.750 | — |
| held-out next-word acc @100% train | **1.000** | T131a >=0.85 ✓ |
| online gain (full − 25%) | +0.250 | T131b >=0.15 ✓ |
| shuffled-rule control | 1.000 | T131c <0.40 ✗ |
| subject-only (verb masked) | 0.000 | T131d <0.40 ✓ |

T131a ✓, T131b ✓, T131c ✗, T131d ✓ → **NULL/partial**.

The substrate GENERATED the correct written next word for all 16 held-out sentences
it never saw (100%), improved online (0.75→1.00), and provably USES the verb (with
the verb masked, accuracy is 0.000 — it cannot guess the object from the subject).
That is real systematic next-word generation.

BUT T131c is a **control-design bug, not a result**: shuffling the verb→object
mapping yields ANOTHER consistent deterministic function, which is equally learnable
and generalizes — so it cannot destroy the regularity. The correct "no-rule" control
is a PER-SENTENCE RANDOM target (no function from context to object), which must drop
held-out accuracy to chance (1/6 ≈ 0.167). Re-registered cleanly as BET-132 with the
corrected control (T131a/b/d unchanged and already met). No silent fix — recorded as
NULL and re-run fresh.
