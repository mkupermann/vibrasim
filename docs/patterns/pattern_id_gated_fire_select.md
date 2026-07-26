# Pattern-id G12 gated fire-select

## Finding
**E194–E196 PASS.** Multi-assoc pair-link train + `firing_eligibility_gate` + `k_pattern_id` enables selective multi-trial readout.

## Protocol
1. Tag association endpoints with pattern_id (post-hoc by band **or** train-time via `active_pattern_id` during ILW — E196).
2. Set `active_pattern_id` to target association.
3. Freq-matched L fire + bridge latch scores R partner.
4. Wrong `active_pattern_id` blocks wrong-arm select (E194 B3).

## Doctrine
1. G12 gate is a **new selective class** beyond E171 freq-matched fire alone.
2. Multi-trial switch durable without retrain (E195).
3. Train-time tagging works on shared multislot ports (E196).

## Distinct from
- Residual co-presence (E162–E168) — no fire/gate
- Mean selective residual NULL (E169/E170)
- Split-port spatial surgery (E177–E183)

## Doctrine (E197–E201)
- Ambient (pid=0) fires under gate → **positive select works without tags**.
- **Wrong-arm block requires non-zero mismatched tags** (E197).
- **L-only tags suffice** for wrong-arm block; R partner tags not required (E201).
- **R-only tags do not block** wrong-arm (E202 NULL); firing-side (L) tags are load-bearing.
- **Reverse fire-select under G12** works (E205 PASS); wrong-pattern reverse blocked.
- **Reverse multi-trial switch** pid1→pid2→pid1 durable (E206 PASS).
- **Reverse train-time tags** suffice without post-hoc (E207 PASS).
- **Reverse long-idle durable** after T=400 (E208 PASS).
- **Reverse split soft-kill** L1 arm-selective (E209 PASS).
- **Reverse soft-kill restore** via retrain (E210 PASS).
- **Forward+reverse coexist** same-world multi-trial (E211 PASS).
- **Reverse split hard-kill** L1 arm-selective (E212 PASS; complements soft E209).
- **Reverse hard-kill restore** via retrain (E213 PASS).
- **Cascade reverse under G12** multi-hop (E215 PASS).
- **Cascade reverse multi-trial switch** under G12 (E216 PASS).

## Soft-kill arm surgery (E198–E200)
- Shared PORT_R soft kill wrong-arm **spills** (E198 NULL) — silences both pid arms.
- Split-port soft kill R1 + G12 **PASS** (E199): pid2 silenced, pid1 survives.
- Retrain restore after soft kill **PASS** (E200): pid2 returns without harming pid1 curriculum.

## Open
- Pattern_id on free dual talent (E222–E223 hybrid ambient NULL)
- Auto-tag without engineered active_pattern_id: **closed negative** E225 PASS (no content auto-tag)
