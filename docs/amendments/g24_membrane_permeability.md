# G24 — Selective membrane permeability: naming and testing the missing rule

Pre-registered: 2026-05-31 (BEFORE the run). Return to the physical substrate.

## Grounded finding (from the code, not assumed)
Phase 3 structure is DONE: closed membrane shells form spontaneously (BET-086, 5/5
seeds, 15–34 atoms, 50–75 vibrations enclosed, persistent 1000–19000 s). Phase 3
part 2 — SELECTIVE PERMEABILITY (CONCEPT §2.4, §4.1: "channel-points where
compatible-frequency molecules can pass") — is NOT done, and the code shows exactly
why:

- `move_vibrations` (world/physics.py) is pure inertial motion + periodic wrap — no
  collision, no membrane interaction.
- `apply_scale_repulsion` (physics.py:1597) acts only between BOUND nodes (`k_*`,
  level ≥ 1), never on free vibrations.
- Across the entire tick pipeline, a free vibration interacts with an atom ONLY via
  the 8 % binding rule. There is no frequency-gated passage.

So the membrane is TRANSPARENT to free vibrations. Selective permeability is absent
not for lack of tuning but because the RULE does not exist. This is the honest Phase-3
gap.

## Proposed minimal rule (G24)
A local, frequency-gated membrane channel: when a free vibration comes within
`r_channel` of a shell atom, it is REFLECTED (radial velocity component reversed)
UNLESS its frequency is compatible with the atom (within an 8 %-family band) — in
which case it passes. Compatible species cross the membrane; incompatible species are
contained. This is the substrate's own 8 % compatibility test, applied at the surface.

## Experiment (physics-faithful, runs on this machine)
A Fibonacci-sphere shell of atoms at a membrane frequency f_mem inside a 28³ box.
Free vibrations seeded OUTSIDE, moving inward, in two bands: COMPATIBLE (within 8 %
of f_mem) and INCOMPATIBLE (frequency ratio ≫ threshold). Motion replicates
`move_vibrations` exactly. Two arms:
- **Control (current substrate, rule OFF):** no membrane interaction.
- **G24 (rule ON):** frequency-gated reflection at the shell.
Measure the fraction of each band that ends up INSIDE the shell after T steps.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G24a | Control is non-selective | rule-OFF: |interior_compatible − interior_incompatible| < 0.12 |
| G24b | Rule creates a barrier | rule-ON: incompatible interior fraction < 0.20 (contained out) |
| G24c | Rule is selective | rule-ON: compatible interior fraction − incompatible ≥ 0.40 |
| G24d | Honest attribution | the selectivity appears ONLY with the rule (G24a holds) |

PASS = G24a-d. PASS = the current substrate has no selective permeability (control),
and a single local 8 %-gated reflection rule produces it — naming and validating the
minimal Phase-3 amendment. This is the CONCEPT's own methodology (§6.5, §9.4: find
which additional rule a level needs). It is an ADDED rule, framed as such, NOT a claim
that the substrate already had selectivity. NULL would mean even this rule does not
produce clean selectivity and a different mechanism is needed.

## RESULT (2026-05-31): NULL/partial — wrong metric, not wrong physics

| arm | interior compatible | interior incompatible |
|-----|---------------------|------------------------|
| control (rule OFF) | 0.033 | 0.047 |
| G24 (rule ON) | 0.033 | **0.000** |

G24a ✓ (control non-selective, |−0.013|), G24b ✓ (rule blocks incompatible, 0.000),
G24c ✗ (gap only +0.033), G24d ✓ → **NULL/partial**.

The rule DOES create a selective barrier — incompatible vibrations never get inside
(0.000 vs control 0.047), they reflect off the shell. But compatible vibrations only
register 0.033 inside because they PASS THROUGH and exit the far side — they transit,
they do not accumulate. My bar G24c used "interior fraction at end-time", which
conflates PERMEABILITY (does the species cross?) with RETENTION (does it stay?). A
membrane is selectively permeable if compatible species CROSS and incompatible do not,
regardless of whether compatible then leave. Wrong metric, not wrong physics.
-> G25 re-measures permeability as CROSSING FLUX (entry events), pre-registered fresh.
