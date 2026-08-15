# V2-P0 implementation plan

## Deliverable

A minimal isolated `vibrasim2` package that executes the frozen P0 arms,
computes the verdict, emits real frames to the wireframe viewer and leaves all
Vibrasim-I physics untouched.

## Sequence

1. Encode immutable P0 configuration and energy-ledger types.
2. Test the uncoupled periodic oscillator field against its discrete energy.
3. Add material oscillators and the registered Hamiltonian coupling term.
4. Test Stage-A gates, including a deliberately broken negative control.
5. Add the fixed equal-site, equal-edge topology fixtures and five arms.
6. Implement the ordered verdict as a pure function with table-driven tests.
7. Adapt real P0 frames to `WireframeFrame`.
8. Run Stage A. Run Stage B only if Stage A passes.
9. Independently re-run the verdict and review the ledger before reporting.

## Forbidden during execution

- editing frozen thresholds after a run;
- modifying `world/physics.py` or importing archived solver stacks;
- using the visual output as an acceptance metric;
- adding a parameter sweep after a NULL;
- pushing any commit.
