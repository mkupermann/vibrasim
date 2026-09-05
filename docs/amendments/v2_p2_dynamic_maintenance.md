# V2-P2 amendment: dynamic-maintenance foundation candidate

**Frozen:** 2026-09-05, before any V2-P2 trajectory

## Scientific identity

P2 replaces the unsupported individuation rung after P0 NULL and P1
UNRESOLVED. It asks only whether a closed local energy/geometry/field loop buys
more post-drive bond-time than matched broken-loop controls.

The design rationale and interpretation limits are frozen in
`docs/superpowers/specs/2026-09-05-v2-p2-dynamic-maintenance-design.md`.

## Registered configuration

| Quantity | Frozen value |
|---|---:|
| Grid | 32 x 32, periodic |
| Matter sites | P0's six fixed coupling sites |
| Candidate radius | 4.5 lattice units |
| Field wave coefficient `c` | 1.0 |
| Reciprocal site coupling `g` | 1.0 |
| Matter-bond stiffness `k_m` | 0.5 |
| Field-bond stiffness `k_f` | 0.25 |
| Capture fraction `eta` | 0.25 of positive coupling work |
| Formation cost `E_form` | 0.02 |
| Bond lifetime `tau_b` | 10.0 |
| Initial field energy | 1.0 |
| Gaussian width `sigma` | 2.0 |
| Primary step / horizon | 0.025 / 100.0 |
| Convergence step / horizon | 0.0125 / 100.0 |
| Source centres | (4,16), (16,4), (4,4) |
| Frame stride | 10 primary steps |

All values are dimensionless. `E_form` is 2% of the normalized input energy;
`tau_b` is one tenth of the horizon. These round ratios were selected before
execution and are not fitted estimates.

Candidate pairs are every unordered pair of sites whose periodic Euclidean
distance is at most 4.5. Pair ordering is lexicographic. Each endpoint may
participate in at most two live bonds. Simultaneously eligible pairs are handled
in that order. There is no random tie-break and no parameter seed.

## Registered step order

For every interval `[t, t + dt]`:

1. evaluate reciprocal field/matter, live matter-bond, and permitted live
   field-bond forces;
2. advance positions and momenta with velocity Verlet;
3. capture `eta * max(0, F_couple * r * dt)` at each site, bounded by that
   site's kinetic energy, by reducing `|r|` and crediting the exact reduction to
   its reservoir;
4. age live bonds by `dt`;
5. expire bonds whose age is at least `tau_b`, returning their instantaneous
   matter- and field-spring potential equally to endpoint reservoirs;
6. form eligible candidate bonds when both endpoints can pay `E_form / 2`,
   debit the reservoirs, record the current matter and field differences as
   rest offsets, and add `E_form` to the cumulative formation sink.

Formation cost is irreversibly consumed. The conservation ledger therefore
tracks mechanical field/matter energy, reservoir energy, live spring energy,
and cumulative formation sink. Their sum must equal initial energy within the
registered numerical tolerance.

## Arms and cells

Each source has these primary cells:

- `full`: all six step rules;
- `no_capture`: capture fraction forced to zero;
- `no_field_feedback`: field-bond force forced to zero, with all other rules
  identical.

The `full` and `no_field_feedback` cells are repeated at half step. Every `full`
primary cell is repeated exactly once as reproduction.

## Frozen gates

Let `B_arm,s` be the integral of live-bond count over `[0, 100]` for source `s`.

Scientific contrast:

`sum_s(B_full,s - B_no_field_feedback,s) >= 3 * tau_b = 30.0`.

Negative control: every `B_no_capture,s` is exactly zero.

Numerical validity:

- half-step aggregate contrast has the same sign and differs by at most 20%
  relative to the primary aggregate contrast;
- reproduction has the identical ordered bond-event ledger and each bond-time
  agrees within `1e-12` absolute;
- at every persisted energy record, absolute ledger drift is at most `2e-4`;
- every numeric value written to a scientific artifact is finite.

Verdict precedence is `FAIL`, `INCONCLUSIVE`, `PASS`, `NULL`. Infrastructure or
artifact failure is `FAIL`; numerical validity failure is `INCONCLUSIVE`; all
valid scientific gates passing is `PASS`; otherwise the outcome is `NULL`.

## Stop rule

One registered run is allowed. No calibration or parameter sweep is permitted.
A NULL closes this mechanism candidate. An INCONCLUSIVE permits only a repair
that leaves scientific constants and gates unchanged and is documented before
rerun.

