# G15F-1 — Flux dream consolidation (engineered pattern tagging + conserving replay)

**Status: SIGNED OFF 2026-08-10, no conditions — committed before any data generation (D2).**
**Verdict 2026-08-10: NULL-T** — gate G-T missed on 3/3 seeds (N_T = {1, 0} vs ≥20 per
pattern); consolidation never testable. Judged against the unchanged bars below; full
case in LOGBOOK 2026-08-10, raw data in archive/run-logs/g15f/. No retry under this ID.
Per D3 any bar change from here on requires a new ID. Per DISCIPLINE_SHARP §4 this is
an engineering side-track amendment (flux capability parity), NOT a belief-path rung;
re-admitted with the sign-off. Bars below are final.

## 1. The one question (D1)

> With a G10-style pattern-tagging path ported to Flux (engineered write, named as such
> per D5) and energy-conserving dreaming, does offline replay consolidate trained
> engrams — i.e. do tagged node populations survive a rest phase better under dream
> replay than under (a) energy-matched unspecific injection and (b) nothing — with the
> no-engram negative control failing?

Context: the 2026-08-10 flux G15/G16 validation was **NULL (vacuous)** — nothing in
Flux assigns `pattern_id != 0`, so replay/blending could never fire (LOGBOOK
2026-08-10). Legacy G15 passed its binary structural bars (tests/test_amendment_G15_dream.py,
README.md:231); the free-talent replications BP-C13/C101/C103 were NULL. This amendment
does NOT claim emergence: tagging is an engineered training signal, replay is an
engineered mechanism. The question is whether the engineered mechanism produces the
claimed *function* (selective consolidation) under honest controls.

## 2. Engineering prerequisites (E1–E3; done-criteria, not experiments)

**E1 — pattern tagging (G10 core, minimal port).**
Mirror of Legacy `World.active_pattern_id` (world/state.py:95–105, assignment at
state.py:262): add mutable `Nodes.active_pattern_id: int = 0`, set ONLY by the
training harness; `Nodes.add()` stamps `pattern_id[slot] = active_pattern_id` at
allocation; slot recycling clears the stale tag. Explicitly OUT of scope: bridge-pid
commit (physics.py:374–379), firing-eligibility gate (G12), pid-matched routing.
*Done-criterion:* unit test — nodes allocated while `active_pattern_id=k` carry `k`;
allocated at 0 carry 0; recycled slots don't leak stale pids.

**E2 — energy-conserving dreaming.**
Current `apply_dream` violates the F0 ledger (audit.py invariant:
`E_initial + E_injected == E_quanta + E_nodes + E_exported + binding_heat + decay_heat`,
tol 1e-9): blend nodes are allocated with 50% of combined source energy without
draining sources; replay seeds inject unbooked energy. Fix:
(a) blend = conservative transfer — the new node's energy is drained pro-rata from the
two source populations, net creation exactly 0;
(b) replay-seed energy is returned in the diagnostics dict
(`out["energy_injected"]`) and the caller books it via `auditor.record_injected()`.
*Done-criterion:* `EnergyAuditor.check()` passes at tol 1e-9 over ≥60 simulated s with
dream mode on and ≥1 blend event occurring (blend may be forced by construction in the
test).

**E3 — labeled training harness.**
Region+frequency-restricted floor injection (extension of `inject_hot_floor` with an
x-window), driving the phase protocol in §3. Headless (D7).
*Done-criterion:* smoke shows tagged node populations forming for both labels.

## 3. Protocol (one full run, D8/§5-compliant)

Fixed world: grid 80×40×10 (voxel 1.0), n_quanta 10000, dt 1/60, BindingConfig()
defaults, DecayConfig() defaults (gamma=100, T_decay_crit=0.02), thermal on,
plasticity on. Seeds: **{42, 43, 44}** — the three seeds together are the ONE full
run. One technical smoke (10 s sim, seed 42, any arm) is allowed before the full run
because the harness is new; its numbers carry no evidential weight (D8).

**Phase T (train, 30 s sim, identical in all arms):** alternating 2 s windows.
Even windows: pattern A — injection n=10/tick, energy_per=10.0, freq 800 Hz
(sigma 0) restricted to x∈[0,20], with `active_pattern_id=1`.
Odd windows: pattern B — same rate, freq 3200 Hz, x∈[60,80], `active_pattern_id=2`.
At phase end: record `N_p(T)` = alive node count with pattern_id p, for p∈{1,2}.

