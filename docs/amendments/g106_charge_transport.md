# G106 — Does CHARGE propagate across distance along the bridge graph? (transport, 2nd channel)

## Motivation
G105 showed free vibrations do not carry a symbol over distance (absorbed locally) — the spatial codec is
co-located. The substrate's OTHER transport candidate is charge moving along the bridge graph
(apply_bridge_charge_propagation / apply_bridge_atom_propagation). G106 tests it: deposit charge into
LEFT-edge atoms at one of K y-positions, let it propagate along bridges, and decode the RIGHT-edge atom
charge pattern. If the right end decodes the input symbol, the substrate CAN transmit over distance via
charge (and a scoped "transmission" claim is restored); if not, the substrate is confirmed local-only on
both its channels.

## Pre-registration (locked BEFORE run)
Keep the settled lattice (atoms + bridges; lambda_gen=0; do NOT blank bridges or cull atoms). K=4
y-channels at y=linspace(8,22,4). Per symbol: zero all atom charge, deposit charge Q into alive atoms with
x<10 and |y−chan_y|<2.5, run PROP=10 ticks (bridge/charge propagation active in tick), then read the
y-binned SUM of atom charge in the FAR region x>20 (transport) and over the whole box (co-located control).
Decoder: multiclass linear, held-out 70/30, calibrated on random traffic.

**Bars (locked):**
- G106a transport via charge: far-region (x>20) decode >= 0.85 both seeds → genuine transport.
- G106b co-located sanity: whole-box decode >= 0.85 both seeds (charge deposited distinguishably).
If G106a → transport exists via charge. If only G106b → substrate is local-only on BOTH channels
(vibration G105 + charge G106); the co-located-codec framing is final. Chance = 0.25.

## Result
_(pending run)_
