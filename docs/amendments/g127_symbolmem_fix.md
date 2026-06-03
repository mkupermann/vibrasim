# G127 — Clean symbol store+recall: edge-margin layout fix (the G126 diagnosis)

## Pre-registration (locked BEFORE run)
G126 recalled 3/4 hex nibbles, failing only the x=24 cell (6 units from the box edge at 30). Fix: move all
cells a margin off the boundary — cells x=6,11,16,21 (pitch 5; the farthest now 9 units from the edge).
Otherwise identical to G126 (settle-once, write/hold POST=300/read, symbols [0xE,0x4,0xA,0x7], both seeds).

**Bars (locked):**
- G127 PASS: ALL four nibbles recalled EXACTLY on both seeds (clean symbol memory).
NULL/PARTIAL otherwise.

## Result
Stored 0xE,0x4,0xA,0x7 → recalled 0xE,0x4,0xA,0x7 EXACTLY on BOTH seeds.

**VERDICT: PASS** — clean store+recall of written hex symbols in the matter memory, no LLM.

## Finding — the deep goal, cleanly demonstrated
With cells kept a margin off the box edge (x=6,11,16,21), every written hex digit is stored in and
recalled from the substrate's own physics with perfect fidelity, both seeds. Confirms the G126 diagnosis
(the lone error was an edge-cell layout artifact) and completes the deep-goal capstone: a persistent
written SYMBOL memory built bottom-up from the substrate, no LLM/transformer/embedding — only driven-atom
writes, spatially-selective maintenance, and presence-by-cell readout.
