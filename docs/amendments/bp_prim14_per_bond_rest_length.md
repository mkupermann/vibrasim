# PRIM14 — Per-bond rest length (D0 diagnostic)

**Status: SIGNED OFF 2026-08-10, no conditions — committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> If each bridge stores its OWN rest length — frozen to the endpoint distance at
> formation time, a strictly local rule — does bridge tension then restore a
> displaced carrier TOWARD its stored position (making stored geometry an
> attractor), where the current single global `r_eq` demonstrably does not?

## 2. Why the existing rules are insufficient (new-primitive justification, §4.3)

G154 (matter recall-by-content) returned **NULL** with an isolated physical cause
(LOGBOOK 2026-06-12, mechanism probe run before accepting the null):
`apply_bridge_tension` (world/bridges.py:137–175) uses one global equilibrium
distance `r_eq = cfg.r_2 * 0.5` (hardcoded, line 145). Bonds therefore encode
"be r_eq from your neighbour", not "be at your stored place" — a pinned neighbour
on the wrong side pushes a displaced carrier AWAY from target (probe: displace 8,
29.0 → 27.8 after 1500 ticks, target 21 never reached). A stored multi-cell pattern
is not a retrievable attractor under the current rule; Hopfield did the task at
1/546th the compute. The direct follow-on is already named in
docs/redesign/design_requirements.md (R5): "let each bond's r_eq be set by a local
learning rule … making a stored configuration a true attractor."

Honesty framing (D5): the primitive itself is LOCAL substrate physics (each bond
freezes its formation geometry; no external per-pattern write). The register
content in any later recall experiment is still PLACED by driven writes —
that part stays named as engineering. PRIM14-D0 tests only the attractor property.

## 3. Mechanism (implementation spec)

- New per-bridge array `World.b_rest_len: float64[B]` (world/state.py, joining
  b_alive/b_atom_i/b_atom_j/b_strength).
- At bridge formation: `b_rest_len[b] = min-image distance(i, j)` at that tick.
- `apply_bridge_tension`: when `cfg.per_bond_rest_enabled`, use `b_rest_len[b]`
  as the equilibrium distance for that bond; when disabled (default), the current
  global `r_eq = cfg.r_2 * 0.5` — behaviour bit-identical to today.
- Config: `per_bond_rest_enabled: bool = False`. No adaptation rule in D0
  (frozen-at-formation only); any adaptive τ is a later pre-reg.
- Force law, damping, tension_k untouched.

## 4. Protocol (D0 diagnostic, adapted from tools/g154_probe.py)

3-carrier anchored chain as in the G154 probe (level-4 carriers, positions
{13, 21, 29} on one axis, bonds formed at that geometry, outer carriers pinned by
continuous drive as in G154). Displace the middle carrier by +8 (to 29), release,
run 2000 ticks. Seeds {42, 7, 13} (the G154 seed set).

Arms:
- **ARM-P:** `per_bond_rest_enabled=True`. Bonds formed at stored geometry.
- **ARM-C (control):** flag off — must reproduce the G154 probe behaviour
  (recovery ≤ 20% at 2000 ticks; the old rule managed 1.2/8 = 15% at 1500).
- **NC1 (content-neutrality):** bonds formed at the DISPLACED geometry
  (middle at 29 from the start), then middle moved to 21 and released — must
  restore toward 29, not 21 (the mechanism stores formation geometry, whatever
  it is; it must not prefer the "correct" pattern).
- **NC2 (no-bond):** ARM-P setup with bridges deleted after displacement —
  no restoring drift beyond ±1 unit (tension is the mechanism, not drift).

Metric: recovery fraction R = (8 − |x_mid(2000 ticks) − x_stored|) / 8.

## 5. Pre-registered bars (fixed before any data; D3)

- **PASS:** ARM-P R ≥ 0.5 on ≥2/3 seeds AND ARM-C R ≤ 0.2 on ≥2/3 seeds AND
  NC1 restores toward formation geometry (R_formation ≥ 0.5 w.r.t. 29) AND
  NC2 stays within ±1.
- **PARTIAL:** ARM-P moves monotonically toward stored position on ≥2/3 seeds
  with 0.2 < R < 0.5 (direction fixed, dynamics too slow), controls clean.
- **NULL:** ARM-P R ≤ 0.2 (per-bond rest does not create the attractor), or
  controls valid but seeds split 1/3–2/3 against every bar.
- **FAIL:** ARM-C restores (≥0.5) — the claimed defect doesn't reproduce, G154's
  diagnosis was wrong, stop and investigate before anything else; or NC1/NC2
  violated (mechanism is not what it claims).

## 6. Predictions (calibration, before data)

- ARM-C reproduces G154 probe (≤0.2): 85%.
- ARM-P R ≥ 0.5: 60% — the restoring force is now ∝ displacement toward the
  stored point; main risk is the damped dynamics staying too slow (→ PARTIAL).
- Verdict distribution: PASS 55%, PARTIAL 25%, NULL 12%, FAIL 8%.
- Most-likely failure mode: pinned-neighbour coupling still dominates the
  middle carrier (chain tension equilibrates as a whole), slowing recovery
  below the 0.5 bar → PARTIAL.

## 7. Budget (hybrid, §5)

Implementation (array + formation init + tension branch + config): 1 h.
D0 harness (adapt g154_probe): 45 min. Runs: minutes. Verdict + LOGBOOK +
FRONTIER (D10): 30 min. **Realistic 2.5 h → hard cap 5 h.** Overrun → FAILED
post-mortem.

## 8. Out of scope

Any recall-by-content re-run (that is a separate G-series pre-reg, only if D0
passes), adaptive rest-length rules (τ > 0), flux-substrate port of the
mechanism, capacity/multi-pattern questions, any change to tension_k/damping.
