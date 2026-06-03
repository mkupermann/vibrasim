# G124 — Long-term stability of the working (full-maintenance) matter memory (POST=2500)

## Pre-registration (locked BEFORE run)
G116/G119c held at POST=1500 with FULL atom-clearing maintenance. G124 confirms the persistence is robust
at a longer hold: settle-once; write [1,0,1]; HOLD POST=2500 with full atom-clearing maintenance; read;
+ no-write control. Both seeds.

**Bars (locked):**
- G124a: [1,0,1] recovered exactly at POST=2500 (both seeds).
- G124b: no-write control empty (both seeds).
PASS = both → the working matter memory is robustly persistent long-term.

## Result
| seed | WRITE readout (target [1,0,1]) | CONTROL |
|------|-------------------------------|---------|
| 42   | [1,0,0]                       | [0,0,0] |
| 7    | (POST=2500 too slow; aborted) | —       |

G124a (pattern exact at 2500): **False** (seed 42 lost the x=21 carrier) → **VERDICT: NULL**
[Seed 7 aborted — impractically slow at POST=2500; the bar is decided by seed 42 (exact-recovery fails).]

## Finding — retention is FINITE (~2000 ticks); failure at 2500 is CARRIER LOSS, not background fill
At POST=2500 with full maintenance the control stays clean ([0,0,0] — the atom-clearing keeps empty cells
empty indefinitely), but the WRITTEN pattern degrades: the farthest carrier (x=21) is lost ([1,0,0]). So
the limit on long holds is the persistence of the CARRIER atoms themselves, not background contamination.
G115 showed carriers persist (drift<2) to ~2000 ticks; by 2500 a carrier drifts out of its cell / is lost.

Honest RETENTION BOUND for the matter memory:
- Stable through ~1500–2000 ticks: G116/G119c PASS at POST=1500; G115 carriers hold to 2000.
- Degrades by ~2500: carrier loss (G124), even though maintenance keeps the 0-cells clean.
So it is a FINITE-RETENTION memory (a long but not infinite hold), bounded by slow carrier drift — like a
volatile store with a finite retention time, refreshed for the 0s but not indefinitely stable for the 1s.
This does NOT diminish the breakthrough (selective + persistent + clean multi-bit within the retention
window, fully demonstrated G116/G119c); it bounds its retention honestly: ~2000 ticks, carrier-drift
limited. A longer-retention variant would need to pin the carriers (anchoring) — a clear next direction.
