# Free dual talent NULL farm — formal closure (C27–C41 + C26)

**Date:** 2026-07-26  
**Depends on:** C16 CLOSED PARTIAL (ilw_strength_decay + wall seed-set unlock); C1–C15 earlier closed  
**Discipline:** After C27–C41, **stop farming free dual mechanism knobs** that are variants of inject+wall+single-config-toggle without a new substrate primitive.

## Verdicts (this farm)

| ID | Mechanism | Verdict | Note |
|----|-----------|---------|------|
| C26 | charge_latch_tau free dual | **FAILED** | hard-cap overrun |
| C27 | short pair_decay | NULL | |
| C28 | short triad_decay | NULL | |
| C29 | asymmetric L/R speed | NULL | |
| C30 | atom_repulsion_k | NULL | hurts |
| C31 | n_emit | NULL | |
| C32 | elevated r_1 | NULL | 0.75 ordered |
| C33 | PRIM7 sideband cull | NULL | pop collapse |
| C34 | elevated r_2 | NULL | pop collapse |
| C35 | lambda_gen | NULL | |
| C36 | tight freq_tolerance | NULL | pop collapse |
| C37 | slow global speed | NULL | |
| C38 | corr_plasticity | NULL | pop collapse |
| C39 | compartment_boundary | NULL | |
| C40 | lambda_dec | NULL | |
| C41 | asymmetric N_SIDE | NULL | treat worse |

## Doctrine

1. **C16 remains** the only free dual partial unlock: `ilw_strength_decay_tau` + midplane wall (seed-set). Not re-opened by bar retune.
2. Single-knob free dual inject+wall **variants above do not unlock** ordered ≥0.90 with treat>control delta bars.
3. Further free dual work requires a **new primitive class** (not another decay/speed/geometry/pop/plasticity toggle from this list).

## Do not farm

pair/triad decay · speed asym/slow · atom_repulsion · n_emit · r_1/r_2 · sideband cull · lambda_gen/dec · tight freq_tol · corr_plasticity · compartment · N_SIDE asymmetry · latch-tau retry without design change

## Open

- Free dual only with mechanism **not** in this table and **not** C16 retune.
- Engineered port multi-trial curricula (E162–E192) closed separately — not free dual.
