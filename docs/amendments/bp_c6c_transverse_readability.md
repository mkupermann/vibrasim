# BP-C6c (G175) — mechanical readability of stored patterns in the transverse channel

**Status: DRAFT — under review; commits before any data once signed off.**

## 0. Position in the programme

BP-C6 (G174) closed INVARIANT (NULL): in the axial/collinear configuration
the substrate is exactly linear and stiffness is pattern-blind. The NULL's
pre-scripted consequence requires any successor to name a NEW mechanism
class. C6c names it analytically, before data: **the buckling channel.**

**The mechanism (derivation, part of the registration):** a spring bond at
axial distance h with rest length r exerts, for small transverse deflection
δ, a restoring (or anti-restoring) transverse force with effective
stiffness k_t = k·(1 − r/h) (bond tension T = k(h−r), string stiffness
T/h). The stored pattern IS a k_t pattern once the gaps are held at a
common axial length h:

| gap class | rest r | k_t at h = 9.0 (k = 8) | behavior |
|-----------|--------|------------------------|----------|
| SHORT (taut) | 6.5 | +2.22 | laterally stiff |
| LONG (compressed) | 10.5 | −1.33 | laterally UNSTABLE (buckles) |
| UNIFORM | 8.5 | +0.44 | weakly stable |

This is FIRST-ORDER structure coupling — the C6 invariance proof does not
apply (it lives in the collinear regime this design deliberately leaves).

