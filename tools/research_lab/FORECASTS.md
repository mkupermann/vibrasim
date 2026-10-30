# Research lab — pre-registered forecasts

**Programme claim (unchanged):** matter acquires function only if its organisation
changes the field that supplies the energy required to maintain that organisation.

**Causal loop under test:** `field → absorbed work → local bond turnover → geometry → field`

These are exploratory mechanism experiments, not frozen P0–P3 runs. Forecasts are
written before the code that produces the data. Misses are scored honestly and the
forecast *method* is enhanced — thresholds are not retro-fitted to force a PASS.

---

## Shared assumptions (A0)

| ID | Assumption |
|----|------------|
| A0.1 | Bonds have fixed finite lifetime `τ_b` and cost `E_form` to form |
| A0.2 | Sustained occupancy requires capture income ≈ `E_form / τ_b` per live bond |
| A0.3 | Capture is rectified positive work `η · max(0, F·r)` (P2 law) unless stated |
| A0.4 | Survival `S` = ∫ N_live dt over a fixed horizon |
| A0.5 | Geometry enters only through a stated constitutive law |

---

## Experiment 1 — Law R (resonant function)

**Question:** Under a sustained source and income-limited renewal, does survival
vs geometry show an *interior peak* (organisation helps only near χ*)?

**Mechanism:** driven damped matter oscillator; χ = detuning `ω_m − ω_drive`.

| ID | Forecast (written before run) |
|----|-------------------------------|
| F1.1 | `S(χ)` attains its maximum at `χ*` with `|χ*| ≤ 0.5` |
| F1.2 | Slope left of peak `> 0`, right of peak `< 0` |
| F1.3 | Peak − trough ≥ 5.0 bond-time units |
| F1.4 | Cut drive (source off) ⇒ peak collapses (range < 2.0) |

**Assumption that would be falsified:** resonance of capture is the geometry→function map.

---

## Experiment 2 — Competition under a shared budget

**Question:** Can one organisation outlast another *because of* how it shapes a
shared field?

**Mechanism:** two geometries (A: tight pair near source, B: wide pair) share one
energy budget. Live bonds raise local transport (Law C). Feedback can be cut.

| ID | Forecast |
|----|----------|
| F2.1 | With feedback on, late survival shares differ by ≥ 0.15 |
| F2.2 | The winner is the geometry that raises its own capture share |
| F2.3 | Cut feedback ⇒ share difference shrinks below 0.08 |
| F2.4 | Swapping geometry parameters swaps the ranking |

**Assumption that would be falsified:** relative function under resource constraint is geometry-dependent and feedback-mediated.

---

## Experiment 3 — Lock sign (P2 reduction)

**Question:** Does a field-bond lock reduce sustainable bond-time vs no lock?

**Mechanism:** structured capture on field difference; lock = spring + difference damping.

| ID | Forecast |
|----|----------|
| F3.1 | `S(k_f) − S(no lock) ≤ 0` for all `k_f > 0` |
| F3.2 | Closed box shows a steeper drop than driven |
| F3.3 | At matched `k_f>0`, conservative lock has `S ≥` dissipative lock (a conservative spring is not a pure lock) |

**Assumption that would be falsified:** P2-style locking is non-positive for organisation.

---

## Forecast method v1

- Each forecast is a binary or inequality check on a named metric.
- Score = mean(hit) over all forecast IDs in an experiment.
- **Enhancement rule:** if score < 1.0, record the miss pattern, write forecast
  method v2 in `FORECAST_LOG.md`, and re-run the *same* physics with the improved
  forecast. Never change acceptance thresholds upward/downward to convert a miss
  into a hit.

## Forecast method v2 (after E2/E3 first-run misses)

1. Report **effect size + seed spread** alongside every pass/fail.
2. Competition geometry is **only** live-bond transport gain; capture efficiency
   is shared physics (0.85). Scarcity is real: source inflow 0.008 < 2·E_form/τ_b.
