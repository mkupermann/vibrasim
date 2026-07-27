"""PRIM10-D0 lateral fire inhibition path competition. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1181, 1191), 10
N_WRITE, T_PROP = 12, 60
L1=np.array([12.,20.,25.]); M1=np.array([35.,20.,25.]); R1=np.array([58.,20.,25.])
L2=np.array([12.,30.,25.]); M2=np.array([35.,30.,25.]); R2=np.array([58.,30.,25.])

def cfg(seed, inhibit):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
        fire_inhibit_radius=25.0 if inhibit else 0.0, fire_inhibit_frac=0.85 if inhibit else 0.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,8)

def train(w,rng):
    link(w,rng,L1,M1,400.,1500.); link(w,rng,M1,R1,1500.,5000.)
    link(w,rng,L2,M2,800.,2500.); link(w,rng,M2,R2,2500.,7000.)

def peaks_both_L(w):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    p1=p2=0.
    for t in range(T_PROP):
        if t%8==0:
            for c in (L1,L2):
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=8:
                        w.k_charge[i]=thr+5.
        tick(w,dt)
        for i in range(w.k_count):
            if not w.k_alive[i] or int(w.k_level[i])<4: continue
            if float(np.linalg.norm(w.k_pos[i]-R1))<=8: p1=max(p1,float(w.k_latch[i]))
            if float(np.linalg.norm(w.k_pos[i]-R2))<=8: p2=max(p2,float(w.k_latch[i]))
    return p1,p2

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1181,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"PRIM10-D0 start smoke={args.smoke}")
    i1s,i2s,i3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*59047+ti*263)
            w=World(cfg(seed,True)); train(w,rng)
            a,b=peaks_both_L(w)
            exclusive=(a>=1.0 and b<=0.25) or (b>=1.0 and a<=0.25)
            i1s.append(exclusive); i3s.append(a>=1.0 or b>=1.0)
            w0=World(cfg(seed,False)); train(w0,rng)
            a0,b0=peaks_both_L(w0)
            i2s.append(a0>=1.0 and b0>=1.0)
    a1,a2,a3=map(float,(np.mean(i1s),np.mean(i2s),np.mean(i3s)))
    p1,p2,p3=a1>=0.80,a2>=0.80,a3>=0.90
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"PRIM10-D0","bars":{
        "I1_exclusive":{"value":a1,"threshold":0.80,"pass":p1},
        "I2_off_both":{"value":a2,"threshold":0.80,"pass":p2},
        "I3_on_atleast_one":{"value":a3,"threshold":0.90,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"PRIM10-D0"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM10-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
