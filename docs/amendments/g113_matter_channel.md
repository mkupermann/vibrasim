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
| seed | arrived | symbol-acc (on arrivals) |
|------|---------|--------------------------|
| 42   | 16/16   | 1.00 |
| 7    | 16/16   | 1.00 |
(K=3, chance 0.33)

G113a (throughput ≥50%): **True** · G113b (fidelity ≥0.85): **True** → **VERDICT: PASS**

## Finding — driven matter is a working K-ary transmission line over distance
Every driven atom (16/16, both seeds) traversed >20 units and its source y-band was recovered exactly at
the far end (symbol accuracy 1.00, K=3). Driven matter is therefore a genuine slow transmission line: it
carries multi-symbol information across distance with full fidelity, no LLM/transformer/embedding.

This completes the communication arc and the corrected transport picture. The substrate supports TWO
distinct communication modes:
- **Co-located codec** (G97–G104): fast (1 tick/symbol), same-site encode/decode, verbatim text.
- **Driven-matter transmission line** (G110–G113): slow (~200 ticks per ~20 units), over-distance, K-ary
  symbols at 100% fidelity.
The driven-matter mode is the positive that three honest self-corrections uncovered — it would have been
buried by the wrong "overdamped, nothing travels" conclusion (G110). Surfaced as
docs/patterns/driven_matter_transport.md. The communication programme (G97–G113) is complete: the
substrate genuinely communicates, both locally and over distance, with no learned language model.
