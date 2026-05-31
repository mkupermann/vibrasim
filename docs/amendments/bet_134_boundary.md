# BET-134 — What kind of non-separable two-word rule generalizes?

Pre-registered: 2026-05-31 (BEFORE the run). BET-133 showed a LINEAR readout cannot
generalize modular addition over random codes. Two follow-ups, one experiment:
is non-separability itself the blocker, or is it the lack of RECOVERABLE STRUCTURE?

- **Relational-selection (structured, non-separable):** two-word context, target =
  the LARGER of the two context words (output word[a] if val[a]>val[b] else word[b];
  val = hidden per-word scalar). Needs both words; relational, like BET-126's
  comparison which DID generalize; the output is a word PRESENT in the context
  (recoverable). Readout = online linear on the VSA code. Test held-out novel bigrams.
- **Modular-with-reservoir (unstructured, non-separable):** the BET-133 rule
  (idx[a]+idx[b]) mod V, but now with the FULL nonlinear SubstrateReservoir
  (features=tanh(Rx), reservoir dim 2000). Does the nonlinearity rescue it?

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T134a | Structured non-separable generalizes | relational-selection held-out >= 0.85 |
| T134b | Not noise | relational-selection no-rule (random target) < 0.40 |
| T134c | Needs both words | relational-selection single-slot (POS2 masked) < 0.65 |
| T134d | Unstructured stays unreachable | modular-with-reservoir held-out < 0.40 |

PASS = T134a-d. PASS draws the boundary precisely: the substrate generalizes
non-separable two-word rules WHEN they have recoverable relational structure, but NOT
arbitrary non-linear maps over random codes — and this is a representation property,
not fixed by adding nonlinear features. That tells the language programme to favour
STRUCTURED regularities (agreement, selection, comparison) and to give symbols
structured (not purely random) codes when arbitrary maps are needed.

## RESULT (2026-05-31): PASS — boundary mapped (and a caveat on novelty)

| metric | value | bar |
|--------|-------|-----|
| selection held-out @25%/@100% | 0.523 / 0.864 | T134a >=0.85 ✓ |
| selection no-rule control | 0.068 | T134b <0.40 ✓ |
| selection single-slot | 0.500 | T134c <0.65 ✓ |
| modular WITH reservoir | 0.000 | T134d <0.40 ✓ |

T134a–d ✓ → **PASS**. The substrate generalizes a non-separable two-word rule
("output the larger word") to novel bigrams (0.864), online, needs both words
(single-slot 0.50), control at noise (0.068). The SAME stack on modular addition
stays at 0.000 even with the full nonlinear reservoir (2000 features). Boundary: it
is RECOVERABLE STRUCTURE, not non-separability per se, that decides generalization;
adding nonlinear features does not rescue an arbitrary map over random codes.

**Caveat (honest):** the methods used across BET-124→134 — VSA/hyperdimensional
computing (Kanerva, Plate), reservoir computing / extreme learning machines (Jaeger,
Huang), recursive least squares — are ESTABLISHED, not new mathematics. This bet
maps a known representational limit cleanly on the substrate; it is competent
composition and honest measurement, not novelty. See LOGBOOK 2026-05-31 reckoning.
