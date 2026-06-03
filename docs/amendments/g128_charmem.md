# G128 — Store + recall ASCII CHARACTERS in the matter memory (2 cell-rows per byte)

## Pre-registration (locked BEFORE run)
Extend G127 (hex nibbles) to real text characters. A byte = high nibble (cell-row at y=10) + low nibble
(row at y=20), each across K=4 wide-spaced cells (x=6,11,16,21, radius 1.5). Settle-once; for each char,
write both rows (drive carriers), hold POST=300 with per-row maintenance, read both rows, reconstruct the
byte → char. Text "EQ"; both seeds. No LLM.

**Bars (locked):**
- G128 PASS: the text "EQ" recalled EXACTLY (both chars, both seeds).
NULL/PARTIAL otherwise.

## Result
Stored "EQ" → recalled "EQ" EXACTLY on BOTH seeds. **VERDICT: PASS.**

## Finding — the matter memory stores and recalls real TEXT CHARACTERS
Each ASCII byte (two nibbles across two cell-rows) is written into the substrate, held, and read back
exactly — the text "EQ" round-trips perfectly on both seeds, no LLM/transformer/embedding. This lifts the
matter-position memory from abstract bits (G116/G119c) and hex symbols (G127) to genuine TEXT: a
character written into the substrate's physics and recalled.

Honest scope (unchanged): engineered cell layout in maintained cleared rows (scaffold ~ §4.8), short
in-window hold, presence-by-cell readout. The READ/WRITE/encode parts are established (a 2-row position
register with refresh); the substrate-specific result is that this physics holds text positionally where
its activity dynamics never could. Multi-char words and long-hold retention (anchoring, G125) are the
next scaling steps.
