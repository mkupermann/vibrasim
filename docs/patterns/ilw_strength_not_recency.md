# Pattern: ILW strength is count-mass, not recency

## Source
BP-E3 NULL (B1_last=0.45; B2 equal imbalance=0; B3 both sides populated=1.0)

## Claim
After sequential ILW writes with the **same event count** on each side (midplane + ILW), mean/total `k_strength` on L vs R does **not** decode which side was written last. Strength tracks **how many** local writes, not **when**.

## Why
`apply_ilw_port_event` adds fixed `ilw_delta_strength` (and seeds/nudges freq). No last-write boost, no recency-weighted decay between equal batches. Equal N ⇒ equal mass after idle.

## Do / don't
- **Do** use strength (or presence) to decode *which side was written* after one-sided write (E1/E2).
- **Do not** claim temporal order / sequence from equal-strength dual write without a new channel.
- **Do not** retune E3's 0.85 bar to rescue the claim.

## Next mechanisms (if order is needed)
Named new amendment only: inter-write decay gap, BTSP-style eligibility, or separate order-encoding structure — not re-running E3.
