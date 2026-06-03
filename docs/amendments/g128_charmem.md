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
_(pending run)_
