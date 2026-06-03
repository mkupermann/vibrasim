# G119 — CLEAN multi-bit matter memory via wider SPACING (the G118-diagnosed fix)

## Motivation
G117 reached 0.88/bit and G118 showed redundancy does NOT improve it — the error is SYSTEMATIC/spatial
(carriers at cell boundaries / overlapping read radii). The principled fix (the G104 analog) is to respect
SPACING: fewer, wider-pitched cells with a tighter read radius and guard gaps. If per-bit jumps to >=0.95,
matter-position is a CLEAN multi-bit content-addressable memory.

## Pre-registration (locked BEFORE run)
K=3 cells at x=7,14,21 (pitch 7, well above G97 ~3) with read radius 1.5 (4-unit guard gaps, no overlap).
NPAT=3 random 3-bit patterns; DRIVE_T=250; POST=300; cleared band; cell occupied = >=1 atom. Both seeds.
Chance 0.50.

**Bars (locked):**
- G119 PASS: per-bit accuracy >= 0.95 on both seeds → clean multi-bit matter memory.
NULL/PARTIAL below.

## Result
_(pending run)_
