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
