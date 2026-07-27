"""BP-E29 two-hop L→M→R charge relay. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (961, 971), 10
N_WRITE, T_PROP, MID = 12, 60, 40.0
PL = np.array([15., 25., 25.]); PM = np.array([40., 25., 25.]); PR = np.array([65., 25., 25.])

def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def n_bridges(w):
    return sum(1 for b in range(w.b_count) if w.b_alive[b])

def max_R_latch(w):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])>55:
            m=max(m, float(w.k_latch[i]))
    return m

def peak_R_after_fire_L(w):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:w.k_count]=0.; w.k_latch[:w.k_count]=0.
    peak=0.
    for t in range(T_PROP):
        if t%8==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])<25:
                    w.k_charge[i]=thr+5.
        tick(w,dt)
        peak=max(peak, max_R_latch(w))
    return peak

def train_twohop(w,rng, full=True):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w, PL, PM, 500., 2000., rng)
    idle(w,15)
    if full:
        for _ in range(N_WRITE):
            apply_ilw_pair_write(w, PM, PR, 2000., 5000., rng)
        idle(w,15)

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((961,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E29 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*48011+ti*199)
            w=World(make_cfg(seed)); train_twohop(w,rng,True)
            b3s.append(n_bridges(w)>=2)
            b1s.append(peak_R_after_fire_L(w)>=1.0)
            w0=World(make_cfg(seed)); train_twohop(w0,rng,False)
            b2s.append(peak_R_after_fire_L(w0)<=0.25)
    a1,a2,a3=float(np.mean(b1s)),float(np.mean(b2s)),float(np.mean(b3s))
    p1,p2,p3=a1>=0.90,a2>=0.90,a3>=0.90
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E29","bars":{
        "B1_twohop_R":{"value":a1,"threshold":0.90,"pass":p1},
        "B2_no_MR":{"value":a2,"threshold":0.90,"pass":p2},
        "B3_bridges":{"value":a3,"threshold":0.90,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E29"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E29: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
