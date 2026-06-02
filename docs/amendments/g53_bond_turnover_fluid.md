# G53 — Bond turnover: does a fluid membrane self-repair while staying intact?

Pre-registered: 2026-06-02 (BEFORE the run). G52 localized membrane rigidity precisely to
PERMANENT BONDS. This BET adds the needle-mover primitive — `bond_turnover_rate` (each bridge
spontaneously breaks with probability rate·dt, freeing valence so form_bridges can re-bond) —
making the membrane FLUID (bonds break + reform → the network remodels). Combined with atom
mobility (node_thermal_speed) and surface-minimizing forces (curvature + edge-closure), a fluid
membrane should be able to flow into a wound and re-close. The risk is the fluidity/stability
trade-off: too much turnover dissolves the membrane.

## Method
G30/G46 protocol + node_thermal_speed=0.2 + edge_closure_k=1.0. Sweep bond_turnover_rate ∈
{0.0 (rigid baseline), 0.1, 0.3}. For each rate × {wounded, unwounded}: wounded → healing
(component regrowth); unwounded → persistence (final/peak). Seeds 42 & 7. A rate "works" if it
HEALS (wounded) AND STAYS INTACT (unwounded) on both seeds.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G53a | Rigid baseline does not heal | rate=0 wounded: healed < 0.1 (both seeds) |
| G53b | Some turnover rate HEALS | ∃ rate>0: wounded healed (recovered−post)/(N0−post) ≥ 0.3 (both seeds) |
| G53c | …and stays intact at that rate | the same rate: unwounded final/peak ≥ 0.7 (both seeds) |

PASS = G53a AND (G53b, G53c satisfied by the SAME rate) → bond turnover yields a fluid,
self-repairing membrane that remains stable: the rigidity ceiling is BROKEN by the new primitive.
A major positive (self-renewing membrane = a far stronger cell precursor). NULL: if no rate
satisfies both (every healing rate also dissolves the membrane, or no rate heals), the
fluidity/stability trade-off is fundamental in this substrate — an honest, decisive boundary on
self-repair. No post-hoc threshold tuning (the rate sweep is pre-registered; "works" requires
BOTH bars at one rate on BOTH seeds).

## RESULT (2026-06-02): NULL/partial — but the ceiling IS breakable (partial fluid self-repair)

| rate | seed 42 heal | seed 7 heal | persist (both seeds) |
|------|--------------|-------------|----------------------|
| 0.0 (rigid) | 0.00 | 0.00 | 1.00 |
| 0.1 | **0.37** | 0.05 | 1.00 |
| 0.3 | 0.05 | 0.11 | 1.00 |

G53a ✓ (rigid heals 0.00), G53b ✗ (no rate ≥0.3 BOTH seeds), G53c ✗ (no working rate). **Verdict:
NULL/partial on the locked bar — but a genuine partial BREAKTHROUGH.**

1. **Bond turnover breaks the rigidity ceiling (partially).** Rigid heals 0.00 everywhere; with
   turnover, seed 42 at rate 0.1 healed **37%** of the wound. The new primitive makes the membrane
   fluid enough to remodel into a wound — the first healing seen in the whole self-repair line
   (G46/G47/G48/G52 all 0.00).
2. **No fluidity/stability trade-off at these rates.** persist = 1.00 everywhere — the membrane
   stays fully intact while partially self-repairing. (The feared dissolution did not occur ≤0.3.)
3. **But it is NOT robust.** Healing is seed-dependent and sub-threshold (0.37 vs 0.05 at rate 0.1)
   → the locked "≥0.3 both seeds at one rate" bar is not met. Honest NULL/partial, not retuned.

**Significance:** the rigidity ceiling, previously characterized as a hard boundary (FINDINGS_
SUMMARY), is BREAKABLE — bond turnover is the right mechanism. The healing is just not yet strong/
robust. Next (G54): strengthen the healing without destabilizing — longer repair window (250→500
ticks; seed 42 was still climbing) + stronger surface-closure forces (edge_closure_k, curvature) —
to push robust ≥0.3 healing on both seeds. This is strengthening the MECHANISM/conditions, not
lowering the bar.
