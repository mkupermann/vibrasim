# G85 — Quiet substrate + local emission: the combination at the root

Pre-registered: 2026-06-03 (BEFORE the run). G84 showed that on a quiet substrate the write is intact
(stim=6.03) but control still latches (5.60) via FAST emission transit (emit_speed=30 = 15 units/tick
= the stim->control distance, reaching control before the next cull). The fix combines BOTH levers:
QUIET substrate (cull background every tick -> control not self-active, input registers, per G83) AND
LOCAL emission (low emit_speed -> the write field co-fires stim neighbours but never travels to
control). G64 tried local emission on the ACTIVE substrate (background drowned it); G84 quieted but
kept fast emission. The combination is untested and addresses both contamination routes. BET-099
correlation-memory protocol, cull-each-tick (G84), sweep emit_speed {3, 6, 12}. Seed 42.

## Bars (locked pre-run — standard memory bars)
| ID | Criterion | Bar |
|----|-----------|-----|
| G85a | Selective write | ∃ emit_speed: LOC STIM fraction-selective ≥ 0.5 |
| G85b | Persistent recall | same: LOC POST (≥ stim_end+2000 s) fraction-selective ≥ 0.5 |
| G85c | Uniform control fails | same: UNI POST fraction-selective < 0.25 |

PASS = G85a-c at one emit_speed → SELECTIVE PERSISTENT MEMORY: removing the root (quiet) + keeping
the write local breaks the write=leak deadlock that resisted ~50 experiments. The memory milestone —
replicate across seeds before any claim. NULL = even quiet + local, control latches (the write field
inherently reaches control, or local emission starves the co-firing write) → the deadlock is truly
fundamental: the write is inseparable from contamination at any locality/quietness. Honest either way.
No post-hoc tuning.
