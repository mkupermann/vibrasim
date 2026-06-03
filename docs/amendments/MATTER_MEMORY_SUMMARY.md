# Matter-memory programme summary (G110–G121): breaking the deadlock via a new representation

## One-line
The substrate's central negative — "no selective persistent memory" — was true for ACTIVITY-based stores
(bridges/firing/charge). MATTER POSITION is a different representation that provides the first
selective + persistent + multi-bit memory on the substrate. It is a MAINTAINED store (active,
spatially-selective, NON-destructive refresh), not a static latch.

## How it was reached
Not designed top-down — discovered. The driven-matter TRANSPORT discovery (G110–G113), which itself
required retracting three wrong claims, revealed that bound matter moves and HOLDS position. That holding
is exactly what activity could never do, so it became a memory representation.

## The chain
| G    | result | finding |
|------|--------|---------|
| G110/G111 | — | bound atoms move under sustained drive (mass-scaled ~3%); NOT bond-restrained |
| G112/G113 | PASS | driven matter transports a symbol over distance (K-ary line, fidelity 1.00) |
| G114 | INVALID | first position-memory test — periodic-wrap + no identity tracking (discarded) |
| G115 | PASS | matter POSITION persists: atom holds its driven location, identity stable (drift<2/2000 ticks) |
| G116 | PASS | SELECTIVE 1-bit: write cell A occupied / unwritten B empty / no-write control empty (both seeds) |
| G117 | PARTIAL | 4-bit content memory at 0.88/bit (tight spacing) |
| G118 | NULL | redundancy does NOT help → the error is SYSTEMATIC/spatial (parallels G103) |
| G119b/c | PASS | WIDE spacing → CLEAN multi-bit content memory, 1.000/bit both seeds (settle-once harness) |
| G120 | NULL | band scaffold is LOAD-BEARING: without active clearing, empty cells repopulate → MAINTAINED, not static |
| G121 | (diag) | repopulation ≈ 56% drift-in + 44% new formation (in the broad band) |
| G122 | PASS* | light maintenance (cull band vibrations) holds a SHORT hold (~800 ticks); carriers untouched |
| G123 | NULL | over a LONG hold (1500), light maintenance FAILS (cells fill / carriers destabilize) — corrects the G122 generalization |

## What it IS, honestly
- The FIRST selective + persistent + clean multi-bit content-addressable memory on this substrate.
- A MAINTAINED store: written bits (carrier atoms) persist intrinsically with no upkeep (G115); empty bits
  require active spatially-selective clearing to stay empty, because the band repopulates by diffusion +
  formation (G120/G121). Crucially the maintenance is NON-DESTRUCTIVE — it never disturbs the written
  carriers. "maintenance = contamination" (the activity deadlock) does NOT apply to matter; that is the
  whole reason a maintained selective memory is possible here and was not for activity.
- Engineered scaffold: a cleared band, comparable to charter §4.8 port topology; readout is
  presence-by-cell. Established-method framing: this is a position-coded register with refresh, not a new
  algorithm — the contribution is that THIS substrate supports it where activity could not.

## Retention (honest bound, G124)
The memory is FINITE-RETENTION: stable through ~1500-2000 ticks (G116/G119c PASS @1500; G115 carriers hold
to 2000), but by ~2500 a carrier drifts out of its cell and is lost (G124 NULL) — even though full
maintenance keeps the empty cells clean. So it is a volatile store with a finite retention window bounded
by slow carrier drift; a longer-retention variant would need to PIN the carriers (anchoring).

## What is NOT yet shown (honest open frontiers)
- A fully PASSIVE/static variant: a structural y-barrier blocks only the drift-in half of repopulation
  (G121), not the formation churn — so some active suppression remains needed.
- Scaffold-free selectivity, content-addressable recall by re-stimulation, text-in-matter integration,
  and persistence beyond ~2000 ticks at scale — all fresh directions.

## The meta-lesson
The breakthrough came from the HONESTY discipline, not despite it: three retracted overclaims
(transmission / atom-condensation / "nothing travels") each hid the real mechanism, and correcting them by
direct measurement (G108/G109/G111) is what surfaced driven matter — and then position memory. Measure the
trajectory; don't reason about the mechanism.
