# G125 — Extend retention by ANCHORING the carriers (re-pin position) at POST=2500

## Pre-registration (locked BEFORE run)
G124 showed retention is bounded (~2000 ticks) by slow CARRIER DRIFT (a carrier leaves its cell by 2500;
control stays clean). The diagnosed fix is to ANCHOR the carriers. G125 re-pins each carrier to its cell
centre every hold tick (a strong structural anchor / latch), full maintenance, POST=2500, pattern [1,0,1]
+ no-write control, both seeds.

**Bars (locked):**
- G125a: [1,0,1] recovered exactly at POST=2500 with anchoring (both seeds).
- G125b: no-write control empty (both seeds).
PASS = both → anchoring removes the carrier-drift retention limit; matter memory becomes long-retention.
(Honest note: re-pinning is a strong intervention — a hardware-latch analog; it makes the carrier a fixed
location by construction. PASS would show retention is engineerable, bounding it to the anchoring cost.)

## Result
_(pending run — compute-heavy at POST=2500; will record on completion)_
