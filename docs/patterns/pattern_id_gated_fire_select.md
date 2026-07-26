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

## Doctrine (E197)
- Ambient (pid=0) fires under gate → **positive select works without tags**.
- **Wrong-arm block requires non-zero mismatched tags** (E197).

## Open
- Pattern_id on free dual talent
- Auto-tag without engineered active_pattern_id curriculum
