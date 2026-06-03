# Pattern — Parallel spatial channel (quiet-substrate real-time MIMO line)

## What it is
The quiet substrate (free-vibration background culled, `lambda_gen=0`) acts as a clean, high-resolution
PARALLEL communication line: multiple spatially-separated input sites each carry an independent
information stream, and a linear ridge decoder per site recovers each stream crosstalk-free, in the
same tick, with no persistence. Established concept (linear MIMO channel); this is its in-substrate
realization and measured pitch.

## When to use
Any real-time transduction task that needs to move multiple independent signals through the substrate
simultaneously — multi-symbol input encoding, parallel sensor fan-in, routing. Use it INSTEAD of the
bridge-memory route when the task does not require storage (the storage route is a closed negative,
G88–G96).

## How (recipe)
1. Settle a lattice, then quiet it: `cull_free_vibrations(w, keep_frac=0.0)` and set `lambda_gen=0`.
2. Place channels at x-sites separated by the pitch (>= ~3 units in a 30-unit box, measured G97).
3. Per integration window, `inject_tight(w, cfg, box, x_site, n=14)` at each ACTIVE channel.
4. Read a fine free-vibration density grid along x (G97 used 10 bins / 30 units).
5. Decode each channel with an independent ridge regressor: `solve(XtX + λI, Xt(y-0.5))`; sign of the
   prediction is the bit. Re-quiet between windows to clear residual.

## Evidence
- G83: single quiet-substrate input reads at balanced-accuracy 1.00 (the active substrate drowns it).
- G97: two channels decode at 1.00 down to pitch d=3 (box=30), crosstalk at/near chance (0.46–0.58),
  both seeds. Implies ~10 independent spatial channels per axis.

## Caveats / honesty
- The decoder is LINEAR. The substrate reads parallel inputs but does NOT combine them nonlinearly in
  real time (spatial XOR is NULL: G82/G83/G87). This is a channel, not a computer.
- Accuracy 1.00 is partly because injection is spatially tight and the task is single-site detection;
  the result extends G83 rather than surprising it. The measured PITCH is the new datum.
- Requires the quiet regime; in the active substrate homogeneous self-activity drowns the channels (the
  G83 root).
