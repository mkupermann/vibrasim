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

## RESULT (2026-06-03): NULL — control latches via FAST EMISSION TRANSIT (emit_speed=30 beats the cull)

| phase | stim_mean | ctrl_mean |
|-------|-----------|-----------|
| STIM | 6.03 | 5.60 |

stim-frac 0.00 — NOT because the write failed (it didn't: stim=6.03, lattice + write intact) but
because CONTROL ALSO latched (ctrl=5.60) even with the background culled EVERY tick and only stim
injected (LOC arm). Mechanism: emit_speed=30, dt=0.5 → emitted vibrations travel 15 units in ONE
tick = exactly the stim→control distance, so stim's firing emissions reach control BEFORE the next
cull, charge control atoms → control co-fires → control bridges latch. The contamination is FAST
EMISSION TRANSIT, faster than the cull interval — quieting the background alone can't stop it.

**The untested fix.** G64 tried LOCAL emission (low emit_speed) but on the ACTIVE substrate (background
drowned it). G84 quieted the substrate but emit_speed=30 still reached control. The combination —
QUIET substrate (control not self-active) + LOCAL emission (write field stays near stim, never reaches
control) — addresses BOTH routes and is untested. G85.
