# BET-133 — Two-word compositional context: next word needs BOTH prior words

Pre-registered: 2026-05-31 (BEFORE the run). Pushes past BET-132's single-slot verb
regularity to a genuine TWO-WORD context. Order-2 VSA context: code =
bundle_analog( bind(POS1, hv[w_{t-1}]), bind(POS2, hv[w_{t-2}]) ). Next word index =
(idx[w_{t-1}] + idx[w_{t-2}]) mod V — a rule that REQUIRES both words (drop either
and it is undetermined). Vocabulary V=12. Train online on a subset of bigram
contexts; TEST on held-out bigrams (ordered word-pairs never seen together).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T133a | Generalizes to novel bigrams | held-out next-word acc >= 0.85 |
| T133b | Learns online | held-out acc full − 25% >= 0.15 |
| T133c | No-rule control collapses | per-context random target held-out < 0.30 |
| T133d | Needs BOTH words | single-word context (POS2 masked) held-out < 0.45 |

PASS = T133a-d. PASS = the substrate generalizes a TWO-WORD compositional
next-word rule to unseen contexts, online, no transformer — and provably uses both
context words (single-word masking fails). NULL marks where order-2 composition
breaks and steers the structure-generalization frontier.

## RESULT (2026-05-31): NULL — linear-over-VSA cannot generalize a non-separable (modular) two-word rule

| metric | value | bar |
|--------|-------|-----|
| held-out acc @25% / @100% | 0.023 / **0.000** | T133a >=0.85 ✗ |
| online gain | −0.023 | T133b >=0.15 ✗ |
| no-rule (random) control | 0.114 | T133c <0.30 ✓ |
| single-word (POS2 masked) | 0.000 | T133d <0.45 ✓ |

T133a ✗, T133b ✗, T133c ✓, T133d ✓ → **NULL**. Clean and important: held-out
accuracy is exactly 0.000 — the linear readout over VSA codes does NOT generalize the
rule next=(idx[a]+idx[b]) mod V to unseen bigrams at all. Two honest reasons:
1. The readout here was LINEAR (features=identity); I did not engage the reservoir's
   nonlinearity. Modular addition is the canonical NON-SEPARABLE / non-linear task —
   exactly the boundary flagged in the BET-132 write-up ("separable regularities are
   carried by the linear readout; non-separable ones may need nonlinear features").
2. Words are RANDOM hypervectors, so (a+b) mod V has no geometric/additive structure
   in hv-space — a random representation cannot expose modular structure to ANY local
   readout without far more capacity/examples.

So this maps the frontier precisely: separable rules generalize (BET-126/130/132);
this non-separable modular rule does not, under a linear readout on random codes. ->
BET-134 asks the two follow-ups: (a) does the nonlinear SubstrateReservoir close it,
and (b) is the failure specific to modular arithmetic — does a LINGUISTICALLY natural
non-separable two-word rule (relational agreement, which BET-126 showed is learnable)
generalize where modular addition does not?
