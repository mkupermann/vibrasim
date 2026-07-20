# Pattern: Port circuit primitives (engineered graph)

## Source
E29–E37 PASS chain · PRIM5/6/8 · replace doctrine

## Circuit library (honest §4.8)

| Primitive | Result | Notes |
|-----------|--------|--------|
| Two-hop relay | E29 PASS | replace OFF |
| Three-hop | E32 PASS | |
| Four-hop | E36 PASS | |
| Parallel isolation | E31 PASS | distinct mids |
| Shared mid crosstalk | E33 PASS | leaks by design |
| Fan-in OR | E34 PASS | either L → R |
| Diamond redundancy | E35 PASS | survives one mid kill |
| Midplane dual chains | E37 PASS | half-box isolation |
| Curriculum overwrite | E28 PASS | replace ON |
| Table-free map + ablation | E25 PASS | |
| Fan-in **AND** | PRIM9 PASS | coincidence_and + k_coincidence_gate |
| Structural **NOT** | PRIM12 PASS | fire_kill_bridge_radius + emitter |
| **XOR** | E42 PASS | OR path + coincidence Mand + structural kill |

## Incompatible defaults
- **replace ON** ↔ multi-hop chains (E30)
- **shared mid** ↔ path isolation (E33)

## Not free talent
All above are engineered ports + ILW + bridges + latch. Free dual-inject talent remains blocked (C1–C8, PRIM7).
