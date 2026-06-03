# G84 — Selective persistent memory on a QUIET substrate (re-attacking the deadlock at its root)

Pre-registered: 2026-06-03 (BEFORE the run). G83 causally confirmed the root: homogeneous self-
activity drowns signal (active substrate: input unreadable; quiet substrate: input read perfectly,
1.00). The memory deadlock (G33-G73, declared "fundamental") was measured on the ACTIVE substrate
where control is never blank. This re-tests memory on a MAXIMALLY QUIET substrate: during STIM, cull
ALL free vibrations each tick and inject ONLY the stimulus, so the only activity is stim-driven.
Stim atoms co-fire (local injection field) and write; control gets NO input -> silent -> its bridges
can't latch -> selective. BET-099 correlation-memory protocol otherwise. Seed 42.

## Bars (locked pre-run — standard memory bars)
| ID | Criterion | Bar |
|----|-----------|-----|
| G84a | Selective write | LOC STIM fraction-selective ≥ 0.5 |
| G84b | Persistent recall | LOC POST (≥ stim_end+2000 s) fraction-selective ≥ 0.5 |
| G84c | Uniform control fails | UNI POST fraction-selective < 0.25 |

PASS = G84a-c → SELECTIVE PERSISTENT MEMORY: removing the homogeneous-activity root (quiet substrate)
breaks the write=leak deadlock that no plasticity/firing knob could. This would be the memory
milestone — replicate across seeds before any claim. NULL = the deadlock persists even quiet (the
write still needs a spreading field that contaminates, or culling starves the write) -> the deadlock
is deeper than background activity. Honest either way. No post-hoc tuning.
