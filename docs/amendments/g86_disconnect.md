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
