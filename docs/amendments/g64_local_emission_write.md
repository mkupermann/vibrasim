# G64 — Local emission: a spatially self-limiting write (re-attacking the memory deadlock)

Pre-registered: 2026-06-02 (BEFORE the run). The memory deadlock is write=broadcast=leak. The
programme tested only the two EXTREMES of emission: BET-099 (n_emit=8, emit_speed=30 → vibrations
fly far → broadcast → contaminates control) and BET-100 (n_emit=0 → no broadcast but the co-firing
WRITE dies too). The middle — emission that is KEPT but made SHORT-RANGE (low emit_speed) so a
firing atom co-fires only its IMMEDIATE bridged neighbours and the emission does NOT reach the
distant control region — was named as a candidate resolution (BET-103) but never actually run.
This is the spatial form of a "directional self-limiting write": the write co-activates local
neighbours (so it writes) but cannot propagate far (so it does not leak).

## Method
BET-099 correlation-memory protocol (neuron_dynamics + correlation plasticity + persistence),
sweeping `emit_speed` ∈ {4, 8, 16} (vs the flooding 30). Arms: LOC + UNI at each speed.
Fraction-selective metric (BET-100): a checkpoint is selective if stim_mean>3 AND ctrl_mean<3.
Seeds: 42 (single per the BET-099 protocol; replicate any pass across seeds before claiming it).

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G64a | Some speed WRITES selectively | ∃ emit_speed: LOC fraction of STIM checkpoints selective ≥ 0.5 |
| G64b | …and RECALLS persistently | the SAME speed: LOC fraction of POST checkpoints (≥ stim_end+2000 s) selective ≥ 0.5 |
| G64c | …with the uniform control failing | the same speed: UNI POST selective fraction < 0.25 |

PASS = G64a–c at one emit_speed → local emission resolves the write/contaminate tension: a
spatially self-limiting write gives the programme's first SELECTIVE PERSISTENT memory. This would
BREAK the deadlock (or at least its firing-channel form) and reopen the cognition path. If it
passes, replicate across seeds (G65) before any milestone claim. NULL: if no speed both writes and
recalls selectively, local emission is insufficient — the contamination is not purely emission
range (e.g. bistable-well drift, per G57), and the deadlock is deeper. Honest either way. No
post-hoc threshold tuning (the speed sweep is pre-registered; "works" = all three bars at one speed).

## RESULT (2026-06-02): NULL — local emission insufficient; leak is control CO-FIRING, not emission transit

| emit_speed | LOC stim-frac | LOC post-frac | UNI post-frac | fire ratio |
|------------|---------------|---------------|---------------|------------|
| 4 | 0.17 | 0.00 | 0.00 | 196 |
| 8 | 0.17 | 0.44 | 0.56 | 116 |
| 16 | 0.17 | 0.20 | 0.50 | 25 |

No working speed → **NULL.** Even at low emit_speed the control region's bridges latch to 3–4
during STIM (stim/ctrl overlap ~2–4), and the uniform control is often MORE "selective" than LOC
(noise). Short-range emission did NOT prevent control potentiation.

**This rules out the spatial/propagation form of the fix.** The contamination is not emission
*transit* (range-limiting it changes nothing) — it is that CONTROL ATOMS CO-FIRE on their own (from
the ambient/residual field) and their bridges latch regardless of stim's emission range. The leak
is in the FIRING COMPETITION, not propagation. Next (G65): the INHIBITION half — a competitive
firing rule (k-winner-take-all) that suppresses weakly-driven control firing so only strongly-driven
stim atoms fire and co-fire. (Honest note: G64/G65 test genuinely NEW mechanisms vs the deadlock;
so far G64 confirms it.)
