# BP-C6 (G174) — structure-coupled break of linear strain invariance

**Status: SIGNED OFF 2026-08-13 (round 15: B and D explicit after their
single amendments were incorporated — exact band operationalization (max
envelope, std reported) and the partial-firing INCONCLUSIVE clause; A and C
conditional sign-offs whose written v2 conditions — endpoint collapse at
k_p=k, mirror degeneracy, named artifact classes + counterbalancing,
treatment-amplitude bands, rescoped NULL text — are all incorporated and
checked line by line; E/F absent after two pings) — committed before any
data (D2). Bars final per D3.**

Review history (kept deliberately — the withdrawn states are the lesson):
- **v1 withdrawn:** the FOLLOWING quotient was the pattern-independent
  constant k_p/(k+k_p) in the linear regime (guaranteed INCONCLUSIVE at
  k_p=0.5) and its congruent cell was a 0/0 degeneration → Trap #6 (metric
  non-degeneracy: evaluate the metric at EVERY design cell; register
  analytic point predictions per cell), adopted in the pattern doc.
- **v2 revised in review, three independent findings:** (a) with k_p = k
  the treatment endpoint collapses to uniform 8.5 in BOTH cells
  (r_i + Q_i = 17 under complement targets → g\* = (r+Q)/2 = 8.5) — the
  primary metric was endpoint-blind by construction; (b) for the strictly
  alternating pattern, complement = spatial reverse, so the two treatment
  cells were MIRROR images — any local force-law nonlinearity of any order
  is mirror-symmetric, forcing Δ_T = 0 and a false NULL with irreversible
  consequence; (c) two order/position artifact classes in the actual
  integrator and field code can fabricate Δ_T without structure coupling
  (§5) — requiring counterbalancing, not extrapolated gates.

## 0. Rung-C reopen justification (charter clause)

Rung C closed PARTIAL with "reopen only via new primitive or named §4.8
ports." C1–C5 predate PRIM14. Under the old single global r_eq there was no
STRUCTURAL channel for formation-time geometry; the tested injection class
could not inscribe formation history into geometry. PRIM14 (per-bond
formation-frozen rest lengths) is that channel and postdates the closure.
This is NOT a re-run of the injection dual-drive frequency family (no
oscillatory drive, no frequency/period/threshold axis — the closure's §3.4
prohibition targets designs varying P_L/P_R, bands, or thresholds; stored
geometry + mechanical strain probe is a different mechanism class). Naming:
the closure document's §3.4 forbids a differently-built experiment also
labeled "C6" (injection class) — this BP-C6 is unrelated to that forbidden
design; the ID collision is noted here to prevent a false grep match.

PRIM14 provides the CHANNEL (structure can hold a frozen pattern). Whether
drive HISTORY writes that pattern is the separate, untested link reserved
for C7 — nothing here claims it.

## 1. The one question (D1)

> Does the substrate's response to a structure-incongruent strain probe
> DEVIATE from the analytic linear-spring invariant in a way COUPLED to the
> stored pattern — i.e., is there any channel (nonlinearity, bond-window
> events, transverse buckling, transient dynamics) through which frozen
> internal structure shapes the response beyond shifting the linear
> minimum?

Motivation, stated honestly: in the ideal linear regime the Hessian is k·I
regardless of the stored pattern — rest lengths move the MINIMUM, not the
STIFFNESS — so ideal-spring "compliance selectivity" is IMPOSSIBLE and a
naive selectivity experiment measures its own guard rails. The realizable
question is whether the REAL substrate breaks that invariance in a
structure-coupled way. A detected break names the mechanism a genuine
selectivity experiment (C6b) would build on; a clean match closes the
compliance angle of the reopen with an analytic explanation, not a
measurement miss. The write is ENGINEERED (register-line procedure,
disclosed); claimed is only the differential response. The probe is
congruent/incongruent to the stored STRUCTURE — no history is involved.

## 2. Design

