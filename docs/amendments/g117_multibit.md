# G117 — Content-addressable MULTI-BIT memory via matter position (scales the G116 breakthrough)

## Motivation
G116 demonstrated a 1-bit selective+persistent store via matter position. G117 scales it: write a random
K-bit pattern across K cells (drive a carrier atom to each 1-cell, leave 0-cells empty), POST, read each
cell's occupancy, and recover the pattern. High per-bit accuracy across many random patterns would make
matter-position a real content-addressable multi-bit memory — the activity-based programme never reached
even 1 selective bit.

## Pre-registration (locked BEFORE run)
Cleared band (|y-15|<4) with K=4 cells at x=8,13,18,23 (pitch 5 > G97 ~3). For each of NPAT=6 random
4-bit patterns (fresh world): drive one carrier per 1-bit to its cell; maintain the band (clear background
except carriers); DRIVE_T=320, then release; POST=800; read cell occupancy (>=1 atom → bit 1). Per-bit
accuracy = fraction of all bits recovered correctly across the 6 patterns. Both seeds. Chance = 0.50.

**Bars (locked):**
- G117 PASS: per-bit accuracy >= 0.90 on both seeds.
NULL/PARTIAL below that.

## Result
_(pending run)_