3. `swap` exchanges transport gains (A↔B), not identical parameters.
4. F2.2 means: winner has **higher total captured income** (share > 0.5).
5. Split monotone vs peak forecasts when a curve can saturate at the horizon
   (E3 conservative-lock still may miss if S is horizon-clipped).

---

## Experiment 4 — N-geometry tournament (competition)

**Question:** With 4 transport geometries on one scarce budget, is ranking stable and transport-ordered?

| ID | Forecast |
|----|----------|
| F4.1 | spread (max−min bond-time) ≥ 10 |
| F4.2 | winner has the largest transport gain |
| F4.3 | cut feedback ⇒ spread < 5 |
| F4.4 | income ranking matches survival ranking |

## Experiment 5 — Law R under noise (σ=0.05)

| ID | Forecast |
|----|----------|
| F5.1 | peak `|χ*| ≤ 0.5` with noise |
| F5.2 | peak-trough spread ≥ 5 |
| F5.3 | drive-off spread < 2 |

## Experiment 6 — P2 constitutive reduction

**Question:** Does a *P2-faithful* field-bond (conservative spring, rest frozen
at formation, rectified capture) give the same non-positive lock sign?

| ID | Forecast |
|----|----------|
| F6.1 | For each `k_f>0`, `S(feedback) − S(no_feedback) ≤ 0` in the closed box |
| F6.2 | Mean contrast over `k_f>0` is `< 0` (strictly negative, matches P2 sign) |
| F6.3 | Pure conservative spring (`kf_damp=0`) is less negative than dissipative (`kf_damp=0.5`) at the same `k_f` |

### E6b — P2 reduction, driven source (confirmation)

Closed box gave non-positive lock contrast (P2 sign). An exploratory driven
pilot flipped positive. **Forecast for a fresh-seed confirmation run** (written
after the pilot, before the confirmatory seeds):

| ID | Forecast |
|----|----------|
| F6b.1 | Driven: `S(feedback) − S(no_feedback) > 0` for `k_f ≥ 0.2` (lock helps under drive) |
| F6b.2 | Closed vs driven lock contrast have **opposite signs** (regime dependence) |
| F6b.3 | Confirmation seeds reproduce pilot magnitude within 15% |

## Experiment 7 — lock-contrast regime map

**Question:** Where does lock contrast `Δ = S(feedback)−S(no_fb)` cross zero
between closed box and continuous drive?

| ID | Forecast |
|----|----------|
| F7.1 | Δ ≤ 0 for drive amplitude 0 (closed) at `k_f=0.5` |
| F7.2 | Δ > 0 for drive amplitude ≥ 0.4 at `k_f=0.5` |
| F7.3 | There is a mid amplitude where |Δ| is minimal (transition band) |

## Experiment 8 — resonant competition

**Question:** On a scarce shared budget, does the *near-resonant* geometry
(χ≈0) outlast a detuned one when live organisation raises transport?

| ID | Forecast |
|----|----------|
| F8.1 | Near-resonant (χ=0) bond-time − detuned (χ=1.2) ≥ 10 |
| F8.2 | Winner is the resonant geometry |
| F8.3 | Cut transport feedback ⇒ gap shrinks below 5 |
| F8.4 | Swapping detunings swaps the winner |

### E8b — pure transport control (φ=1 both)

After E8 F8.3 miss: isolate transport from resonance.

| ID | Forecast |
|----|----------|
| F8b.1 | With φ=1 for both, feedback-on gap ≥ 10 (transport alone ranks) |
| F8b.2 | With φ=1 and feedback cut, gap < 5 |
| F8b.3 | With φ=1 and feedback cut, gap < feedback-on gap |

## Experiment 9 — 2×2 factorial (resonance × transport)

**Question:** Are φ (resonance) and transport main effects additive, or is
there interaction?

| ID | Forecast |
|----|----------|
| F9.1 | Main effect φ: gap(φ on, transport on) − gap(φ off, transport on) > 10 |
| F9.2 | Main effect transport: gap(φ on, transport on) − gap(φ on, transport off) > 10 |
| F9.3 | Interaction: combined gap < sum of the two single-factor gaps (sub-additive) |
| F9.4 | Both-on winner is the geometry with χ=0 *and* high transport |

