# G127 — Clean symbol store+recall: edge-margin layout fix (the G126 diagnosis)

## Pre-registration (locked BEFORE run)
G126 recalled 3/4 hex nibbles, failing only the x=24 cell (6 units from the box edge at 30). Fix: move all
cells a margin off the boundary — cells x=6,11,16,21 (pitch 5; the farthest now 9 units from the edge).
Otherwise identical to G126 (settle-once, write/hold POST=300/read, symbols [0xE,0x4,0xA,0x7], both seeds).

**Bars (locked):**
- G127 PASS: ALL four nibbles recalled EXACTLY on both seeds (clean symbol memory).
NULL/PARTIAL otherwise.

## Result
_(pending run)_
