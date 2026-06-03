# G130 — Head-to-head: ACTIVITY spreads vs matter POSITION stays (validates the core discovery)

## Motivation
The session's one genuinely transferable insight is the ASYMMETRY: in this substrate a memory written as
ACTIVITY leaks/spreads (write=leak) but the same content written as matter POSITION stays selective. So
far that rests on a cross-experiment comparison (G88-G96 activity NULL vs G116 position PASS). G130 tests
it WITHIN ONE RUN: place atoms at cell A, ACTIVATE them (deposit charge), and over a short window measure
(1) the activity readout — charge in the A-region vs the neighbour B-region (does activity spread A->B?)
and (2) the position readout — atom count in A vs B (does the matter move to B?).

## Pre-registration (locked BEFORE run)
Quiet substrate; deposit charge Q into A-region atoms (x=10); run T=60 ticks; measure summed |k_charge|
in A (x=10) and B (x=18) regions (radius 2.5) and atom counts. Both seeds.

**Bars (locked):**
- G130a ACTIVITY spreads: charge B/A >= 0.2 after T (activity propagates to the neighbour), both seeds.
- G130b POSITION stays: no atom-count gain in the B-region (matter does not move there), both seeds.
PASS = both → the activity-spreads / position-stays asymmetry that underlies the breakthrough, validated
in a single run. (Names established quantities; the contribution is the direct in-substrate demonstration.)

## Result
| seed | charge A0→A | charge B | spread B/A | B-region atom gain |
|------|-------------|----------|------------|--------------------|
| 42   | 1326 → 462  | 0.0      | 0.00       | -74                |
| 7    | 1368 → 558  | 0.0      | 0.00       | -89                |

G130a (activity spreads, B/A>=0.2): **False** · G130b (position stays): True → **VERDICT: NULL**

## Finding — REFINES the mechanism: "activity spreads" is REGIME-specific, not same-conditions
In the QUIET substrate the deposited charge did NOT spread to the neighbour (B-charge 0.0); it decayed in
place — consistent with G106 (charge doesn't propagate across distance). So the simple framing "activity
spreads while position stays, in the same conditions" is WRONG: in the quiet regime, charge is local too.
The activity-memory failure (write=leak, G88–G96) was an ACTIVE-substrate phenomenon — the self-ignition
broadcast cascade in a substrate full of self-activity (the G83 root) — not generic charge diffusion.

Corrected mechanism of the discovery (6th self-correction): the two representations require INCOMPATIBLE
REGIMES. Activity-memory needs the ACTIVE substrate (atoms need flux to write/sustain) — and that active
regime self-contaminates → fails. Matter-position works in the QUIET substrate (atoms stay put, no
self-activity) — and that quiet regime cannot support an activity write. So the escape is not "matter
diffuses slower than charge in the same conditions"; it is "matter-position is readable+stable in the
QUIET regime, which is the only regime without the contaminating self-activity." The breakthrough
(position memory works where activity failed) STANDS; the one-line mechanistic story is corrected to a
regime statement, not a same-conditions spread asymmetry.
