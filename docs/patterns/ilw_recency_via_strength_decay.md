# Pattern: Recency via ILW strength decay (PRIM3)

## Source
PRIM3-D0 PASS · BP-E7 PASS · contrast E3 NULL (tau=0)

## Claim
With `ilw_strength_decay_tau > 0`, older port mass fades; after gap + later one-sided write, **strength decode recovers last side**. With tau=0, same protocol is chance (E3).

## Use
Curriculum steps that need **order / recency** must enable PRIM3 and a temporal gap — do not claim order from equal-N ILW alone.

## Honesty
Engineered leak; L4 nodes still permanent (identity); only strength leaks toward 1.0.
