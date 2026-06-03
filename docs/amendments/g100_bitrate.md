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
_(pending run)_
