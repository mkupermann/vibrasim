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
| seed | uncoded CER (REP=1) | coded CER (REP=3) | coded output | exact |
|------|---------------------|-------------------|--------------|-------|
| 42   | 0.14 | **0.00** | `EQMOD SUBSTRATE SPEAKS` | Yes |
| 7    | 0.09 | 0.09 | `EQMOD SUBTTRATE SPEA;S` | No |

G103a (verbatim both seeds): **False** · G103b (code helps): True (42: 0.14→0.00) → **VERDICT: NULL/PARTIAL**

## Finding — repetition coding fixes RANDOM errors, not SYSTEMATIC ones; the real cause is a pitch violation
The repetition code fixed seed 42 (0.14→0.00, verbatim) but did NOTHING for seed 7 (0.09→0.09). That is
the signature of SYSTEMATIC error: seed 7 misreads the same symbols the same way on all 3 repetitions, so
majority vote cannot help. A repetition code only corrects independent random errors.

The systematic errors trace to a CHANNEL-PITCH VIOLATION. K=16 channels packed into span [6,24] sit at
pitch (24−6)/15 = **1.2**, far below the crosstalk-free pitch of **~3** measured in G97. Adjacent symbols
overlap and are consistently confused — exactly the systematic bias seen. So G102/G103 were operating the
channel BEYOND its measured spatial capacity; no amount of repetition coding rescues that.

The principled fix is not more coding but RESPECTING the channel: use fewer, well-separated symbols
(K=4 → pitch 6, comfortably above 3). G104 tests end-to-end verbatim text at K=4 (2 bits/symbol, 4
symbols/byte), predicting clean verbatim on both seeds with no error-correcting code at all. This also
nicely closes the loop with G97: the measured pitch is a real operational constraint, not a curiosity.
