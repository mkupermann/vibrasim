# Port multi-trial association residual (no baked map)

## Finding
**BP-E162 PASS.** Multislot OFF. Fixed joint association c0 (L=500, R=5000) trained multi-trial (N=15 dual ILW), then L-only rewrite. R-side high-freq residual remains (≥0.80); L-only control has no R partner. L stays low.

## What it is / is not
- **Is:** multi-trial co-presence residual scored without external class map in readout.
- **Is not:** generative partner from L alone (E12 still holds — no creation after R kill).
- Engineered §4.8 ports write the association; residual is substrate co-presence after L-only probe.

## Doctrine
1. Multi-trial dual train → durable R residual under L-only probe.
2. Control (no dual train) → no spurious R partner.
3. Distinct from decade reconfig (E160/E161 multislot OFF last-write) and from content wipe (E155/E156 port kill leaves decade content).

## Extensions
- **E163 PASS:** c0→c1 sequential train; last-write residual (c1 R-low) under multislot OFF; control no spurious c1.
- **E164 PASS:** soft R-port kill does not clear residual (E155-class durability).

## Open
- Hard R-port kill residual (vs soft E164).
- Multislot ON multi-assoc residual capacity (interference / dual retention).
