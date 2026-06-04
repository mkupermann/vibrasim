# GEO-74 — Validate the full system on REAL-WORLD data (periodic table)

## Motivation
Every prior rung used synthetic/invented data. GEO-74 validates the system on GENUINE real-world structured
data (periodic table elements: real atomic numbers, symbols, groups, states) — testing factoid retrieval,
symbolic comparison, and semantic queries on facts that aren't constructed for the test.

## Pre-registration (locked BEFORE run)
- ~20 real elements with real attributes (atomic number, symbol, period, state-at-STP).
- Queries: factoid ("what is the symbol of <element>?"), comparison ("which has higher atomic number, X or
  Y?" via symbolic), semantic ("which element is a noble gas used in balloons?" -> helium, no name token).
- Metric: per-category accuracy. Bar: factoid >=0.8, comparison >=0.9 (symbolic), semantic >=0.6. PASS if the
  system works on REAL data as on synthetic. NULL/PARTIAL honestly otherwise.

## Result — PASS (real data)
| query type | accuracy |
|------------|----------|
| factoid (element -> symbol) | 1.00 |
| comparison (atomic number, symbolic) | 1.00 |
| semantic (description -> element, no name token) | 1.00 |

**VERDICT: PASS.** The full system works on GENUINE periodic-table data (real symbols, atomic numbers,
descriptions) at 1.00 across factoid retrieval, symbolic numeric comparison, and semantic description-matching
("noble gas used in balloons" -> Helium, no shared token). Not overfit to invented examples — it validates on
real structured data. **Honest note:** the periodic table is clean structured data with distinctive element
names, so it sits in the system's strong regime (like the clean synthetic cases); genuinely messy real data
would hit the noise/ambiguity limits (GEO-43, mitigated by entity-resolution GEO-44). But the core capabilities
transfer cleanly to real-world facts.
