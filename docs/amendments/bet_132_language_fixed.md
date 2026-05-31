# BET-132 — Micro-language next-word generation, corrected control

Pre-registered: 2026-05-31 (BEFORE the run). Identical to BET-131 except the
"no-rule" control is fixed: instead of a shuffled (still-consistent) verb->object
permutation, the control assigns a PER-SENTENCE RANDOM object (no function from
context to next word), which must give chance. T131a/b/d carried over (already met
in BET-131: 1.000 held-out, +0.25 online, 0.000 subject-only).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T132a | Generates novel sentences | held-out next-word accuracy >= 0.85 |
| T132b | Learns online | held-out acc full − 25% >= 0.15 |
| T132c | No-rule control collapses | per-sentence-random-target held-out < 0.40 |
| T132d | Uses the verb | subject-only (verb masked) held-out < 0.40 |

PASS = T132a-d. PASS = the substrate generates the correct written next word for
sentences it never saw, the ability depends on a learnable regularity AND on reading
the verb slot, learned online, no transformer.

## RESULT (2026-05-31): PASS — first clean language-direction milestone

| metric | value | bar |
|--------|-------|-----|
| held-out next-word acc @25% / @100% | 0.750 / **1.000** | T132a >=0.85 ✓ |
| online gain | +0.250 | T132b >=0.15 ✓ |
| no-rule (per-sentence random target) | 0.188 | T132c <0.40 ✓ (≈ chance 1/6) |
| subject-only (verb masked) | 0.000 | T132d <0.40 ✓ |

T132a–d all ✓ → **PASS**. The substrate GENERATES the correct written next word for
all 16 sentences it never saw (subject+verb combinations held out), the ability
collapses to chance when there is no regularity to learn (0.188) and to zero when
the verb is hidden (0.000) — so it is reading the composed structure and exploiting
the selectional regularity, not memorizing. Learned strictly ONLINE (0.75→1.00 as
sentences arrive). NO LLM, NO transformer: analog VSA composition + an online linear
readout + content-addressable cleanup to the vocabulary. First demonstration of
substrate-native, generalizing, online written-word generation.
