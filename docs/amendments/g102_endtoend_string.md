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
Original: `EQMOD SUBSTRATE SPEAKS`
| seed | recovered | sym-acc | CER | exact |
|------|-----------|---------|-----|-------|
| 42   | `EQM?D TUBSCRATE CPEAKS` | 0.89 | 0.18 | No |
| 7    | `EQMOD SUBSTRATE SPEAKS` | 1.00 | 0.00 | **Yes** |

G102a (verbatim both seeds): **False** → **VERDICT: PARTIAL**

## Finding — the substrate transmitted text verbatim on one seed; not yet reliable across seeds
Seed 7 recovered the full string EXACTLY through the substrate physics — a genuine end-to-end
demonstration of writing a message into the substrate and reading it back, with no LLM, transformer, or
embedding, only the spatial channel and a linear decoder calibrated on random traffic. Seed 42 garbled
~11% of nibbles (sym-acc 0.89), and because each byte is 2 nibble-symbols those errors compound to a
human-readable-but-wrong string (CER 0.18). By the two-seed gate the verbatim bar fails → PARTIAL.

This is the expected consequence of using a RAW (uncoded) K=16 channel for text: at ~0.9–1.0 per-symbol
accuracy (G99: K=16 → 0.94–0.97), per-character reliability is acc^2 ≈ 0.8–0.94 — enough to read, not
enough to guarantee verbatim. The standard fix is an error-correcting code, NOT a tuning knob: G103 adds
a repetition code (each symbol sent 3× with majority vote) to drive CER to 0 on both seeds. The raw
result is honestly a partial: readable text transmitted through the physics, verbatim on 1/2 seeds.
