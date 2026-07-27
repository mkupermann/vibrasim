"""BP-E127 dual 3-hop soft wipe-restore then multi-site hard re-cut path0. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (3461, 3471), 6
N_WRITE, T_PROP, N_RES = 10, 50, 8
L0=np.array([12.,18.,25.]); A0=np.array([28.,18.,25.]); B0=np.array([48.,18.,25.]); R0=np.array([65.,18.,25.])
I0=np.array([38.,18.,25.])
L1=np.array([12.,32.,25.]); A1=np.array([28.,32.,25.]); B1=np.array([48.,32.,25.]); R1=np.array([65.,32.,25.])
I1=np.array([38.,32.,25.])
# multi-site hop mids on path0 only
M_LA0=np.array([20.,18.,25.]); M_AB0=np.array([38.,18.,25.]); M_BR0=np.array([56.,18.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.5,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
        fire_weaken_bridge_radius=8.0, fire_weaken_bridge_frac=1.0,
        fire_kill_bridge_radius=8.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb,n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,5)

def train(w,rng):
    link(w,rng,L0,A0,400.,1000.); link(w,rng,A0,B0,1000.,2500.); link(w,rng,B0,R0,2500.,6000.)
    link(w,rng,L1,A1,400.,1100.); link(w,rng,A1,B1,1100.,2600.); link(w,rng,B1,R1,2600.,6100.)
    for pos in (I0, I1):
        for _ in range(N_WRITE):
            apply_ilw_port_event(w,pos,rng,seed_freq=9000.)
        idle(w,3)

def set_weaken_at(w, pos):
    if hasattr(w,"k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:]=0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=6.0:
            w.k_weaken_bridge_emitter[i]=1

def set_kill_at(w, pos):
    if hasattr(w,"k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:]=0
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=6.0:
            w.k_kill_bridge_emitter[i]=1

def disarm(w):
    if hasattr(w,"k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:]=0
    if hasattr(w,"k_kill_bridge_emitter"):
        w.k_kill_bridge_emitter[:]=0

def soft_cut_at(w, pos, n=30):
    set_weaken_at(w, pos)
    fire_phase(w, pos, n=n)
    disarm(w)

def hard_cut_at(w, pos, n=30):
    set_kill_at(w, pos)
    fire_phase(w, pos, n=n)
    disarm(w)

def restore_p0(w,rng):
    link(w,rng,L0,A0,400.,1000.,N_RES)
    link(w,rng,A0,B0,1000.,2500.,N_RES)
    link(w,rng,B0,R0,2500.,6000.,N_RES)

def restore_p1(w,rng):
    link(w,rng,L1,A1,400.,1100.,N_RES)
    link(w,rng,A1,B1,1100.,2600.,N_RES)
    link(w,rng,B1,R1,2600.,6100.,N_RES)

def fire_phase(w, target, n=T_PROP):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(n):
        if t%5==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-target))<=7:
                    w.k_charge[i]=thr+5.
        tick(w,dt)

def end_at(w, pos):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=7:
            m=max(m,float(w.k_latch[i]))
    return m

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((3461,),2) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E127 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*150217+ti*863)
            w=World(cfg(seed)); train(w,rng)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L0); on0=end_at(w,R0)>=1.0
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L1); on1=end_at(w,R1)>=1.0
            b1s.append(on0 and on1)
            soft_cut_at(w,I0); soft_cut_at(w,I1)
            restore_p0(w,rng); restore_p1(w,rng)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L0); r0=end_at(w,R0)>=1.0
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L1); r1=end_at(w,R1)>=1.0
            b2s.append(r0 and r1)
            # multi-site hard re-cut path0 hops
            for pos in (M_LA0, M_AB0, M_BR0):
                hard_cut_at(w, pos)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L0); off0=end_at(w,R0)<=0.25
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L1); stay1=end_at(w,R1)>=1.0
            b3s.append(off0 and stay1)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.80,a2>=0.80,a3>=0.80
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E127","bars":{
        "B1_both_initial":{"value":a1,"threshold":0.80,"pass":p1},
        "B2_both_after_wipe_restore":{"value":a2,"threshold":0.80,"pass":p2},
        "B3_multisite_hard_recut_p0":{"value":a3,"threshold":0.80,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E127"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E127: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
