# G89 — Selective memory via low-intensity write (avoid the runaway)

Pre-registered: 2026-06-03 (BEFORE the run). G88 found a STABLE BLANK STATE (zero input -> blank) but
stim at n=40 triggers a 77850-fire runaway self-ignition that reaches control. Fix: write with LOW
stim intensity so local stim co-firing happens without igniting the cascade -> control stays blank ->
selective. Quiet (cull each tick) + disconnected (compartment_boundary=15) + local emission. Sweep
stim injection n in {2,4,8,20}. Seed 42.

## Bars (locked pre-run — standard memory bars)
| ID | Criterion | Bar |
|----|-----------|-----|
| G89a | Selective write | LOC STIM fraction-selective >= 0.5 |
| G89b | Persistent recall | LOC POST (>= stim_end+2000 s) fraction-selective >= 0.5 |
| G89c | Uniform control fails | UNI POST fraction-selective < 0.25 |

PASS = G89a-c at one n -> SELECTIVE PERSISTENT MEMORY: a low-intensity local write avoids the runaway
that contaminated control, exploiting the stable blank state -> the deadlock BREAKS. Replicate across
seeds. NULL = every intensity either fails to write (too low) or triggers the runaway (too high) ->
the runaway is inseparable from the write. Honest either way. No post-hoc tuning.
