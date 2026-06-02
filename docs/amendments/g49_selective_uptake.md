# G49 — Selective uptake: does the membrane CONCENTRATE a nutrient above exterior levels?

Pre-registered: 2026-06-02 (BEFORE the run). G43/G44 showed the membrane EXCLUDES foreign
species (interior depleted). The richer, complementary cell function is active UPTAKE: not just
keeping waste out, but concentrating a nutrient IN — accumulating compatible species in the
interior ABOVE exterior levels (transport against a gradient). The plain G32 channel cannot do
this (compatible passes freely → equilibrates). The 'uptake' mode (membrane_channel_uptake)
adds: reflect COMPATIBLE OUTBOUND vibrations back inside (a one-way trap for nutrient), while
still excluding incompatible — so the interior accumulates compatible above the exterior.

## Method
G30 membrane + atom-proximity channel, continuous ambient pressure. Measure interior (r<0.6R)
vs exterior COMPATIBLE concentration (count/volume) over the last third. Arms:
- **uptake** (membrane_channel_uptake=True): trap compatible inside.
- **plain** (membrane_channel_uptake=False, = G32): compatible passes freely (control).
Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G49a | Membrane forms | largest bridged component ≥ 50 (both seeds) |
| G49b | Nutrient accumulation (uptake) | interior/exterior compatible concentration ≥ 1.5 (mean over last third, both seeds) |
| G49c | Channel-dependent (plain control) | plain channel: interior/exterior compatible ≤ 1.2 (no accumulation) |

PASS = G49a–c → the membrane actively CONCENTRATES a nutrient interior above exterior (transport
against a gradient), and only with the uptake trap: a richer cell-precursor function (active
uptake) on top of homeostasis. NULL: if G49b fails the trap does not accumulate compatible
(the uptake mechanism does not concentrate at this scale); if G49c also accumulates, the
geometry traps species regardless of the mode. Honest either way. No post-hoc threshold tuning.
