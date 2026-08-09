"""BP-E37 midplane-separated dual two-hop chains. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1121, 1131), 8
N_WRITE, T_PROP, MID = 12, 60, 40.0
# left chain x<40, right x>40
LL=np.array([15.,25.,25.]); LM=np.array([25.,25.,25.]); LR=np.array([35.,25.,25.])
RL=np.array([45.,25.,25.]); RM=np.array([55.,25.,25.]); RR=np.array([65.,25.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=True, midplane_wall_x=MID,
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

def train(w,rng):
    link(w,rng,LL,LM,400.,1200.); link(w,rng,LM,LR,1200.,2000.)
    link(w,rng,RL,RM,800.,2500.); link(w,rng,RM,RR,2500.,5000.)

def peak_near(w,c,rad=7.):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=rad:
            m=max(m,float(w.k_latch[i]))
    return m

def fire_and_peaks(w, fire_c):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    pl=pr=0.
    for t in range(T_PROP):
        if t%8==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-fire_c))<=7:
                    w.k_charge[i]=thr+5.
        tick(w,dt)
        pl=max(pl,peak_near(w,LR)); pr=max(pr,peak_near(w,RR))
    return pl,pr

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1121,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E37 start smoke={args.smoke}")
    b1s,b2s,b3s,b4s=[],[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*56037+ti*241)
            w=World(cfg(seed)); train(w,rng)
            pl,pr=fire_and_peaks(w,LL)
            b1s.append(pl>=1.0); b2s.append(pr<=0.25)
            w2=World(cfg(seed)); train(w2,rng)
            pl2,pr2=fire_and_peaks(w2,RL)
            b3s.append(pr2>=1.0); b4s.append(pl2<=0.25)
    a1,a2,a3,a4=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s),np.mean(b4s)))
    p1,p2,p3,p4=a1>=0.85,a2>=0.85,a3>=0.85,a4>=0.85
    verdict="PASS" if all([p1,p2,p3,p4]) else "NULL"
    result={"id":"BP-E37","bars":{
        "B1_left_on":{"value":a1,"threshold":0.85,"pass":p1},
        "B2_left_no_right":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_right_on":{"value":a3,"threshold":0.85,"pass":p3},
        "B4_right_no_left":{"value":a4,"threshold":0.85,"pass":p4},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E37"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E37: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
