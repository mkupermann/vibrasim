# Content+cascade multi-hop fire-select hybrid — CLOSED PASS (E186–E190)

**Date:** 2026-07-26  
**Scope:** Dual spatial content cascades; fire-select at R; mid-hop surgery; hop depth 2–3.

## Verdicts

| ID | Verdict | Finding |
|----|---------|---------|
| E186 | PASS | Dual-path two-hop L→M→R content cascade fire-select |
| E187 | PASS | Mid-hop hard kill M0 silences path0; path1 survives |
| E188 | PASS | Mid-hop kill + restore multi-trial |
| E189 | PASS | Soft mid-hop kill parity |
| E190 | PASS | Triple-hop L→M→A→R content cascade fire-select |
| E191 | PASS | Incomplete cascade (missing last hop) fails R select |
| E192 | PASS | Graded bridge_prop_min_strength=0.5 still supports fire-select |
| E193 | PASS | Long-idle durability T=400 multi-hop fire-select |

## Doctrine
1. Multi-hop **content** cascades support fire-select (not only one-hop pair residual).
2. Mid-hop is **critical** for path prop and **path-local** under spatial split.
3. Soft and hard mid-hop kill both work (E187/E189); multi-trial restore (E188).
4. Doctrine **scales to three hops** (E190).
5. **End-to-end hop chain necessary**: omit terminal hop → no R select (E191).
6. **Graded prop** (BET-107) compatible with trained pair-link cascades (E192).
7. Multi-hop fire-select **durable** after long idle (E193).

## Do not farm
Re-running E186–E193 bars without new hop/topology question.

## Open
- Free talent still CLOSED PARTIAL
