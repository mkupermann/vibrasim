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
- **E165 PASS:** hard R-port kill does not clear residual (E156-class).
- **E166 PASS:** multislot ON retains both R high+low after c0+c1 train (capacity); c0-only high-only control.

## Doctrine (E162–E168 CLOSED PASS — see bp_port_residual_curriculum_closure.md)
1. Multi-trial dual train → residual co-presence without baked map.
2. Multislot OFF → last-write residual reconfig (c0→c1).
3. Soft/hard port kill does not wipe residual content.
4. Multislot ON → multi-assoc capacity (both partner bands retained).
5. Temporal gap L→R residual works (E167); write order order-blind (E168).

## Boundary: selective residual
- **E169 NULL / E170 NULL:** after multi-assoc capacity train, L-only probe band does **not** select R partner mean (B2=B3=0). Pair-links do not fix. Capacity residual ≠ selective associative readout.
- Residual under generative/partner-from-L alone still No (E12).
- Free talent still blocked; residual family is engineered-port content, not free dual.
