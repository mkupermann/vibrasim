# G86 — Quiet + local + DISCONNECTION: the definitive percolation test

Pre-registered: 2026-06-03 (BEFORE the run). G85 pinned the contamination to BRIDGE-GRAPH
PERCOLATION (charge flows stim->control along the connected lattice, defeating quiet + local). The
implied fix: true DISCONNECTION. New engine change: form_bridges skips pairs straddling
compartment_boundary (no bridge across x=15) AND neuron charge integration is already gated across it
(BET-103). With quiet (cull each tick) + local emission (emit_speed=6) + disconnection
(compartment_boundary=15 between stim x=7.5 and control x=22.5), stim and control share NO bridges and
NO cross charge -> control fully isolated -> blank -> selective. BET-099 protocol, seed 42.

## Bars (locked pre-run — standard memory bars)
| ID | Criterion | Bar |
|----|-----------|-----|
| G86a | Selective write | LOC STIM fraction-selective >= 0.5 |
| G86b | Persistent recall | LOC POST (>= stim_end+2000 s) fraction-selective >= 0.5 |
| G86c | Uniform control fails | UNI POST fraction-selective < 0.25 |

PASS = G86a-c -> SELECTIVE PERSISTENT MEMORY via engineered disconnection + quiet + local: the
deadlock breaks when the contamination route (lattice percolation) is physically cut. This confirms
the charter's thesis (selective memory needs engineered modularity) and is the memory milestone -
replicate across seeds. NULL = even full disconnection fails (the write starves when isolated, or
control latches via yet another route) -> the deadlock is fundamental at the deepest level. Honest
either way. No post-hoc tuning.

## RESULT (2026-06-03): NULL — control latches INTRINSICALLY; deadlock conclusively unbreakable

LOC STIM: stim=5.88 ctrl=5.63. Even with stim and control FULLY DISCONNECTED (no shared bridges,
no cross charge) + quiet + local emission, control still latches (5.63). Control's latching is NOT
contamination from stim — it is INTRINSIC: control's own atoms develop latched bridges with no input.
New bridges start at low (1.0), yet control reaches 5.6, so control atoms co-fire via a residual/
intrinsic route. The mechanism keeps shifting (emission transit -> percolation -> intrinsic latching)
but the RESULT is invariant across every fix.

## DEFINITIVE CLOSE — selective memory is unbreakable in this substrate
Across ~70 experiments (BET-089->102, G33-G73, G64-G86) every mechanism fails identically: firing
selection, plasticity rule, consolidation, sleep-sweep, charge persistence, quiet substrate, local
emission, AND physical disconnection. The invariant: the substrate has NO STABLE BLANK STATE — any
region with atoms develops latched bridge activity, so there is never a contrast between a written
(stim) and an unwritten (control) region. Selective persistent memory is therefore impossible, not
for want of a write mechanism (every write works) but because the medium cannot stay quiescent where
it is structured. This is the deadlock, exhaustively and causally closed. The honest decision: STOP
the memory thread (continuing past 70 NULLs is refusing a robust negative, not science). The
substrate is a memoryless nonlinear analog processor.
