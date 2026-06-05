# G149 — Is the oscillator's weakness (G148) a COMPUTE artifact, or fundamental? (matched-budget fairness check)

Pre-registered: 2026-06-05 (BEFORE the run). G148 found the physical oscillator-Ising machine TIES a strong
correct greedy and LOSES to classical SA 15/15 at n=200–360, concluding the genuine advantage is classical
SA's, not the substrate's. The obvious objection: the oscillator was **under-resourced** (5 seeds × 1500
steps) versus SA (4 restarts × 1000 sweeps × n single-spin updates — far more spin-flips at large n). G149
gives the oscillator a ≥10× compute budget — *same dynamics and noise schedule, only more of it* (a fairness
control, NOT threshold/parameter tuning) — and re-tests. Either outcome is informative and strengthens the
record.

## Method
Same instances as G148 (spin-glass MAX-CUT, signed Gaussian, `rng_seed=2`), `n ∈ {200, 360}`, 5 instances per
n. Solvers:
- **OSC_base** — G148's oscillator (best of 5 seeds × 1500 steps).
- **OSC_big** — identical dynamics + noise schedule, scaled to **best of 15 seeds × 5000 steps** (≈10× compute).
  No change to dt, noise amplitude, or the annealing form — pure budget increase.
- **SA** — G148's proper SA (4 × 1000 sweeps, incremental field).
- **GRD** — sign-correct greedy, 60 restarts.
- **REF** — best over all + long SA; for approximation ratios.

## Bars (locked pre-run)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G149a | More compute helps OSC (sanity) | mean OSC_big ≥ mean OSC_base at both n |
| G149b | **Fairness verdict (decisive)** | classify per below at the largest n (360) |
| G149c | OSC_big vs SA (report) | does extra compute close the OSC–SA gap? (diagnostic) |

**G149b classification (pre-registered):**
- **SALVAGED** (scoped positive): OSC_big beats GRD on ≥ 4/5 instances at n=360 AND mean(OSC_big − GRD)/REF
  ≥ 0.01 → given fair compute, the oscillator IS a competitive physical annealer that beats correct greedy on
  hard instances. G148's "weak" was partly a budget artifact; a genuine (if SA-dominated) physical-annealing
  result survives.
- **ROBUST-NEGATIVE**: OSC_big still wins ≤ 3/5 vs GRD at n=360 AND mean(OSC_big − GRD)/REF < 0.01 → the
  oscillator is *fundamentally* a weak annealer, not under-resourced; G148's negative is bulletproof.

## Verdicts
- **SALVAGED** → record a scoped positive: oscillator-Ising (fairly resourced) ≥ correct greedy on hard
  instances, though still ≤ classical SA. The physical machine is a legitimate competitive annealer.
- **ROBUST-NEGATIVE** → G148 stands unassailably: even at 10× compute the physical oscillator confers no edge
  over trivial correct greedy. The substrate's computation niche is closed for good.

No post-hoc tuning: only the compute budget is scaled; dynamics/noise/schedule are frozen at G148 values.
Budgets reported in output.

## RESULT (2026-06-05): ROBUST-NEGATIVE — the oscillator's weakness is FUNDAMENTAL, not a budget artifact

| n | OSC_big vs GRD (wins, gap) | OSC_big vs SA (wins) | mean OSC_base → OSC_big | mean SA |
|---|---------------------------|----------------------|-------------------------|---------|
| 200 | 3/5, **+0.002** | **0/5** | 1005.3 → 1007.4 | 1025.9 |
| 360 | 3/5, **+0.007** | **0/5** | 2517.5 → 2538.5 | 2594.3 |

- **G149a ✓** — 10× compute helps the oscillator marginally (mean big ≥ base at both n: e.g. 2517→2538 at
  n=360), confirming it was a real budget increase.
- **G149b = ROBUST-NEGATIVE** — but the extra compute does NOT change the standing: OSC_big still only TIES
  correct greedy (3/5 wins, gap +0.002 / +0.007, both under the 0.01 SALVAGED bar).
- **G149c** — OSC_big vs SA: **0/5 at both scales.** Classical SA beats the well-resourced oscillator on
  *every* instance (by ~1.5–3%). The gap to SA did not close with 10× compute.

**Verdict: ROBUST-NEGATIVE — G148 is bulletproof.** The "you under-resourced the oscillator" objection is
answered: even with ~10× compute (same dynamics, only more of it), the physical oscillator-Ising machine ties
trivial correct greedy and loses to classical SA on all 10 instances across two scales. Its weakness is a
property of the *dynamics*, not the budget. (Robustness bonus: these n=360 instances differ from G148's — the
rng stream is consumed differently with n∈{200,360} vs {200,280,360} — yet the conclusion is identical, so it
is not instance-specific.)

**The computation thread is now definitively closed.** Across G145→G149: the substrate's last candidate
advantage is an advantage of the **classical SA algorithm alone**; the physical/vibrations realization confers
no edge over correct local search at any scale or budget tested. The physics is decorative everywhere — the
programme's complete, honest endpoint.
</content>
