# Closure — latch-clear inhibit (NOT/XOR) family

**Written 2026-07-20** after PRIM11, E40, E41

| ID | Verdict | Note |
|----|---------|------|
| PRIM11 XOR | NULL | both-clear ok-ish; single OR broken |
| E40 concurrent NOT | NULL | L+I re-latches |
| E41 sequential NOT | NULL | L-then-I does not clear R |

## Closed
Hard **latch-zero inhibit** as NOT/XOR actuator is **not** established under current timing/topology. Primitive knobs exist (`fire_zero_latch_radius`, `k_zero_latch_emitter`) but do not yield defensible NOT.

## Still true
PRIM9 coincidence **AND** PASS. Port OR (E34) PASS. Circuit library without NOT.

## Reopen only with
New inhibit mechanism (e.g. bridge-local suppress, strength kill) under new ID.