## Experiment 10 — rectifier vs signed work (Law R)

**Question:** Is the resonance peak an artifact of rectified capture `max(0,Fr)`?

| ID | Forecast |
|----|----------|
| F10.1 | Rectified capture: peak-trough spread ≥ 5 (replicates E1) |
| F10.2 | Signed mean-work capture (`mean(F·r)` clipped at 0 only if total negative): spread ≥ 5 |
| F10.3 | Peak location stays `|χ*|≤0.5` for both rules |
| F10.4 | Drive-off collapses both spreads below 2 |

## Experiment 11 — economic regime robustness

**Question:** Do E1/E3 signs hold when `E_form/τ_b` (amortized cost) changes?

| ID | Forecast |
|----|----------|
| F11.1 | Law R peak stays in `|χ*|≤0.5` at cost ratio 0.003 and 0.012 (vs 0.006 default) |
| F11.2 | Lock contrast (closed, k_f=0.5) stays ≤ 0 at both ratios |
| F11.3 | Peak-trough spread stays ≥ 5 at both ratios |

## Experiment 12 — 4-way mixed geometry tournament

**Question:** With four geometries differing in (χ, transport), does survival
rank by the **product** φ(χ)·transport?

| ID | Forecast |
|----|----------|
| F12.1 | Ranking matches order of φ(χ)·gain (Spearman=1) |
| F12.2 | Spread max−min ≥ 10 |
| F12.3 | Top-ranked has both near-zero χ and high gain |
| F12.4 | Cut feedback ⇒ spread < 5 |

## Experiment 13 — dual-map null (cut transport *and* φ)

| ID | Forecast |
|----|----------|
| F13.1 | Cut transport only ⇒ spread ≥ 10 (φ remains) |
| F13.2 | Cut φ only (flat φ) + equal transport ⇒ spread < 5 |
| F13.3 | Cut **both** maps ⇒ spread < 5 and Spearman undefined/near 0 |
| F13.4 | Restore both maps on same seed ⇒ ranking matches E12 order |

## Experiment 14 — self-boost null + ensemble symmetry

| ID | Forecast |
|----|----------|
| F14.1 | Cut live-bond self-boost (`g` constant 0.03) + flat φ ⇒ single-seed spread < 5 |
| F14.2 | Ensemble mean of bond-time over 20 seeds has range < 5 for identical geometries |
| F14.3 | With self-boost restored, ensemble range ≥ 10 (symmetry still broken in mean) |
| F14.4 | G1 (best φ·gain) has highest ensemble mean when both maps on |

## Experiment 15 — asymmetry dose-response

**Question:** How small a geometric difference still produces stable ranking?

| ID | Forecast |
|----|----------|
| F15.1 | Δgain=0.02 (almost equal) still yields ensemble range ≥ 5 |
| F15.2 | Δχ=0.1 still yields ensemble range ≥ 5 |
| F15.3 | Asymmetry → 0 ⇒ range → 0 (monotone in dose) |
| F15.4 | At equal geometry (dose=0) range = 0 exactly |

## Experiment 16 — minority invasion

**Question:** Can a high φ·gain geometry starting as 1 of 4 take over?

| ID | Forecast |
|----|----------|
| F16.1 | Start 1×G1 + 3×G4: G1 ends with ≥ 50% of total bond-time |
| F16.2 | Start 3×G1 + 1×G4: G1 keeps ≥ 50% share |
| F16.3 | Start 4×G4 (control): no invasion artefact, shares ≈ 25% |
| F16.4 | Start 1×G4 + 3×G1: G4 share < 25% |

---

## Live viewer contract

The dashboard shows only values written by `live_lab.py` from the running
experiment state. No mocked series. Progress is `completed_steps / total_steps`
of the actual integrator. Forecast cells light up only after the corresponding
metric is computed from stored trajectories.
