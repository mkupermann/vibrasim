"""PRIM9-D0 / coincidence AND via elevated mid theta. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1161, 1171), 10
N_WRITE, T_PROP = 12, 80
L1=np.array([12.,18.,25.]); L2=np.array([12.,32.,25.])
M=np.array([40.,25.,25.]); R=np.array([68.,25.,25.])
MID_THETA = 3.5

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
        coincidence_and_enabled=True,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,8)

def train(w,rng):
    link(w,rng,L1,M,400.,1500.); link(w,rng,L2,M,800.,1500.); link(w,rng,M,R,1500.,5000.)
    # coincidence gate only on mid (AND node)
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-M))<=8:
            w.k_coincidence_gate[i] = 1

def peak_R(w, fires):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    # re-assert mid theta after reset not needed
    peak=0.
    for t in range(T_PROP):
        if t%8==0:
            for c in fires:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=8:
                        w.k_charge[i]=thr+5.
        tick(w,dt)
        for i in range(w.k_count):
            if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-R))<=8:
                peak=max(peak,float(w.k_latch[i]))
    return peak

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1161,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"PRIM9-D0 start smoke={args.smoke}")
    a1s,a2s,a3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*58043+ti*257)
            w=World(cfg(seed)); train(w,rng)
            a1s.append(peak_R(w,[L1])<=0.25)
            w2=World(cfg(seed)); train(w2,rng)
            a2s.append(peak_R(w2,[L2])<=0.25)
            w3=World(cfg(seed)); train(w3,rng)
            a3s.append(peak_R(w3,[L1,L2])>=1.0)
    a1,a2,a3=map(float,(np.mean(a1s),np.mean(a2s),np.mean(a3s)))
    p1,p2,p3=a1>=0.85,a2>=0.85,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"PRIM9-D0","bars":{
        "A1_L1_off":{"value":a1,"threshold":0.85,"pass":p1},
        "A2_L2_off":{"value":a2,"threshold":0.85,"pass":p2},
        "A3_both_on":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"PRIM9-D0"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM9-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
