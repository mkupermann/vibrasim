# G66–G68 — Parallel directional/self-limiting-write variants (memory deadlock)

Pre-registered: 2026-06-02 (BEFORE the runs). G64 localized the leak to control atoms CO-FIRING on
their own. G65 tests global k-WTA. These three run in PARALLEL, each a distinct new-mechanism attack
on the same leak (BET-099 correlation-memory protocol; LOC+UNI; seed 42). Generous wall budget so
CPU contention does not truncate.

| BET | Mechanism | Sweep |
|-----|-----------|-------|
| G66 | **Strong refractory** — long refractory prevents reverberation / repeated weak control latching | `t_refractory` ∈ {0.5, 2.0, 5.0} (vs 0.05) |
| G67 | **High firing threshold** — only strongly-charged (stim) atoms cross θ; weak control charge stays sub-threshold | `theta_fire` ∈ {6, 10} (vs 4) |
| G68 | **Combo** — local emission + k-WTA together | `emit_speed` ∈ {5, 10} with `global_wta_k`=10 |

## Bars (locked pre-run — identical to G65, per variant)
A variant PASSES if at one swept value: LOC STIM fraction-selective ≥ 0.5 AND LOC POST (≥
stim_end+2000 s) fraction-selective ≥ 0.5 AND UNI POST fraction-selective < 0.25.

PASS (any variant) = that mechanism gives selective persistent memory → replicate across seeds
before any claim. NULL (all) = none of refractory, threshold, or combined inhibition+local-emission
separates the write from the leak — the deadlock is robust to the full directional/self-limiting
-write family. Honest either way. No post-hoc threshold tuning (sweeps pre-registered).

## RESULT (2026-06-03): all NULL — but G66 (refractory) is a strong NEAR-MISS

| variant | best value | stim-frac | post-frac | uni-post | verdict |
|---------|-----------|-----------|-----------|----------|---------|
| G66 refractory | t_refractory=0.5 | **0.83** | **0.44** | 0.20 | NULL (0.44 < 0.5) |
| G66 refractory | t_refractory=2.0/5.0 | 0.00 | 0.00 | — | starves write |
| G67 threshold | theta_fire 6/10 | 0.00 | 0.04–0.12 | 0.12–0.20 | NULL |
| G68 combo | emit 5/10 + WTA10 | 0.00 | 0.00 | 0.00 | NULL (write starved, fire_ratio 1500–2200) |

All four NULL on the locked bars. But **G66 at t_refractory=0.5 is a strong near-miss**: a clean
SELECTIVE WRITE (stim-frac 0.83) and POST recall 0.44 (just 0.06 under the bar) with the uniform
control failing (0.20). Refractory makes firing DIRECTIONAL (an atom can't immediately re-fire →
co-firing pairs form in a directional sequence within the stim region), which produces a selective
write — what every other firing lever failed to do. It only missed on the recall leak (control
bridges still drift up in POST). That recall leak is exactly what the LEAKY write (G69) targets.

**Conclusion:** the firing-side family fails on the locked bars, but refractory is the first lever
to make the WRITE selective. Next: combine refractory=0.5 (selective write) with the leaky write
(prevents the control recall-leak) — G69 + G69R, run in parallel.