**Hold length h = 9.0, not 8.5 (Trap #6 at design time):** at h = 8.5 the
U control's bonds sit exactly at rest (k_t = 0) — a degenerate cell with
zero transverse stiffness whose response is undefined drift. h = 9.0 keeps
all three classes interior (+2.22 / −1.33 / +0.44).

**Natural saturation (declared per review):** a buckling LONG gap arrests
ITSELF — deflection grows until the 3D bond length reaches the rest
length: δ\* = √(r² − h²) = √(10.5² − 9²) ≈ **5.41**. The arrest mechanism
is the bond, analytic, not a collision or window event. Registered point
prediction: LONG-gap transverse deflection saturates near 5.41; SHORT-gap
deflection ≈ f/k_t(SHORT) = 0.1/2.22 ≈ 0.05; U ≈ 0.1/0.44 ≈ 0.23.
Ordering LONG ≫ U > SHORT. Trap #6 at the runaway cell: at saturation the
metric is defined and non-trivial (values ≈ 5.4 vs ≈ 0.05 — distinct
interior values, nothing 0/0, nothing forced).

**No-mimic argument (review condition):** the axial holder acts on the
AXIAL COORDINATE ONLY (force applied to the x-component; code-level
guarantee, asserted in the harness) — it has zero transverse component by
construction and cannot produce transverse structure. The lateral probe
force is identical across gaps and chains (structure-free). The only
structure-coupled transverse term is bond tension × geometry — exactly the
claimed channel. Axial residual compliance of the holder (order
k_hold-residuals) is axial and cannot leak into the transverse metric.

## 1. The one question (D1)

> When a written chain is held at uniform AXIAL gap length h = 9.0 and
> perturbed by a small structure-free lateral force, does the transverse
> deflection pattern REPRODUCE the stored rest-length pattern (compressed
> gaps deflect, taut gaps hold) — while the uniform control stays flat?

Scope (review condition): this claims mechanical READABILITY of the stored
pattern through the transverse channel — NOT selectivity (C6b), NOT talent
(Rung C verdict language stays closed-partial).

## 2. Design

Substrate conventions as BP-C6 (calibration_session3 base, k = 8.0,
damping 0.95, valence 2, per-bond rests, three chains PA/PB/U in lanes
20 apart, counterbalancing base/cb as in C6). Patterns PA = [S,S,L,L,S,L],
PB = complement (mirror-degeneracy-free per the C6 symmetry walk — but the
walk is RE-RUN for the new observable in §4, not inherited).

- **Write:** register-line procedure (engineered, disclosed), census.
- **Hold:** per-gap axial springs k_h = 8.0 pulling the SIGNED AXIAL
  PROJECTION Δx_i toward h = 9.0 (x-component force only). END carriers
  pinned fully (position clamp) — the lateral frame reference.
  Axial-uniformity gate (review condition): measured |Δx_i − 9.0| < 0.35
  for every gap at both snapshots, else INCONCLUSIVE (holder failed;
  0.35 = 2·k·max|h−r|/k_h·... derived bound: static residual =
  k·|h−r|/(k+k_h) ≤ 8·1.5/16 = 0.75 — TOO LARGE at k_h = k; therefore
  **k_h = 40 (5k), residual ≤ 8·1.5/48 = 0.25 < 0.35** — derivation
  documented, not tuned).
- **Probe:** constant lateral force f = 0.1 (derived: visibility floor
  δ_SHORT ≈ f/k_t(SHORT) ≈ 0.05, one order above float noise, two under
  saturation) on interior carriers 1–5, ALTERNATING sign (+,−,+,−,+) —
  zero net lateral force and zero mean moment, exciting per-gap shear
  rather than a global arch (an arch would inflate end gaps
  structure-independently). Direction: declared axis ŷ (breaks the
  rotational degeneracy BY DECLARATION; review condition).
- **Duration:** T = 800 ticks; snapshots t ∈ {400, 800} (buckling needs
  growth time; two snapshots guard against measuring only the arrest).

**Observable (direction-agnostic per review):** per-gap transverse
magnitude g⊥_i = |(p_{i+1} − p_i) − ((p_{i+1} − p_i)·x̂) x̂| at each
snapshot. Full trajectories and raw components logged.

**Discriminator (correlation, not scalar delta — review condition):**
per treatment chain: **strict class separation** SEP = min_{LONG gaps}
g⊥ − max_{SHORT gaps} g⊥ (positive = the written pattern is read back);
reported alongside: point-biserial correlation ρ(g⊥, bits) and the
saturation check |median_{LONG} g⊥ − 5.41| (report-only).
U flatness: FLAT_U = (max_i g⊥ − min_i g⊥) over U's six gaps.

## 3. Two-stage protocol and bars (final on sign-off; D3)

**Stage 0 — U flatness validation + bands (U only, treatment sealed;
review condition that U is validated flat BEFORE treatment):** seeds
{42, 7, 13}, U in base and cb. Flatness gate: FLAT_U < 0.12 — half the
predicted U deflection (0.23), derived, documented, fixed here. Bands
(both calibrated from the U spread, the structure-free noise reference):
band_sep = band_flat = max(0.05, 3·max_seed FLAT_U). Seal protocol as BP-C6
(bands → own commit → Stage-1 harness reads committed file, logs SHA).
If the flatness gate fails, Stage 1 does NOT run (engineering stop,
redesign = new pre-reg).

**Stage 1 — measurement:** fresh seeds {101, 102, 103}; PA, PB in base and
cb; U in base and cb (12 runs); censuses (write + probe, cross-lane
exclusion, axial-uniformity gate at both snapshots, max transverse
excursion per carrier logged, min non-neighbor distance logged).

- **READABLE (the registered expectation):** SEP > band_sep on EVERY seed,
  BOTH treatment chains, BOTH configurations, at BOTH snapshots, AND
  FLAT_U < band_flat everywhere, AND axial gate holds, AND censuses valid.
  Consequence: the stored pattern is mechanically readable through the
  transverse channel; C6b (selectivity framing on this named mechanism)
  becomes admissible.
- **NOT-READABLE (NULL):** SEP ≤ 0 anywhere with all gates clean — the
  buckling channel does not transmit the pattern under these primitives;
  the mechanism class is closed with the derivation recorded as wrong
  (calibration lesson mandatory).
- **INCONCLUSIVE:** 0 < SEP ≤ band_sep (unresolved), or partial firing
  across seeds/configs/snapshots (NOT partial evidence, no C6b license),
  or FLAT_U ≥ band_flat, or axial gate broken, or CB inconsistency
  (|SEP_base − SEP_cb| > 2·band_sep), or census breaks.
- **FAIL:** cross-lane bonds after passed gate, invalid write census, or
  U shows class structure it cannot have.

## 4. Walks (traps #5, #6, symmetry — re-run for the NEW observable)

- Coupling: the probe is structure-free by construction; the metric g⊥ is
  coupled to stored structure ONLY through bond tension (no-mimic argument
  §0) — the coupling is the hypothesis, the holder and probe are provably
  transverse-inert resp. structure-free.
- Metric at every cell: g⊥ defined everywhere (magnitude, no 0/0);
  predictions interior and DISTINCT per class (0.05 / 0.23 / 5.41); U cell
  non-degenerate at h = 9.0 (k_t = +0.44 ≠ 0 — the h = 8.5 design was
  rejected for exactly this).
- Symmetry: the discriminator SEP is computed WITHIN each chain (LONG vs
  SHORT classes of the same chain) — no cross-cell symmetry is load-
  bearing, so neither sign-flip nor mirror relations can force SEP to a
  value; PA and PB swap their class layouts (complement), so a
  structure-independent positional artifact (e.g. arch residue) inflating
  gap i identically in both chains lands in OPPOSITE classes and would
  push their SEPs in opposite directions — requiring BOTH chains to pass
  is the artifact gate on this axis. Direction degeneracy is broken by the
  declared probe axis; the magnitude metric is insensitive to the sign of
  the buckle.

## 5. Predictions (calibration, before data; honesty condition from review)

- READABLE: **80%** — this is a first-order derived effect; the honest
  framing is "does the run MATCH the registered quantitative picture",
  not "did something happen". Registered quantitative picture: LONG
  saturation near 5.41 (±1.0), SHORT ≈ 0.05 (±0.05), U ≈ 0.23 (±0.15),
  all report-only.
- NOT-READABLE 5%, INCONCLUSIVE 12% (most likely: axial gate at 0.35 or
  U flatness — the alternating probe on a weakly-stiff U may still ripple),
  FAIL 3%.
- Most-likely failure mode: INCONCLUSIVE via FLAT_U ≥ band (U's +0.44
  stiffness is only 5× the probe scale).

## 6. BELIEF_PATH §4 row text, pre-scripted per verdict

- READABLE: "R8 CLOSED PARTIAL; buckling channel (named mechanism class)
  POSITIVE scoped: stored rest patterns are mechanically READABLE in the
  transverse channel (engineered write, engineered hold, structure-free
  probe); selectivity (C6b) and emergent write (C7) remain open."
- NOT-READABLE: "R8 CLOSED PARTIAL; buckling channel closed (derived
  first-order effect absent — derivation recorded wrong); reopen requires
  another named mechanism class."
- INCONCLUSIVE/FAIL: row unchanged; LOGBOOK only.

## 7. Budget

Harness (axial holder + lateral probe + g⊥ metric, from the C6 harness):
45 min. Stage 0: minutes. Stage 1: ~15 min. Verdict + D10: 30 min.
**Realistic 1.5 h → hard cap 3 h.**

## 8. Out of scope

Selectivity (C6b), emergent write (C7), retention of transverse
readability, Flux substrate, frequency/period axes (closed).
