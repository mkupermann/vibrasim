# G104 — Verbatim text by RESPECTING the channel pitch (K=4, no error-correcting code)

## Motivation
G102/G103 failed verbatim because K=16 packs channels at pitch 1.2, below G97's crosstalk-free pitch of
~3, producing SYSTEMATIC symbol confusion that repetition coding cannot fix. The principled fix is to
operate WITHIN the measured channel capacity: K=4 channels in span [6,24] gives pitch 6, comfortably
above 3. Prediction: clean verbatim recovery on both seeds with NO error-correcting code — closing the
loop with G97 (the measured pitch is a real operational constraint).

## Pre-registration (locked BEFORE run)
Identical pipeline to G102 EXCEPT K=4 (2 bits/symbol; each byte = 4 symbols). Decoder calibrated on
random K=4 traffic, WIN=4, per-symbol reset. Message: "EQMOD SUBSTRATE SPEAKS".

**Bars (locked):**
- G104a verbatim recovery: reconstructed == original (CER = 0) on both seeds, NO repetition code.
PASS = G104a. NULL/PARTIAL otherwise (report CER + garbled output).

## Result
Original: `EQMOD SUBSTRATE SPEAKS`
| seed | recovered | sym-acc | CER | exact |
|------|-----------|---------|-----|-------|
| 42   | `EQMOD SUBSTRATE SPEAKS` | 1.00 | 0.00 | **Yes** |
| 7    | `EQMOD SUBSTRATE SPEAKS` | 1.00 | 0.00 | **Yes** |

G104a (verbatim both seeds, no ECC): **True** → **VERDICT: PASS**

## Finding — verbatim communication, achieved by respecting the channel, not by adding machinery
At K=4 (pitch 6, above G97's crosstalk-free ~3) the substrate transmits the full string VERBATIM on both
seeds with perfect symbol accuracy and NO error-correcting code — the exact case that failed at K=16
(G102/G103, pitch 1.2). This confirms the G103 diagnosis: the failures were a channel-pitch violation,
not a fundamental limit. Operating within the measured spatial capacity removes the systematic errors
that repetition coding could not.

This is the capstone of the communication arc (G97–G104): a message is written into the substrate's
physics as spatial-channel symbols, transported by the substrate, and read back exactly — no LLM,
transformer, embedding, or tokenizer; only the engineered injection/readout and a linear decoder
calibrated on random traffic. The cost of K=4 is rate (2 bits/symbol → 4 symbols/byte), the honest
trade for reliability. The whole arc holds together: G97's pitch is the design rule that G104 obeys to
get verbatim text.
