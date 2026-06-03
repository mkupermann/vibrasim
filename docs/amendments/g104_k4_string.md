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
_(pending run)_