Legacy substrate, register-line conventions (calibration_session3 base).
Chains of 7 carriers / 6 gaps, valence 2, centered, separate lanes,
cross-lane exclusion by census; SHORT=6.5, LONG=10.5, UNIFORM=8.5;
bridge_tension_k k=8.0, damping 0.95; formation freeze + census during
probe (write channel closed — register traps #1/#2).

Patterns: **PA = [S,S,L,L,S,L], PB = complement(PA) = [L,L,S,S,L,S]**
(equal multiset → equal span), U = [8.5 ×6]. NOT the strictly alternating
pattern: there complement = spatial reverse, and the mirror degeneracy
blinds the symmetry axis (v2 finding (b); symmetry walk in §4).

**Probe:** for T_probe=800 ticks, positional springs of stiffness
**k_p = k/3 = 8/3 — DERIVED, not chosen: k_p = k·F\*/(1−F\*) at design
point F\* = 0.25** (documented force balance, not taken from any run).
F\* = 0.5 (k_p = k) is FORBIDDEN by the endpoint-collapse finding: under
complement targets r_i + Q_i = 17, so k_p = k gives g\* = 8.5 uniform in
both treatment cells — endpoint blind. At k_p = k/3: g\* = (3r + Q)/4,
treatment endpoints 7.5/9.5 (pattern survives), residual factor
k/(k+k_p) = 3/4. **Q = P is forbidden everywhere** (Trap #6).

With m := PA − PB = [−4,−4,+4,+4,−4,+4] per gap:

| Cell | mismatch (gap_start − Q) | linear point prediction F_800 |
|------|--------------------------|-------------------------------|
| PA @ Q=PB | m | 0.25 |
| PB @ Q=PA | −m (exact negative) | 0.25 |
| U @ Q=PA | −m/2 | 0.625 |
| U @ Q=PB | +m/2 | 0.625 |
| U @ Q4 = 8.5·1 − m | m | 0.25 |
| U @ Q4′ = 8.5·1 + m | −m | 0.25 |

The U@Q4 pair (targets in {4.5, 12.5}, m-pattern) is the AMPLITUDE- AND
PATTERN-MATCHED structure-free control: a band calibrated only at mismatch
2 would be too narrow for mismatch-4 cells if noise scales with excursion —
biasing toward false DETECTED. Its mismatch vectors equal the treatment
pair's, so its symmetry status matches too. Q4 equilibria at k_p = k/3 are
(3·8.5 + 4.5)/4 = 7.5 and (3·8.5 + 12.5)/4 = 9.5 — well inside the bond
window; the harness still logs the maximum transient gap excursion per
cell and flags ≥ 11.5 (window-event risk, reported; asymmetric firing
within a pair is reported alongside the verdict).

Point predictions are STATED AS APPROXIMATE: the integrator's in-loop
damping (§5a) makes the true fixed point a weighted balance; deviations
from the analytic values are classified as integrator artifact unless they
are structure-coupled (i.e., they appear in Δ, not only in F).

**Metric (fixed normalizer — no self-normalization):**
F_t(cell) = 1 − mean_i(|gap_i(t) − Q_i|) / D with **D = 4.0** constant
across all cells. Full F(t) trajectories and raw per-gap residuals logged.

**Two co-primary read-outs** (both, per cell): the endpoint **F_800** and
the mid-transient snapshot **F_100** (the transient is where a dynamic
structure coupling would live; the endpoint is where a static one would).

**Axes:**
- **Symmetry (the structure-coupling axis):** treatment mismatch vectors
  are exact negatives; linear dynamics (any damping, any mass coupling) is
  sign-flip invariant, so Δ_T = |F(PA@PB) − F(PB@PA)| = 0 analytically —
  and the mirror degeneracy that would also force Δ_T = 0 under local
  nonlinearity of any order is broken by the pattern choice. Computed for
  both read-outs: Δ_T^800, Δ_T^100; likewise Δ_U per U pair.
- **Point-prediction axis (secondary, report-only):** |F − F_pred| per
  cell; symmetric deviations = substrate/integrator nonlinearity WITHOUT
  structure coupling.

**Counterbalancing (order/position artifacts, §5):** every treatment cell
runs in TWO configurations: baseline, and counterbalanced (lanes swapped
AND slot-allocation order reversed). CB(cell) = |F_baseline − F_cb| per
read-out. The U@Q4 pair runs counterbalanced too (same gate).

## 3. Two-stage protocol and bars (final on sign-off; D3)

**Stage 0 — band calibration (U only, treatment sealed):** seeds
{42, 7, 13}; cells U@PA, U@PB, U@Q4, U@Q4′, the Q4 pair in both
configurations. **Band operationalization (exact, reproducible):** for
amplitude pair p ∈ {2, 4}, seed s and read-out t ∈ {100, 800}, let
Δ_U^t(p, s) = |F_t(U@Q_p; s) − F_t(U@Q_p′; s)| (same seed, same
configuration). Then band_sym^t = max(0.02, 3 · max_{p,s} Δ_U^t(p, s)) and
band_point^t = max(0.02, 3 · max_{cell,s} |F_t(cell; s) − F_pred(cell)|)
over the U cells. The max (not the standard deviation) is deliberate:
three seeds cannot estimate a tail, and the max is the conservative
envelope; per-cell seed standard deviations are additionally REPORTED. **Seal protocol (order must
be provable, not asserted):** after Stage 0 the band values are written
into this section and committed as their OWN commit (this file only)
BEFORE any Stage-1 code runs; the Stage-1 harness READS the bands from the
committed file (never recomputes) and logs that commit's SHA into the
verdict artifact.

**Stage 1 — measurement:** fresh seeds {101, 102, 103}; treatment cells in
both configurations + U cells (12 treatment runs + 18 U runs incl. CB);
censuses (write + probe, zero cross-lane bonds, formation freeze verified,
minimum non-neighbor distance logged — substantiates the atom-repulsion
all-clear of §5c).

- **STRUCTURE-COUPLING DETECTED:** on at least one read-out t:
  Δ_T^t ≥ band_sym^t on every seed with consistent sign IN BOTH
  configurations, AND CB(treatment) < band_sym^t on every seed, AND
  Δ_U^t < band_sym^t on every seed, AND censuses valid. Consequence:
  mechanism localization reported (transient shape, per-gap residuals);
  successor pre-reg C6b may frame genuine selectivity on the named
  mechanism.
- **INVARIANT (NULL):** Δ_T^t < band_sym^t on every seed for BOTH
  read-outs, controls and censuses clean. Supported statement (exactly
  this, no more): structured and structure-free chains deviate
  INDISTINGUISHABLY from the linear invariant at equal strain amplitude
  and matched mismatch pattern. Consequence: the compliance angle of the
  PRIM14 reopen is CLOSED; Rung C stays closed unless a different
  mechanism class is named in advance. Point-prediction deviations
  reported either way.
- **INCONCLUSIVE:** CB(treatment) ≥ band_sym^t (order/position artifact —
  §5 classes live), or Δ_U ≥ band_sym^t (probe-intrinsic artifact), or
  census breaks, or Stage-0 bands degenerate (band_sym^800 > 0.2), or
  **partial firing**: any exceedance of band_sym^t WITHOUT full seed
  consistency or WITHOUT consistent sign (e.g. 2 of 3 seeds, or
  sign-flipping exceedances) — the resolution cannot separate coupling
  from run-to-run variation. Per-seed Δ_T^t raw values are reported, and
  explicitly: this outcome is NOT partial evidence for coupling and does
  NOT license a C6b successor.
- **FAIL:** cross-lane bonds after a passed gate, or invalid write census.

## 4. Coupling walk + metric walk + symmetry walk (traps #5, #6)

Coupling: the probe addresses gaps positionally; the coupled variable is
the per-gap mismatch vector, distinct per cell by construction —
arrangement is coupled here, unlike the G173 readout.

Metric at every cell: D = 4.0 > 0 constant; every cell's initial mean
mismatch ∈ {2, 4} > 0; predictions {0.25, 0.625} interior; treatment
endpoint geometry 7.5/9.5 retains the pattern (no k_p = k collapse) — no
cell undefined or trivially satisfied.

**Symmetry walk (Trap #6 one level up: evaluate the symmetry argument
under the ACTUAL physical transformation between cells — a chain mirror
maps (P, Q) → (reverse(P), reverse(Q)) — not merely the algebraic relation
between mismatch vectors).** Verified inequalities:
- reverse(PA) = [L,S,L,L,S,S] ≠ PB — treatment cells NOT mirror-related;
- reverse(PB) = [S,L,S,S,L,L] ≠ PA (checked both ways);
- reverse(Q4) ≠ Q4′ (same m-pattern) — the matched U pair equally
  non-mirror-related.
Had any equality held, mirror-symmetric physics of ANY order would force
the corresponding Δ = 0 and the axis would be blind to its target.

## 5. Known artifact classes (named before data; the CB gate exists for
these)

- **(a) Integrator order-dependence:** the bond loop applies damping
  INSIDE the per-bond iteration (world/bridges.py:184-193) — an interior
  carrier's earlier-indexed bond force is damped once more than its
  later-indexed one; the tick fixed point is a weighted balance with a
  direction along ascending bond index that does NOT mirror with the
  chain, and interior carriers are damped twice per tick (0.9025) vs ends
  once (0.95). Can fabricate Δ_T; caught by allocation-order reversal in
  CB. Point predictions are approximate under this (stated in §2).
- **(b) Scale-repulsion field:** apply_scale_repulsion
  (world/physics.py:1585) is a 1/r² pair term over ALL living nodes
  (repulsion_k 100.0), no bonded-pair exclusion — different lanes see
  different field gradients; Δ_U cannot catch a lane effect (U measures
  its own lane). Caught by lane swap in CB.
- **(c) Atom repulsion:** default k = 0.0, active only under r_2·0.5 with
  bonded pairs excluded; next-nearest neighbors sit ≈ 14–21 under these
  patterns. All-clear ASSERTED, and substantiated by logging the minimum
  non-neighbor distance in the census.

## 6. Predictions (calibration, before data)

- Stage-0 bands at the 0.02 floor: 60%; amplitude-4 noise > amplitude-2
  noise: 60%.
- Verdict: INVARIANT (NULL) 50%, INCONCLUSIVE 30% (the CB gate is new and
  §5a is a REAL directional term — it may well fire), DETECTED 15%,
  FAIL 5%.
- Most-likely failure mode: INCONCLUSIVE via CB(treatment) ≥ band —
  integrator order-dependence visible at mismatch 4.
- If DETECTED: C6b (selectivity on the named mechanism), then C7
  (history → structure via drive statistics) — attribution order per the
  G170 lesson.

## 7. BELIEF_PATH §4 row text, pre-scripted per verdict (scope discipline)

- DETECTED: "R8 CLOSED PARTIAL, reopen in progress: structure-coupled
  invariance break POSITIVE scoped (engineered write, mechanical probe;
  read-out: <F_100 transient | F_800 endpoint | both> — dynamic and static
  coupling ground DIFFERENT C6b successors); rung stays closed until C6b
  selectivity + C7 emergent write."
- NULL: "R8 CLOSED PARTIAL; PRIM14 compliance angle closed (structured and
  structure-free chains indistinguishable from the linear invariant at
  equal amplitude and matched mismatch pattern); reopen requires a new
  named mechanism class."
- INCONCLUSIVE/FAIL: row unchanged; LOGBOOK only.

## 8. Budget

Harness (register write + probe springs + F(t)/residual logging + CB
configurations): 1 h. Stage 0: minutes. Stage 1: ~30 min. Verdict +
LOGBOOK + FRONTIER + BELIEF_PATH: 30 min. **Realistic 2 h → hard cap 4 h.**

## 9. Out of scope

Selectivity claims (C6b), emergent write from drive statistics (C7),
retention, Flux substrate, any frequency/period drive axis (stays closed).
