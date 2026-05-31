"""Render a few 3D frames of the EQMOD-2 energy memory doing a denoising recall:
a corrupted cue relaxing back into the stored attractor. For showing the result.

  python tools/showcase_energy.py            # writes showcase_*.png
"""
import sys
import numpy as np
import pyvista as pv
from world.energy import EnergyNet, make_patterns

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def edges(W, keep=0.18):
    N = W.shape[0]; iu, ju = np.triu_indices(N, 1); w = W[iu, ju]
    nz = np.abs(w) > 1e-9; iu, ju, w = iu[nz], ju[nz], w[nz]
    if not len(w):
        return np.zeros((0, 2), int)
    thr = np.quantile(np.abs(w), 1 - keep)
    sel = np.abs(w) >= thr
    return np.column_stack([iu[sel], ju[sel]])


def render(pos, state, W, title, fname):
    pl = pv.Plotter(off_screen=True, window_size=[1100, 820])
    pl.set_background('white')
    # real 3D spheres (radius in world units) so nodes are large and vivid
    nm = pv.PolyData(pos); nm['act'] = state
    balls = nm.glyph(scale=False, orient=False,
                     geom=pv.Sphere(radius=0.7, theta_resolution=14, phi_resolution=14))
    pl.add_mesh(balls, scalars='act', cmap='coolwarm', clim=[-1, 1],
                smooth_shading=True, specular=0.2,
                scalar_bar_args={'title': 'activation (-1 ... +1)'})
    e = edges(W)
    if len(e):
        em = pv.PolyData(pos)
        em.lines = np.hstack([np.full((len(e), 1), 2), e]).astype(np.int64).ravel()
        pl.add_mesh(em, color='dimgray', line_width=1, opacity=0.12)
    pl.add_text(title, font_size=13, name='t', color='black')
    pl.view_isometric()
    pl.camera.zoom(1.5)
    pl.screenshot(fname)
    pl.close()
    print(f"wrote {fname}")


if __name__ == "__main__":
    net = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.6, seed=0)
    pats = make_patterns(net, n_patterns=6, seed=7)
    for _ in range(300):
        net.train_epoch(pats, cue_frac=0.4, lr=0.02, relax_steps=20)

    rng = np.random.default_rng(11)
    target = pats[2]
    # noisy input: flip 30% of ALL bits, then relax FREELY (no clamp) so the
    # attractor corrects the errors — classic energy-based denoising.
    noisy = target.copy()
    flip = rng.random(net.N) < 0.30
    noisy[flip] *= -1
    net.state = noisy.astype(float)
    acc0 = float(np.mean(np.sign(net.state) == np.sign(target)))
    render(net.pos, net.state.copy(), net.W * net.M,
           f"EQMOD-2 energy memory  —  noisy input, 30% bits flipped (t=0)\n"
           f"overlap with target: {acc0:.2f}",
           "showcase_1_cue.png")

    frames = []
    net.relax(None, None, 24, record=frames)
    mid = frames[6]
    accm = float(np.mean(np.sign(mid) == np.sign(target)))
    render(net.pos, mid.copy(), net.W * net.M,
           f"settling into the attractor (t=6)\noverlap with target: {accm:.2f}",
           "showcase_2_settling.png")

    settled = frames[-1]
    accf = float(np.mean(np.sign(settled) == np.sign(target)))
    render(net.pos, settled.copy(), net.W * net.M,
           f"recalled — slid into the energy valley\noverlap with target: {accf:.2f}",
           "showcase_3_recalled.png")
    print(f"overlap: cue {acc0:.2f} -> settling {accm:.2f} -> recalled {accf:.2f}")
