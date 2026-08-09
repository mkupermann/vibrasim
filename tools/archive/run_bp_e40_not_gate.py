"""BP-E40 NOT gate: path L-M-R unless inhibitor I zeros R latch. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (1251, 1261), 10
N_WRITE, T_PROP = 12, 80
L=np.array([15.,25.,25.]); M=np.array([40.,25.,25.]); R=np.array([65.,25.,25.])
I=np.array([65.,40.,25.])  # near R for zero-latch radius

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
        fire_zero_latch_radius=20.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def train(w,rng):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,L,M,400.,1500.,rng)
    idle(w,8)
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,M,R,1500.,5000.,rng)
    idle(w,8)
    # seed inhibitor node near R (no need bridge)
    for _ in range(N_WRITE):
        apply_ilw_port_event(w,I,rng,seed_freq=9000.)
    idle(w,5)
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-I))<=8:
            w.k_zero_latch_emitter[i]=1

def end_R(w, fire_L=False, fire_I=False):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    for t in range(T_PROP):
        if t%8==0:
            if fire_L:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-L))<=8:
                        w.k_charge[i]=thr+5.
            if fire_I:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-I))<=8:
                        w.k_charge[i]=thr+5.
        tick(w,dt)
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-R))<=8:
            m=max(m,float(w.k_latch[i]))
    return m

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1251,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E40 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*61059+ti*271)
            w=World(cfg(seed)); train(w,rng)
            b1s.append(end_R(w,True,False)>=1.0)
            w2=World(cfg(seed)); train(w2,rng)
            b2s.append(end_R(w2,True,True)<=0.25)
            w3=World(cfg(seed)); train(w3,rng)
            b3s.append(end_R(w3,False,True)<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.90,a2>=0.90,a3>=0.90
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E40","bars":{
        "B1_L_on":{"value":a1,"threshold":0.90,"pass":p1},
        "B2_L_and_I_off":{"value":a2,"threshold":0.90,"pass":p2},
        "B3_I_only_off":{"value":a3,"threshold":0.90,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E40"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E40: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
