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
import sys, time, threading
import numpy as np
from pathlib import Path

# ensure repo root on path so `world` / `tools` import when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

STATE_FILE = Path.home() / '.eqmod' / 'energy' / 'state.npz'


def load_state(retries=4):
    for _ in range(retries):
        try:
            with np.load(STATE_FILE, allow_pickle=False) as d:  # close promptly
                return {k: d[k] for k in d.files}
        except Exception:
            time.sleep(0.08)
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

    # nodes as real 3D sphere glyphs (radius in world units) so they are large
    # and vividly coloured. name= replaces the previous actor each frame.
    nm = pv.PolyData(pos); nm['act'] = act
    balls = nm.glyph(scale=False, orient=False,
                     geom=pv.Sphere(radius=0.7, theta_resolution=12, phi_resolution=12))
    plotter.add_mesh(balls, scalars='act', cmap='coolwarm', clim=[-1, 1],
                     smooth_shading=True, name='nodes',
                     scalar_bar_args={'title': 'activation (-1 ... +1)'})

    # edges (rebuild — cheap; weights change during training)
    e, _ = edge_list(W)
    em = build_edges_polydata(pos, e)
    plotter.add_mesh(em, color='dimgray', line_width=1, opacity=0.12,
                     name='edges', show_scalar_bar=False)

    plotter.add_text(
        f"EQMOD-2 energy memory\nphase: {phase}\nepoch: {epoch}\n"
        f"completion: {acc:.3f}\nenergy: {energy:.1f}",
        font_size=12, name='hud', color='black')


def main():
    import pyvista as pv
    snap = None
    if '--snapshot' in sys.argv:
        snap = sys.argv[sys.argv.index('--snapshot') + 1]

    # --demo: run the snapshot producer in a background thread so a SINGLE command
    # shows a live, changing view (no need for a second terminal).
    if '--demo' in sys.argv and snap is None:
        from tools.run_bet110_energy import demo_run
        threading.Thread(target=demo_run, daemon=True).start()
        print("started snapshot producer in background (--demo)")
        # wait for the first snapshot to appear
        for _ in range(60):
            if STATE_FILE.exists():
                break
            time.sleep(0.5)

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
    plotter.camera.zoom(1.4)

    if snap is not None:
        plotter.screenshot(snap)
        print(f"wrote {snap}")
        return

    print("Live viewer running (close the window to stop). Refreshing ~1.2 s.")
    prog = {'k': None}

    def _tick(*_args):
        s = load_state()
        if s is None:
            return
        render_once(s, plotter, actors)
        key = (str(s['phase']), int(s['epoch']))
        if key != prog['k']:
            print(f"  frame: phase={key[0]} epoch={key[1]} "
                  f"completion={float(s['acc']):.3f}", flush=True)
            prog['k'] = key

    # Reliable live updates: a VTK interactor timer fires _tick during show().
    try:
        plotter.add_callback(_tick, interval=1200)
        plotter.show()
    except Exception:
        # fallback: non-blocking show + manual poll loop
        plotter.show(interactive_update=True, auto_close=False)
        try:
            while True:
                time.sleep(1.2)
                _tick()
                plotter.render(); plotter.update()
        except Exception as e:
            print(f"[viewer closed: {e}]")


if __name__ == "__main__":
    main()
