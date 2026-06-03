# G102 — End-to-end string transmission through the substrate (capstone demo)

## Motivation
G97–G101 characterised the channel. This is the concrete embodiment of "communication in writing
without an LLM": take a real ASCII string, encode it to symbols, transmit each symbol THROUGH THE
SUBSTRATE PHYSICS (one-hot spatial channel + per-symbol reset), decode from the free-vibration readout,
and reconstruct the string. No transformer, no embedding — only the substrate channel and a linear
decoder calibrated on random traffic.

## Pre-registration (locked BEFORE run)
Alphabet K=16 (one nibble/symbol; each byte = 2 symbols). Calibrate the multiclass linear decoder on a
random K=16 message (no peeking at the test string). Then transmit the test string
"EQMOD SUBSTRATE SPEAKS" as nibble-symbols (WIN=4, per-symbol active reset), decode each symbol, recombine
nibble pairs into bytes, and compare to the original.

**Bars (locked):**
- G102a verbatim recovery: reconstructed string == original (character error rate = 0) on both seeds.
PASS = G102a. NULL/PARTIAL if any character is wrong (report the character error rate and the garbled
output honestly).

## Result
_(pending run)_