**Phase R (rest, 60 s sim), three arms from the identical post-T state:**
- **ARM-D:** external injection off; dream on (`dream_replay_seeds_per_tick=5`,
  `dream_replay_seed_energy=10.0` → 3000 E/s replay injection, booked per E2).
- **ARM-N (energy-matched control):** external unspecific injection 3000 E/s
  (n=10/tick × energy_per=5.0 × 60/s… fixed as n=30/tick, energy_per=1.6667,
  uniform freq 100–10000 Hz, full floor); dream off.
- **ARM-R:** nothing — no injection, dream off.

**Metrics:** `S_p(arm) = N_p(end of R) / N_p(T)` per pattern and seed; blend-node
count in ARM-D (fresh pid, born in phase R); auditor status everywhere.

**NC1 (no-engram negative control):** phase T with identical injection but
`active_pattern_id` held at 0 throughout, then ARM-D. Required outcome: **0 replay
seeds fired and 0 blend events** (the mechanism must gate on trained engrams, not on
any high-energy node). Matched wallclock by construction.

## 4. Pre-registered bars (fixed before any data; D3)

**Gate G-E (validity):** auditor tol 1e-9 holds in every phase of every arm and NC.
Violation → run INVALID, engineering FAIL, no experiment verdict.

**Gate G-T (trainability):** `N_p(T) ≥ 20` for BOTH patterns on ≥2/3 seeds.
Missed → verdict **NULL-T** (tagged engrams can't even form at this protocol; stop,
no retry under this ID).

**Primary verdict (consolidation), judged only if both gates hold:**
- **PASS:** on ≥2/3 seeds and for BOTH patterns:
  `S_D ≥ 1.5·S_N` AND `S_D ≥ 1.5·S_R` AND `S_D ≥ 0.5` — and NC1 clean (0/0).
- **PARTIAL:** the above margins hold for exactly ONE pattern on ≥2/3 seeds, NC1 clean.
- **NULL:** margins `< 1.2` in both comparisons, or `S ≥ 0.95` in all arms (no decay
  pressure at rest — ratios uninformative), or S values not evaluable (all-zero
  denominators after G-T passed).
- **FAIL:** `S_D < S_N` for both patterns on ≥2/3 seeds (energy-matched noise beats
  targeted replay), **or NC1 fires** (replay/blend without engrams → the port's
  gating is broken).

**Secondary bar B (blending; does NOT affect the primary verdict):**
- **B-PASS:** ≥1 blend node with a fresh pattern_id in ARM-D on ≥2/3 seeds, 0 in NC1.
- **B-NULL:** otherwise.

## 5. Predictions (calibration, recorded before sign-off)

- G-T passes: **70%** (flux binding forms nodes fast; tagging inherits trivially).
- Replay fires in ARM-D: **95%**.
- Primary verdict: **NULL 45%** — most likely via "no decay pressure at rest"
  (T falls below T_decay_crit=0.02 with injection off, S≈1 in all arms);
  PASS 25%, PARTIAL 15%, FAIL 10%, NULL-T 5%.
- B-PASS: **60%**.

Single most-likely failure mode: the NULL-via-no-decay path above. If it occurs, the
honest reading is "consolidation is untestable at this decay regime", and any follow-up
(e.g. thermal noise floor during rest) is a NEW pre-registered ID, not a retune.

## 6. Budget (hybrid, §5)

Engineering E1–E3: 3 h realistic. Smoke + full run: <0.5 h wallclock (flux runs
~3–5× real-time here). Analysis + LOGBOOK + FRONTIER in one commit (D10): 1 h.
**Realistic total 4.5 h → hard cap 9 h.** Overrun → FAILED post-mortem in LOGBOOK,
no quiet extension.

## 7. Out of scope (explicit)

Bridge-pid segregation and pid-matched routing (G10 full), G12 eligibility gate,
NREM/REM ratio effects, cross-modal hallucination, and ALL of G16 (self-model /
workspace winner) — G16F gets its own amendment once tagging exists; during this
experiment `apply_self_aware` stays OFF so its binding-alpha homeostasis
(world/flux/self_aware.py:201) cannot confound the arms.
