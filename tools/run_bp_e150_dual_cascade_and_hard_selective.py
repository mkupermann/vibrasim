"""BP-E150 dual cascade AND paths + hard selective silence path0. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (4001, 4011), 6
N_WRITE, T_PROP, N_RES = 12, 90, 8
# path0 y=12, path1 y=36 — sep=24 > kill r=8
L0a=np.array([12.,8.,25.]); L0b=np.array([12.,16.,25.])
M0=np.array([32.,12.,25.]); A0=np.array([50.,12.,25.]); R0=np.array([68.,12.,25.])
I0a=np.array([12.,8.,30.]); I0b=np.array([12.,16.,30.])
L1a=np.array([12.,32.,25.]); L1b=np.array([12.,40.,25.])
M1=np.array([32.,36.,25.]); A1=np.array([50.,36.,25.]); R1=np.array([68.,36.,25.])
I1a=np.array([12.,32.,30.]); I1b=np.array([12.,40.,30.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.5,
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
    idle(w,6)

def arm_gate_at(w, pos):
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=7:
            w.k_coincidence_gate[i]=1

def train(w,rng):
    link(w,rng,L0a,M0,400.,1200.); link(w,rng,L0b,M0,800.,1200.)
    link(w,rng,M0,A0,1200.,3000.); link(w,rng,A0,R0,3000.,6000.)
    link(w,rng,L1a,M1,400.,1400.); link(w,rng,L1b,M1,800.,1400.)
    link(w,rng,M1,A1,1400.,3200.); link(w,rng,A1,R1,3200.,6200.)
    for pos in (I0a,I0b,I1a,I1b):
        for _ in range(N_WRITE):
            apply_ilw_port_event(w,pos,rng,seed_freq=9000.)
        idle(w,2)
    arm_gate_at(w,M0); arm_gate_at(w,M1)

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

def restore_p0(w,rng):
    link(w,rng,L0a,M0,400.,1200.,N_RES); link(w,rng,L0b,M0,800.,1200.,N_RES)
    link(w,rng,M0,A0,1200.,3000.,N_RES); link(w,rng,A0,R0,3000.,6000.,N_RES)
    arm_gate_at(w,M0)

def peak_at(w, fires, R):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:]=0; w.k_latch[:]=0
    peak=0.
    for t in range(T_PROP):
        if t%8==0:
            for c in fires:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=7:
                        w.k_charge[i]=thr+5.
        tick(w,dt)
        for i in range(w.k_count):
            if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-R))<=7:
                peak=max(peak,float(w.k_latch[i]))
    return peak

def path0_dual_on(w):
    return peak_at(w,[L0a,L0b],R0)>=1.0 and peak_at(w,[L0a],R0)<=0.25

def path1_dual_on(w):
    return peak_at(w,[L1a,L1b],R1)>=1.0 and peak_at(w,[L1a],R1)<=0.25

def path0_off(w):
    return peak_at(w,[L0a,L0b],R0)<=0.25

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((4001,),2) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E150 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*173217+ti*1031)
            w=World(cfg(seed)); train(w,rng)
            b1s.append(path0_dual_on(w) and path1_dual_on(w))
            hard_cut_at(w,I0a); hard_cut_at(w,I0b)
            b2s.append(path0_off(w) and path1_dual_on(w))
            restore_p0(w,rng)
            b3s.append(path0_dual_on(w) and path1_dual_on(w))
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.80,a2>=0.80,a3>=0.80
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E150","bars":{
        "B1_both_dual_on":{"value":a1,"threshold":0.80,"pass":p1},
        "B2_p0_off_p1_on":{"value":a2,"threshold":0.80,"pass":p2},
        "B3_restore_p0_both_on":{"value":a3,"threshold":0.80,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E150"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E150: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
