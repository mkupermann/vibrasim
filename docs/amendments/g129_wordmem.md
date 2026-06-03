# G129 — Store + recall a WORD ("EQMOD") in the matter memory (deep-goal capstone)

## Pre-registration (locked BEFORE run)
Extend G128 (single chars) to a full word: write each character of "EQMOD" into the 2-row matter memory in
turn (drive carriers, hold POST=300 with maintenance, read back the byte → char), concatenating the recalls
into the recovered word. Same layout as G128 (rows y=10,20; cells x=6,11,16,21). Both seeds. No LLM.

**Bars (locked):**
- G129 PASS: the recalled word == "EQMOD" exactly (both seeds).
NULL/PARTIAL otherwise.

## Result
Stored "EQMOD" → recalled "EQMOD" EXACTLY on BOTH seeds. **VERDICT: PASS.**

## Finding — a WORD round-trips through the matter memory
The substrate writes each character of "EQMOD" into its matter-position memory and reads the full word
back exactly, both seeds, no LLM — the tangible deep-goal demonstration.

Honest scope: characters are stored SEQUENTIALLY (one at a time in the 2-row memory), so this is a
write/read register cycle over a byte stream, not a whole word held simultaneously (that needs a larger
2D cell grid). The result is real and general (any byte stream works) but it is a faithful DATA register,
not a cognitive system — it carries the bits, it does not understand them. The READ/WRITE machinery is
established; the substrate-specific fact is that this physics holds text positionally where activity never
could.
