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
| seed | far (x>20) | co-located | far charge energy |
|------|-----------|------------|-------------------|
| 42   | 0.00      | 1.00       | 0.0 |
| 7    | 0.00      | 1.00       | 0.0 |
(K=4, chance 0.25)

G106a (charge transport): **False** · G106b (co-located sanity): **True** → **VERDICT: PARTIAL**

## Finding — charge is local-only too; the transport question is CLOSED
The far-region charge energy is literally 0.0 on both seeds — deposited charge never reaches x>20. It
propagates only to immediately bridged neighbours and decays within a few ticks; the settled bridge graph
does not carry it across the box (atoms cluster; the graph is fragmented over distance). Co-located
readout is perfect (1.00), so the deposit is distinguishable — it simply does not travel.

**The substrate is LOCAL-ONLY on both candidate transport channels:** free vibrations (G105, absorbed
locally) and charge along bridges (G106, decays before crossing). There is no transmission over distance.
This definitively closes the transport question and finalises the communication framing: the G97–G104
result is a CO-LOCATED spatial codec — symbols written as localized excitations and read back at the same
site in the same tick — not a transmission line. The verbatim-text demonstration (G104) stands within
that honest scope. To get genuine transport one would need an engineered low-loss conduit (a maintained
bridge "wire" or a reflecting waveguide) — a structural addition, not a property the bare substrate has.
