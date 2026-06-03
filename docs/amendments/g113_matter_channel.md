# G113 — Multi-symbol MATTER transmission line (capstone of the driven-matter discovery)

## Motivation
G112 showed a single driven atom traverses >20 units with its y preserved. G113 turns that into a K-ary
transmission line: drive M atoms across the box, classify each by ARRIVAL y-band, and recover its SOURCE
y-band (the symbol). This is the over-distance analogue of the co-located codec (G97/G99) and the full
demonstration of the discovered driven-matter transport mode.

## Pre-registration (locked BEFORE run)
Settle; lambda_gen=0. Drive the M=16 leftmost level>=4 atoms at k_vel_x=6 (re-asserted each tick) for
MAXT=280 ticks. Symbol = source y-band (K=3 bins over y∈[6,24]); recovered = arrival y-band when the atom
first crosses x>20.

**Bars (locked):**
- G113a throughput: >= 50% of driven atoms reach x>20 within the window (both seeds).
- G113b fidelity: symbol accuracy on arrivals >= 0.85 (both seeds; chance = 1/3).
PASS = G113a AND G113b → driven matter is a working K-ary transmission line over distance. PARTIAL =
atoms arrive but y-band not preserved. NULL = too few arrive.

## Result
_(pending run)_
