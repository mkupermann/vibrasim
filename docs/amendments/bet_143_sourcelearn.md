# BET-143 — Learn code fragments FROM sources, recombine, grow online

Pre-registered: 2026-05-31 (BEFORE the run). The system mines primitive operations
(filters/maps/reducers) from REAL Python source via AST, with trigger words from the
function names, then recombines them on demand. Ingesting a new source grows what it
can generate.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| T143a | Mines operations from source | >= 8 distinct operations extracted |
| T143b | Recombines correctly | >= 0.80 of test queries produce correct code (executed) |
| T143c | New combinations | generated pipelines were not whole functions in the source |
| T143d | Online growth | a query needing a new op fails before, succeeds after a new source |

## RESULT (2026-05-31): PASS

Mined 10 functions → 10 distinct ops (filters x>0, x<0, x%2; maps x*x, 2*x; reducers
sum/max/min/len). 5/5 recombination queries produced correct executed code. Online
growth: "the largest of the cubed positive" was impossible before, worked after
ingesting a source defining `cubed`. All bars ✓. Provenance: AST fragment mining +
rule-based program synthesis, no LLM/transformer.

NOTE (honest, see LOGBOOK 2026-05-31): this works, but it has essentially NOTHING to do
with the EQMOD PHYSICAL substrate (vibrations → electrons → atoms → molecules). It is
abstract symbolic ML wearing the "substrate" label. That gap is the real issue Michael
named.
