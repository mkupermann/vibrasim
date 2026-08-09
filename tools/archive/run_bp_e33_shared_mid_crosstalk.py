"""BP-E33 shared mid crosstalk vs separate mids. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1041, 1051), 8
N_WRITE, T_PROP = 12, 60
L1=np.array([12.,20.,25.]); M=np.array([40.,25.,25.]); R1=np.array([68.,20.,25.])
L2=np.array([12.,35.,25.]); R2=np.array([68.,35.,25.])
M1=np.array([40.,20.,25.]); M2=np.array([40.,35.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,8)

def peak_near(w,c,rad=8.):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=rad:
            m=max(m,float(w.k_latch[i]))
    return m

def fire_L1_peaks(w):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    p1=p2=0.
    for t in range(T_PROP):
        if t%8==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-L1))<=8:
                    w.k_charge[i]=thr+5.
        tick(w,dt)
        p1=max(p1,peak_near(w,R1)); p2=max(p2,peak_near(w,R2))
    return p1,p2

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1041,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E33 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*52021+ti*227)
            # shared mid
            w=World(cfg(seed))
            link(w,rng,L1,M,400.,1500.); link(w,rng,M,R1,1500.,5000.)
            link(w,rng,L2,M,800.,1500.); link(w,rng,M,R2,1500.,7000.)
            p1,p2=fire_L1_peaks(w)
            b1s.append(p1>=1.0); b2s.append(p2>=1.0)
            # separate mids
            w2=World(cfg(seed))
            link(w2,rng,L1,M1,400.,1500.); link(w2,rng,M1,R1,1500.,5000.)
            link(w2,rng,L2,M2,800.,2500.); link(w2,rng,M2,R2,2500.,7000.)
            _,p2s=fire_L1_peaks(w2)
            b3s.append(p2s<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.85,a2>=0.85,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E33","bars":{
        "B1_shared_R1":{"value":a1,"threshold":0.85,"pass":p1},
        "B2_shared_R2_x":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_sep_R2_off":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E33"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E33: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
