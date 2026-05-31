# BET-125 — Systematic (symbolic) generalization over composed substrate codes

Pre-registered: 2026-05-31 (BEFORE the run). Follows BET-124 (interpolative). The
honest hard test for language: generalize to novel COMBINATIONS of known symbols
(systematic generalization), not novel interpolation points.

## Task — relational comparison (a classic systematic-generalization probe)
M=10 symbols, each a random ±1 hypervector hv[k] AND a hidden scalar value v[k].
A pair (i,j), i!=j, is COMPOSED with the substrate's VSA algebra (world/vsa.py):

    code(i,j) = bundle( bind(ROLE_left, hv[i]), bind(ROLE_right, hv[j]) )

Target label = +1 if v[i] > v[j] else -1 (an ASYMMETRIC relation: needs left vs
right). Split the 90 ordered pairs into 60% train / 40% HELD-OUT pairs. Systematic
split: EVERY symbol appears in training pairs; only specific COMBINATIONS are held
out. Models learn ONLINE (RLS), one pair at a time.

Models compared:
- **reservoir**  : SubstrateReservoir over code(i,j) — nonlinear substrate features.
- **linear-VSA** : linear RLS readout directly on code(i,j).
- **no-binding control**: code = bundle(hv[i], hv[j]) WITHOUT roles, so
  code(i,j)==code(j,i). Destroys left/right structure — an asymmetric relation
  becomes unsolvable. MUST fail.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T125a | Systematic generalization | best structured model held-out acc >= 0.85 on NOVEL pairs |
| T125b | Composition carries it (not lookup) | no-binding control held-out acc < 0.65 |
| T125c | Relation is learned (not noise) | shuffled-label control held-out acc < 0.65 |

PASS = T125a-c. PASS = the substrate generalizes a RELATION to symbol combinations
it never saw, and the win is proven to come from COMPOSITIONAL binding (the
no-binding control collapses). This is the systematic-generalization step VSA-codes
+ substrate readout give that pure memorization (BET-117) cannot. NULL/partial is a
real finding: it would mark exactly which relations stay out of reach and steer
BET-126.

## RESULT (2026-05-31): NULL — systematic generalization does NOT fall out of sign-bundled VSA codes

| metric | value | bar |
|--------|-------|-----|
| reservoir held-out acc | 0.639 | — |
| linear-VSA held-out acc | 0.611 | — |
| best structured (T125a) | 0.639 | >=0.85 ✗ |
| no-binding control (T125b) | 0.222 | <0.65 ✓ |
| shuffled-label control (T125c) | 0.417 | <0.65 ✓ |

T125a ✗, T125b ✓, T125c ✓ → **NULL**. Honest, informative:
- The relation IS tied to composition — both controls collapse hard (no-binding
  0.222 *below* chance: with code(i,j)==code(j,i) an asymmetric label is
  anti-learnable; shuffled-label 0.417 ≈ chance). So the substrate is using the
  bound structure, not memorizing.
- BUT held-out accuracy on novel symbol pairs is only ~0.64 — systematic
  generalization of the comparison relation is WEAK. Reservoir ≈ linear-VSA, so the
  nonlinear features didn't add systematic power here.

**Diagnosed mechanism (-> BET-126 hypothesis, no post-hoc tuning of this bet).**
`bundle` applies `sign(Σ)`. That sign nonlinearity destroys the ANALOG
superposition a linear readout needs to unbind a slot and recover each symbol's
value: with analog (non-sign) bundle, code⊙role_left ≈ hv[i] + noise, so a single
linear readout W = w_left⊙role_left − w_right⊙role_right computes v[i]−v[j] and
generalizes to ANY pair systematically. Pre-registered fresh as BET-126: analog
superposition restores systematic generalization. NULL generated a falsifiable
mechanism — exactly the experiment-series mandate.
