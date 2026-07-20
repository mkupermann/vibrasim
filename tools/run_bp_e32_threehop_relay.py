"""BP-E32 three-hop L-A-B-R charge relay. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1021, 1031), 8
N_WRITE, T_PROP = 12, 80
PL=np.array([12.,25.,25.]); PA=np.array([30.,25.,25.])
PB=np.array([50.,25.,25.]); PR=np.array([68.,25.,25.])

def cfg(seed):
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

def link(w,rng,a,b,fa,fb):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,8)

def train(w,rng, full=True):
    link(w,rng,PL,PA,400.,1200.)
    if full: link(w,rng,PA,PB,1200.,3000.)
    link(w,rng,PB,PR,3000.,7000.)

def n_br(w):
    return sum(1 for b in range(w.b_count) if w.b_alive[b])

def peak_R(w):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    peak=0.
    for t in range(T_PROP):
        if t%6==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])<20:
                    w.k_charge[i]=thr+5.
        tick(w,dt)
        for i in range(w.k_count):
            if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])>60:
                peak=max(peak, float(w.k_latch[i]))
    return peak

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1021,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E32 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*51019+ti*223)
            w=World(cfg(seed)); train(w,rng,True)
            b3s.append(n_br(w)>=3); b1s.append(peak_R(w)>=1.0)
            w0=World(cfg(seed)); train(w0,rng,False)
            b2s.append(peak_R(w0)<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.90,a2>=0.90,a3>=0.90
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E32","bars":{
        "B1_threehop":{"value":a1,"threshold":0.90,"pass":p1},
        "B2_broken":{"value":a2,"threshold":0.90,"pass":p2},
        "B3_bridges":{"value":a3,"threshold":0.90,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E32"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E32: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
