# G118 — Clean multi-bit matter memory via REDUNDANCY (close the G117 fidelity gap)

## Motivation
G117 showed 4-bit matter-position memory at 0.88/bit (PARTIAL — below the 0.90 bar). The standard fix
(as G103/G104 did for the codec) is redundancy: place REDUN=2 carrier atoms per 1-bit cell, so the cell
reads 1 if at least one survives — robust to a single carrier loss/misplacement. If this lifts per-bit
accuracy to >=0.95, matter-position is a clean multi-bit content-addressable memory.

## Pre-registration (locked BEFORE run)
Same as G117 (K=4 cells x=8,13,18,23; cleared band; NPAT=4 random 4-bit patterns; DRIVE_T=320; POST=400)
EXCEPT each 1-bit cell gets REDUN=2 carriers (cell occupied = >=1 atom present). Both seeds. Chance 0.50.

**Bars (locked):**
- G118 PASS: per-bit accuracy >= 0.95 on both seeds.
NULL/PARTIAL below.

## Result
_(pending run)_
