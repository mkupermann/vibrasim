# BET-109 — Consolidation, Fixed: Lock Only What's Written During STIM

Pre-registered: 2026-05-31 (BEFORE any run). BET-108's consolidation was sound but
the warmup-lock bug locked every bridge (blank reset strength, not the lock-set).
Fix applied: `blank_bridges` now also clears `world._consolidated`. BET-109 re-runs
the same sweep so consolidation locks ONLY bridges written during STIM.

## Variants (parallel) — identical to BET-108, with the fix in effect

| Label | gain | consol | wall |
|-------|-----:|-------:|------|
| 109a | 4 | 5 | ON |
| 109b | 4 | 4 | ON |
| 109c | 6 | 5 | ON |
| 109d | 4 | 5 | OFF (control) |
| 109e | 4 | 0 | ON (baseline ≈ 0.32) |

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

PASS (wall-ON consol variant, Tc ≥ 0.5, 109d leaking, 109e ≈ 0.32) = MILESTONE:
first clean selective, persistent, content-bearing memory via a modular
bridge-graph write with consolidation — substrate primitives only, no LLM.

If recall still < 0.5 with locking working correctly: the fade is bridge TURNOVER
diluting the region-mean readout (new bridges born weak), not strength decay —
this becomes a strategic checkpoint (the programme is at 3/4 bars after ~20
amendments; selective write + containment solid, recall the structural gap).

## RESULT

_(to be filled after all variants complete)_
