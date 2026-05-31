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

## RESULT (2026-05-31): consolidation does NOT close recall — it slightly hurts

| Variant | gain | consol | wall | stim-frac | post-frac | uni | verdict |
|---------|-----:|-------:|------|----------:|----------:|----:|---------|
| 109a | 4 | 5 | ON  | 0.33 | 0.26 | 0.25 | NULL |
| 109b | 4 | 4 | ON  | 0.33 | 0.26 | 0.25 | NULL |
| 109c | 6 | 5 | ON  | (truncated/slow) | | | — |
| 109d | 4 | 5 | OFF | 0.00 | 0.06 | 0.00 | NULL (control) |
| 109e | 4 | 0 | ON  | **0.67** | **0.32** | 0.20 | NULL (baseline, best) |

With the lock-set now cleared at blank, consolidation worked correctly — and made
things slightly WORSE: the no-consolidation baseline (109e) stays best at 3/4
bars (0.67/0.32/0.20), while locking (109a/b) dropped to 0.33/0.26 AND broke
containment (uni 0.25). Strength-locking is NOT the recall fix.

### Conclusion — recall is structurally capped, not a decay problem

Across BET-105→109 the bridge-graph write + wall + charge-blank cleanly reaches
3/4 bars (selective firing, selective write, containment) but persistent recall
sits at ~0.3 regardless of gain, gating, or locking. The fade is therefore NOT
strength decay (locking it doesn't help) — it is the cascade being metastable and
the region-mean readout diluted by bridge TURNOVER (new bridges born weak). This
is a structural property of the tiny, churning lattice. **Strategic checkpoint:
the spontaneous-substrate memory programme is at its honest ceiling (3/4 bars);
closing recall would require a fundamentally larger/stabler substrate or a
turnover-immune readout — i.e. a redesign, not another knob.** See
docs/NEW_DIRECTION.md.
