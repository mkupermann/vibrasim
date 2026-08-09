"""BP-B7 fingerprint with ambient free field — continuous lab headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from tools.classify_molecules import _ground_atom_decades, species_fingerprint
from world.config import WorldConfig
from world.physics import tick
from world.state import World

SEEDS, N, T, N_AMB = (131, 137), 20, 500, 200


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 80., 80.),
        n_vibrations_max=1024, n_nodes_max=512, rng_seed=seed,
        lambda_gen=0., lambda_dec=0., lambda_dec_mol=0.,
        node_thermal_speed=0., mol_fusion_enabled=False,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        speed_min=5., speed_max=20.,
    )


def fdec(d, o=0.):
    return float(10**d * 3 + o)


def plant_mol(w, lab, pos):
    d0, d1 = (3, 3) if lab == 0 else (3, 4)
    f0, f1 = fdec(d0), fdec(d1, 100)
    box = np.array(w.config.box_size)
    a0 = w.allocate_node(pos=(pos+[box[0]*0.3,0,0])%box, freq=f0, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    a1 = w.allocate_node(pos=(pos+[0,box[1]*0.3,0])%box, freq=f1, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    m = w.allocate_node(pos=pos.copy(), freq=f0+f1, pol=True, level=5,
                        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1)
    w.k_strength[m] = 10.0
    return m


def inject_ambient(w, rng, n):
    box = np.array(w.config.box_size)
    start = int(w.n_alive)
    for k in range(n):
        i = start + k
        if i >= w.config.n_vibrations_max:
            break
        w.s_pos[i] = rng.uniform(0, 1, 3) * box
        w.s_freq[i] = float(np.exp(rng.uniform(np.log(100), np.log(10000))))
        w.s_pol[i] = rng.random() < 0.5
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2*np.pi)
        sq = float(np.sqrt(max(1-z*z, 0)))
        sp = float(rng.uniform(5, 20))
        w.s_vel[i] = sp * np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        w.s_alive[i] = True
    w.n_alive = min(start + n, w.config.n_vibrations_max)


def fp(w, m):
    if not w.k_alive[m]:
        return "A?"
    return species_fingerprint(_ground_atom_decades(w, m))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, n, t = ((131,), 6, 100) if args.smoke else (SEEDS, N, T)
    print(f"BP-B7 start smoke={args.smoke} N={n} T={t}")
    ok_t, ok_c, surv = [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        labs = [0]*(n//2)+[1]*(n-n//2); rng.shuffle(labs)
        box = np.array([80.,80.,80.])
        for i, lab in enumerate(labs):
            w = World(cfg(seed))
            inject_ambient(w, rng, N_AMB)
            m = plant_mol(w, lab, rng.uniform(0,1,3)*box)
            dt = float(w.config.dt)
            for _ in range(t):
                tick(w, dt); w.t += dt
            f = fp(w, m)
            pred = 0 if f=="A33" else (1 if f=="A34" else None)
            ok_t.append(pred == lab)
            surv.append(bool(w.k_alive[m]) and f not in ("A?",""))
            w2 = World(cfg(seed))
            inject_ambient(w2, rng, N_AMB)
            m2 = plant_mol(w2, lab, rng.uniform(0,1,3)*box)
            st, en = int(w2.k_comp_offset[m2]), int(w2.k_comp_end[m2])
            kids = [int(w2.k_comp_indices[j]) for j in range(st, en)]
            if len(kids)>=2:
                o = 1-lab
                d0,d1 = ((3,3) if o==0 else (3,4))
                w2.k_freq[kids[0]]=fdec(d0); w2.k_freq[kids[1]]=fdec(d1,200)
            for _ in range(t):
                tick(w2, dt); w2.t += dt
            f2 = fp(w2, m2)
            p2 = 0 if f2=="A33" else (1 if f2=="A34" else None)
            ok_c.append(p2 == lab)
    aT=float(sum(ok_t)/len(ok_t)); aC=float(sum(ok_c)/len(ok_c)); sv=float(sum(surv)/len(surv))
    b1,b2,b5 = aT>=0.90, aC<=0.60, sv>=0.75
    verdict = "PASS" if (b1 and b2 and b5) else "NULL"
    result={"id":"BP-B7","bars":{
        "B1_T":{"value":aT,"threshold":0.90,"pass":b1},
        "B2_scramble":{"value":aC,"threshold":0.60,"pass":b2},
        "B5_surv":{"value":sv,"threshold":0.75,"pass":b5},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-B7"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-B7: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
