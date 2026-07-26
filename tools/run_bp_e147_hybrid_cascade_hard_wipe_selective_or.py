"""BP-E147 hybrid cascade hard dual wipe selective OR restore. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (3941, 3951), 6
N_WRITE, T_PROP, N_RES = 12, 90, 8
L1=np.array([12.,18.,25.]); L2=np.array([12.,32.,25.])
L3=np.array([12.,25.,42.])
M=np.array([32.,25.,25.]); A=np.array([50.,25.,25.]); R=np.array([68.,25.,25.])
I1=np.array([12.,18.,30.]); I3=np.array([12.,25.,47.])

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
        fire_kill_bridge_radius=8.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb,n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,8)

def arm_gate(w):
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-M))<=8:
            w.k_coincidence_gate[i]=1

def train(w,rng):
    link(w,rng,L1,M,400.,1500.); link(w,rng,L2,M,800.,1500.)
    link(w,rng,M,A,1500.,3000.); link(w,rng,A,R,3000.,6000.)
    link(w,rng,L3,R,600.,6000.)
    for pos in (I1,I3):
        for _ in range(N_WRITE):
            apply_ilw_port_event(w,pos,rng,seed_freq=9000.)
        idle(w,3)
    arm_gate(w)

def set_kill_at(w, pos):
    if hasattr(w,"k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:]=0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=5.5:
            w.k_kill_bridge_emitter[i]=1

def disarm(w):
    if hasattr(w,"k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:]=0

def hard_cut_at(w, pos):
    set_kill_at(w, pos)
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(30):
        if t%5==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=6:
                    w.k_charge[i]=thr+5.
        tick(w,dt)
    disarm(w)

def restore_or(w,rng):
    link(w,rng,L3,R,600.,6000.,N_RES)

def peak_R(w, fires):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
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
    seeds,trials=((3941,),2) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E147 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*170217+ti*1013)
            w=World(cfg(seed)); train(w,rng)
            hard_cut_at(w,I1); hard_cut_at(w,I3)
            both_off = peak_R(w,[L1,L2])<=0.25 and peak_R(w,[L3])<=0.25
            b1s.append(both_off)
            restore_or(w,rng)
            b2s.append(peak_R(w,[L3])>=1.0)
            b3s.append(peak_R(w,[L1,L2])<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.80,a2>=0.80,a3>=0.80
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E147","bars":{
        "B1_both_silent":{"value":a1,"threshold":0.80,"pass":p1},
        "B2_or_restored":{"value":a2,"threshold":0.80,"pass":p2},
        "B3_cascade_and_still_off":{"value":a3,"threshold":0.80,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E147"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E147: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
