# G100 — Channel bit rate: minimum ticks-per-symbol (temporal bandwidth)

## Motivation
G97 measured the channel's SPATIAL capacity (pitch ~3) and G99 its symbol ALPHABET (K=16, 4 bits/symbol,
with reset). The remaining axis is TEMPORAL: how few ticks per symbol (WIN) still transmit reliably?
That fixes the bit RATE (bits per tick = log2(K)/WIN). Standard channel-bandwidth measurement; applied
in-substrate.

## Pre-registration (locked BEFORE run)
Fix K=8 (3 bits/symbol). Same as G99 (one-hot spatial channels, per-symbol active reset, multiclass
linear decode, held-out 70/30). Sweep WIN (injection ticks per symbol) in {8, 4, 2, 1}.

**Bars (locked):**
- G100a sanity (WIN=8): held-out symbol accuracy >= 0.90 (both seeds). Chance = 0.125.
- G100b bandwidth: report accuracy vs WIN and the MINIMUM WIN still reaching >= 0.90 on both seeds; from
  it report the bit rate log2(8)/WIN_min bits per injection tick (descriptive; no threshold tuned).
PASS (characterised) = G100a. NULL if even WIN=8 fails (contradicts G99 — would signal instability).

## Result
| seed | WIN=8 | WIN=4 | WIN=2 | WIN=1 |
|------|-------|-------|-------|-------|
| 42   | 1.00  | 1.00  | 1.00  | 1.00  |
| 7    | 1.00  | 1.00  | 1.00  | 1.00  |
(K=8, chance 0.125, n=240 each)

G100a sanity (WIN=8 both seeds): **True** · G100b min WIN >= 0.90 (both): **WIN=1**
→ bit rate = log2(8)/1 = **3.00 bits per injection tick** (4.0 at K=16) → **VERDICT: PASS**

## Finding — the channel is reset-limited, not duration-limited
Decode stays at 1.00 down to WIN=1 (a single injection tick per symbol), both seeds. The symbol rate is
bounded only by the active-reset operation between symbols, not by any temporal integration: one tight
injection is instantly spatially readable (consistent with G83's instantaneous 1.00 read). The channel
needs no settling time per symbol.

Honest reading: this is not surprising given G83/G97 — a single localized injection is detectable in the
same tick — but it completes the quantitative picture. The substrate channel is essentially a memoryless
(after reset) spatial code: ~10 parallel channels (G97) × up to 4 bits/symbol (G99) × 1 tick/symbol
(G100). The binding constraint everywhere is the SAME one: signal must be actively cleared between uses
(G98), because the substrate retains-and-superimposes rather than storing selectively (G88–G96).
