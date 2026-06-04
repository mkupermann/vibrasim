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
