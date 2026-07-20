# Pattern: Charge latch for end-state partner readout

## Source
PRIM6-D0 PASS · E21 PASS · contrast E13/E18/E19 NULL · E14/E20 peak PASS

## Claim
Membrane `k_charge` is for fast dynamics; **end-state** content-addressable partner needs a **separate latched mark** (`k_latch`) filled by bridge charge prop.

## Do
- Enable `charge_latch_enabled` when scoring after idle without re-drive.
- Keep peak readouts for protocols that intentionally avoid latch.

## Don't
- Treat membrane end-state zeros as “routing failed” (see `peak_not_endstate_charge_readout`).
- Claim free persistent activity without naming the latch as engineered.
