"""3D near-real-time viewer for the EQMOD-2 energy memory (BET-110).

Polls ~/.eqmod/energy/state.npz (written by run_bet110_energy.py --demo) every
~1-2 s and renders the modular geometric network in 3D: nodes coloured by
activation (blue −1 ... red +1), edges coloured by learned weight sign, and a HUD
(phase / epoch / completion / energy). Decoupled from the compute, so the
simulation is never blocked by rendering.

  # terminal 1 — produce snapshots:
  python tools/run_bet110_energy.py --demo
  # terminal 2 — watch in 3D:
  python tools/viz3d_energy.py

  python tools/viz3d_energy.py --snapshot frame.png   # render one frame (smoke test)
"""
import sys, time
import numpy as np
from pathlib import Path

STATE_FILE = Path.home() / '.eqmod' / 'energy' / 'state.npz'


def load_state(retries=3):
    for _ in range(retries):
        try:
            d = np.load(STATE_FILE, allow_pickle=False)
            return {k: d[k] for k in d.files}
        except Exception:
            time.sleep(0.1)
    return None


def edge_list(W, keep_frac=0.18):
    """(i,j,w) for the strongest |w| connections, for a legible 3D graph."""
    N = W.shape[0]
    iu, ju = np.triu_indices(N, k=1)
    w = W[iu, ju]
    nz = np.abs(w) > 1e-9
    iu, ju, w = iu[nz], ju[nz], w[nz]
    if len(w) == 0:
        return np.zeros((0, 2), int), np.zeros(0)
    thr = np.quantile(np.abs(w), 1.0 - keep_frac)
    sel = np.abs(w) >= thr
    return np.column_stack([iu[sel], ju[sel]]), w[sel]


def build_edges_polydata(pos, edges):
    import pyvista as pv
    if len(edges) == 0:
        return pv.PolyData(pos)
    lines = np.hstack([np.full((len(edges), 1), 2), edges]).astype(np.int64).ravel()
    pd = pv.PolyData(pos)
    pd.lines = lines
    return pd


def render_once(state, plotter, actors):
    import pyvista as pv
    pos = state['pos'].astype(float)
    act = state['state'].astype(float)
    W = state['W'].astype(float)
    phase = str(state['phase']); epoch = int(state['epoch'])
    acc = float(state['acc']); energy = float(state['energy'])

    # nodes
    if actors.get('nodes') is None:
        nm = pv.PolyData(pos); nm['act'] = act
        actors['node_mesh'] = nm
        actors['nodes'] = plotter.add_mesh(
            nm, scalars='act', cmap='coolwarm', clim=[-1, 1],
            render_points_as_spheres=True, point_size=30,
            scalar_bar_args={'title': 'activation'})
    else:
        actors['node_mesh']['act'] = act

    # edges (rebuild — connectivity is fixed but cheap to recreate)
    e, w = edge_list(W)
    em = build_edges_polydata(pos, e)
    if actors.get('edges') is not None:
        plotter.remove_actor(actors['edges'])
    actors['edges'] = plotter.add_mesh(em, color='gray', line_width=1,
                                       opacity=0.18, show_scalar_bar=False)

    txt = (f"EQMOD-2 energy memory\nphase: {phase}\nepoch: {epoch}\n"
           f"completion: {acc:.3f}\nenergy: {energy:.1f}")
    if actors.get('text') is not None:
        actors['text'].SetText(2, txt)
    else:
        actors['text'] = plotter.add_text(txt, font_size=11, name='hud')


def main():
    import pyvista as pv
    snap = None
    if '--snapshot' in sys.argv:
        snap = sys.argv[sys.argv.index('--snapshot') + 1]

    st = load_state()
    if st is None:
        print(f"No state yet at {STATE_FILE}. Start: python tools/run_bet110_energy.py --demo")
        if snap is None:
            print("Waiting for the first snapshot...")
            while st is None:
                time.sleep(1); st = load_state()
        else:
            return

    plotter = pv.Plotter(off_screen=snap is not None, title="EQMOD-2 energy memory")
    plotter.set_background('white')
    actors = {}
    render_once(st, plotter, actors)
    plotter.view_isometric()

    if snap is not None:
        plotter.screenshot(snap)
        print(f"wrote {snap}")
        return

    plotter.show(interactive_update=True, auto_close=False)
    print("Live viewer running (close the window to stop). Polling every ~1.2 s.")
    try:
        while True:
            time.sleep(1.2)
            st = load_state()
            if st is not None:
                render_once(st, plotter, actors)
            plotter.update()
    except Exception as e:
        print(f"[viewer closed: {e}]")


if __name__ == "__main__":
    main()
