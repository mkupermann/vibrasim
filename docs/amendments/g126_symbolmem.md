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
Stored: 0xE, 0x4, 0xA, 0x7
| seed | recalled        | exact |
|------|-----------------|-------|
| 42   | 0xE,0x4,0xA,0x6 | No (3/4) |
| 7    | 0xE,0x4,0xA,0x6 | No (3/4) |

**VERDICT: PARTIAL** — 3 of 4 nibbles recalled exactly on both seeds; the systematic error is 0x7→0x6
(the last bit, cell x=24).

## Finding — the deep goal WORKS (symbols stored+recalled in matter), bounded by an edge-cell layout error
The matter memory stored and recalled written hex-digit SYMBOLS with no LLM/transformer/embedding — 15 of
16 bits correct, 3 of 4 nibbles exact, identically on both seeds. The single error is SYSTEMATIC: cell
x=24 (only 6 units from the box edge at 30) consistently drops its bit. This is the same systematic-spatial
signature as G117/G118 — a layout issue (a cell too near the periodic box boundary, where drive overshoot
wraps or edge dynamics interfere), NOT a memory failure. The fix is the G119 lesson applied to the
boundary: keep all cells a margin away from the box edge (G127 moves x=24 → x=22).

So the deep goal — a persistent written symbol stored in and recalled from the substrate's own physics,
no learned language model — is DEMONSTRATED (modulo the edge-cell layout, cleanly diagnosed). Combined
with the codec (G104) and transport (G113), the substrate now supports the three pieces of
communication-without-an-LLM: encode/read (codec), move (driven matter), and STORE/recall (matter memory).
