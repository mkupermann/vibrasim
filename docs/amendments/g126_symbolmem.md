# G126 — Deep-goal capstone: store + recall written HEX-NIBBLE symbols in the matter memory

## Pre-registration (locked BEFORE run)
Realize the deep goal in miniature: store a written 4-bit symbol (hex digit) in the matter-position memory
and recall it — no LLM/transformer/embedding. Each nibble is a presence pattern across K=4 wide-spaced
cells (x=6,12,18,24, pitch 6 > G97 ~3, radius 1.5). Settle-once harness; for each test nibble, WRITE
(drive carriers to 1-cells), HOLD POST=300 with full maintenance (within the stable window), READ
presence-by-cell, reconstruct the nibble. Test symbols [0xE,0x4,0xA,0x7]; both seeds.

**Bars (locked):**
- G126 PASS: ALL four nibbles recalled EXACTLY on both seeds.
NULL/PARTIAL if any mis-recalled.

## Result
_(pending run)_
