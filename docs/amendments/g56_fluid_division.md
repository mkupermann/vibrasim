# G56 — Fluid membrane fission: does strong curvature split one shell into two?

Pre-registered: 2026-06-02 (BEFORE the run). The fluid membrane (G53–G55) is size-homeostatic and
coalesces to ONE shell (G51). Cell DIVISION = one membrane → two. Test whether a fluid membrane
under STRONG spontaneous curvature (which has a preferred radius) becomes unstable at large size
and FISSIONS into ≥2 shell-like components. Fluidity (bond turnover) is required so the network can
remodel and pinch; strong curvature_k is the splitting driver.

## Method
G30 substrate, larger material supply (box 28³, n_initial 600, caps scaled), fluid
(bond_turnover_rate=0.15, node_thermal_speed=0.2), strong curvature (curvature_k=4.0 vs 2.0),
edge_closure_k=2.0. Run 400 ticks. Enumerate all bridged components each checkpoint; count
shell-like ones (≥30 atoms, σ_r/R<0.45). Track the trajectory of the shell count. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G56a | A membrane forms | ≥1 shell-like component at some point, both seeds |
| G56b | Fission to a population | max shell-like component count ≥ 2 during the run, both seeds |
| G56c | Fluidity required (control) | rigid (turnover=0) does NOT reach ≥2 shells (both seeds) — division needs the fluid remodeling |

PASS = G56a–c → strong curvature splits a fluid membrane into multiple shells (a division/fission
event), only when fluid: the substrate can produce a membrane POPULATION by fission, not just
coalescence. NULL: if G56b fails the fluid membrane stays a single shell (curvature deforms but
does not pinch off) — an honest boundary on division; if G56c also splits, multiplicity is a
formation artifact, not fission. Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL — fluid membrane stays a single shell (no fission)

FLUID max_shells=1 throughout (both seeds, trajectory all 1s); RIGID also 1. Even with strong
spontaneous curvature (4.0) + fluidity, the membrane does NOT split — it remains one coalesced
minimal surface. G56b ✗. Division does not occur by curvature instability; the substrate robustly
coalesces to a single shell (consistent with G51). Honest boundary: no spontaneous fission/division.
