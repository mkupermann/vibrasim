# G103 — Reliable verbatim text via a repetition code (error correction)

## Motivation
G102 showed the raw K=16 channel transmits readable text and recovered the message VERBATIM on seed 7,
but garbled ~11% of nibbles on seed 42 (PARTIAL). The standard, non-tuning fix for an uncoded channel is
an error-correcting code. G103 adds the simplest one — a REPETITION code: each symbol is transmitted 3×
and the decoder takes the majority vote of the 3 readouts. Established method (named as such); it should
drive the character error rate to 0 on both seeds.

## Pre-registration (locked BEFORE run)
Identical to G102 (K=16 nibble-symbols, WIN=4, per-symbol reset, decoder calibrated on random traffic)
EXCEPT each message symbol is sent REP=3 times; decode = majority vote of the 3 per-repetition argmax
predictions. Message: "EQMOD SUBSTRATE SPEAKS".

**Bars (locked):**
- G103a verbatim recovery: reconstructed == original (CER = 0) on both seeds.
- G103b the code is the cause: report uncoded (REP=1) vs coded (REP=3) CER side by side; REP=3 must
  improve on REP=1 (else the code is not doing the work).
PASS = G103a. (G103b is a within-run control, not a separate bar.)

## Result
_(pending run)_
