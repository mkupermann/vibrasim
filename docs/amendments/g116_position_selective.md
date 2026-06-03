# G116 — SELECTIVE + persistent memory via matter position? (test on the central deadlock)

## Motivation
G115 showed matter POSITION persists (a written position holds, identity stable). That cracks the
PERSISTENCE horn. G116 tests the SELECTIVITY horn that defeated every activity-based store (write=leak):
in a cleared band, WRITE cell A by driving a carrier atom there and leave cell B empty; after a long POST,
A should be occupied, B empty, and a no-write CONTROL should leave A empty too. Localized matter should
give selectivity for free (an atom at A cannot populate B), exactly what bridge/firing/charge stores
never could.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. Maintain a cleared band (|y-15|<4): each tick clear background atoms in the band
EXCEPT the tracked carriers. WRITE arm: drive 4 carriers to cell A (x=15, stop on arrival), release,
POST=1500 ticks. CONTROL arm: identical but NO carriers driven. Cells are 2.5-radius boxes at A(x=15) and
B(x=22), row y=15.

**Bars (locked):**
- G116a: WRITE cell A occupied (>=1 atom) after POST, both seeds.
- G116b: WRITE cell B empty (0 atoms) after POST, both seeds (no spread/cross-talk).
- G116c: CONTROL cell A empty (0 atoms) after POST, both seeds (occupancy is caused by the write).
PASS = G116a AND G116b AND G116c → SELECTIVE + PERSISTENT store via matter position, the first on this
substrate. PARTIAL = A written + control-clean but B contaminated. NULL otherwise.

## Result
| arm     | seed | cell A | cell B |
|---------|------|--------|--------|
| WRITE   | 42   | 4      | 0      |
| WRITE   | 7    | 4      | 0      |
| CONTROL | 42   | 0      | 0      |
| CONTROL | 7    | 0      | 0      |

G116a (A occupied) True · G116b (B empty) True · G116c (control A empty) True → **VERDICT: PASS**

## Finding — SELECTIVE + PERSISTENT memory via matter position (first on this substrate)
A bit written by driving carrier atoms to cell A persists there over 1500 POST ticks; cell B stays empty
(the write does not spread); and the no-write control leaves A empty (the occupancy is caused by the
write, not background). All three hold on both seeds. This is the FIRST selective + persistent store the
programme has produced — and it works precisely because it uses a NON-activity representation:
- ACTIVITY stores (bridge strength / firing / charge) couple persistence and selectivity through the
  same spreading dynamics → write=leak, maintenance=contamination → every one failed (G88–G96).
- MATTER POSITION decouples them: a localized atom does not spread (selectivity for free), needs no
  sustaining activity (persists once released, G115), and holds with stable identity. Writing A leaves B
  untouched — the exact contrast the activity stores could never produce.

## Honest scope (claimed cautiously, multi-seed per G37→G38)
- This is a 1-BIT presence store (A occupied vs empty), with 4 redundant carrier atoms. It is NOT yet a
  content-addressable, multi-pattern memory — that is the next frontier (encode N independent bits at N
  cells; read each; low cross-talk).
- It uses an ENGINEERED scaffold: a maintained cleared band (background atoms cleared each tick except
  the carriers), comparable to the charter's engineered §4.8 port topology. The non-trivial PHYSICS
  result is not the scaffold but that matter, unlike activity, does not leak/spread/erode — so within a
  clean region a written position is a stable, selective bit. The carrier persistence itself needs no
  scaffold (G115 showed position holds without band-clearing); the band only keeps the READOUT clean.
- Reframes the programme's central negative honestly: "no selective persistent memory" was true for
  ACTIVITY-based representations; MATTER-POSITION provides one. The deadlock was representational, not
  absolute — and the way out came from the driven-matter discovery (G110–G113), which itself came from
  chasing and correcting three wrong claims. Logged as a milestone with bounded scope.
