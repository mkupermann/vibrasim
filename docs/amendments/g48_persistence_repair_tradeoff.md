# G48 — Persistence ⊥ self-repair: relaxing valence commitment buys healing at the cost of longevity

Pre-registered: 2026-06-02 (BEFORE the run). G46/G47 found the membrane does not self-repair,
and diagnosed the cause as the `fusion_bond_block` valence commitment (the source of persistence)
blocking the new bonds a wound needs. This BET tests that mechanism directly: relax the
commitment and the prediction is the membrane HEALS but LOSES persistence — a genuine trade-off.

## Method
G30/G46 protocol. Four conditions = `fusion_bond_block` ∈ {0 (relaxed), 2 (committed, G30
default)} × {wounded, unwounded}. Wounded: form → wound (polar cap + bridges) → repair window →
measure healing (component regrowth). Unwounded: form → observe window → measure persistence
(final/peak component size). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G48a | Relaxed HEALS | block=0 wounded: healed fraction (recovered−post)/(N0−post) ≥ 0.3 (both seeds) |
| G48b | Relaxed loses persistence (the cost) | block=0 unwounded: final/peak ≤ 0.7 (both seeds) |
| G48c | Committed persists | block=2 unwounded: final/peak ≥ 0.9 (both seeds) |
| G48d | Committed does NOT heal (reconfirms G47) | block=2 wounded: healed fraction < 0.1 (both seeds) |

PASS = G48a–d → the trade-off is confirmed: valence commitment gives persistence but blocks
self-repair; relaxing it gives self-repair but loses persistence. The substrate cannot have both
through this mechanism — a clean, mechanistically-grounded structural finding. NULL: if G48a
fails even the relaxed membrane does not heal (the blocker is not valence commitment but
something else — e.g. no wound-targeting at all); if G48b fails the relaxed membrane persists
anyway (commitment is not the source of persistence). Honest either way. No post-hoc tuning.
Note: block=0 may not form a stable ~110-atom shell at all — if N0 is small, that is itself the
persistence cost in its starkest form (no commitment → no stable membrane to wound).

## RESULT (2026-06-02): NULL — REFUTES the trade-off; persistence is NOT from valence commitment

| condition | block=0 | block=2 |
|-----------|---------|---------|
| unwounded persistence (final/peak) | 1.00 | 1.00 |
| wounded healing (frac of damage) | 0.00 | 0.00 |

(N0 = 112/110 both seeds; wounded post = 24/33; final ≡ post in every wounded case.)

G48a ✗, G48b ✗, G48c ✓, G48d ✓ → **NULL — and it falsifies the G47 hypothesis.**

block=0 and block=2 behave IDENTICALLY: both persist fully (1.00) AND both fail to heal (0.00).
`fusion_bond_block` makes no measurable difference here. Therefore:

1. **Persistence is NOT from valence commitment.** The membrane persists with block=0 too — its
   longevity comes from the bridge network + curvature/repulsion holding the shell's shape,
   independent of fusion_bond_block. (Corrects the G46/G47/summary attribution.)
2. **No-self-repair is NOT from valence commitment either.** Relaxing it does not enable healing.

**The real reason the membrane is static (corrected):** positional RIGIDITY + no wound-targeting.
Removed atoms leave a gap; the remaining bonded atoms hold their positions (curvature/repulsion
fix the shell shape) rather than migrating to re-close; the wound fragments do not re-merge; and
new ambient atoms form elsewhere, untargeted to the wound. The membrane is a rigid, stable
structure, not a fluid self-renewing one — for simple structural reasons, not a persistence
trade-off. My G47 trade-off explanation was a plausible hypothesis that the confirmatory test
FALSIFIED; recorded as such (honesty over consistency).
