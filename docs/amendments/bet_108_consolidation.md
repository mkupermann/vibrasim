# BET-108 — Consolidation (Freeze-on-Write): Close the Recall Gap

Pre-registered: 2026-05-31 (BEFORE any run). BET-106 solved selective write +
containment (106a: Ta/Tb/Td ✓); the lone gap was recall metastability (Tc 0.32 —
latched stim bridges drift back below mid in POST). BET-107 (gating) was the wrong
tool (broke the write bootstrap). Correct lever: consolidate the written pattern.

## Mechanism

`apply_correlation_plasticity` gains `bridge_consolidate_threshold`: once a bridge
strength reaches it, the bridge is LOCKED at the strong well (high), immune to
further decay/turnover. A written stim bridge thus cannot fade in POST; control
bridges never reach the threshold so are never locked. Built on BET-106's working
ungated regime (bridge propagation gain, charge-blank, wall).

## Variants (parallel, pre-committed) — n_emit=0, tau_LTP=1.0, charge-blank ON

| Label | gain | consol | wall | regime |
|-------|-----:|-------:|------|--------|
| 108a | 4 | 5 | ON  | lock near strong well |
| 108b | 4 | 4 | ON  | lock just past mid |
| 108c | 6 | 5 | ON  | stronger sustain + lock |
| 108d | 4 | 5 | OFF | control (should leak) |
| 108e | 4 | 0 | ON  | NO consolidation (= BET-106a baseline ≈ 0.32) |

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing (gate) | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

A variant PASSES if Ta–Tc AND Td. PASS (wall-ON, 108d leaking, 108e showing the
baseline 0.32 to attribute the gain to consolidation) = the MILESTONE: first
clean selective, persistent, content-bearing memory via a modular bridge-graph
write with consolidation — substrate primitives only, no LLM. If Tc still < 0.5
even with locking, the readout fade is from bridge TURNOVER (new bridges at low
dilute the region mean), not strength decay → next lever targets turnover.

## RESULT

_(to be filled after all variants complete — per-variant + pattern)_
