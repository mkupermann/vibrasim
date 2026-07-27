# Pattern: Write-time multi-band storage ≠ associative learning

## Source
BP-E4 PASS · BP-E5 PASS

## Claim
Dual-port ILW with distinct `seed_freq` reliably stores band identity on each side after idle. Decoders that use **experimenter-known centroids / pair tables** recover class at ceiling.

## What this is
- Engineered **content storage** at ports (§4.8)
- External map: human/protocol holds “class 0 means L=400,R=7000”
- Useful for curricula that *assume* a known code

## What this is not
- Multi-trial **learned** association (map not pre-baked into readout)
- Partner recovery when only one side was written
- Free-chemistry talent (C5 FREE still NULL)
- Temporal order (E3)

## Next if climbing “memory”
Require a bar that **fails** when the readout must invent the map, or when the partner side is never written, or when contingency is learned across trials without joint write every time.
