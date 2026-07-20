"""BP-E42 XOR: OR path + coincidence Mand kills bridges. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1311, 1321), 10
N_WRITE, T_PROP = 12, 60
L1=np.array([12.,18.,25.]); L2=np.array([12.,32.,25.])
Mor=np.array([35.,25.,25.]); Mand=np.array([38.,38.,25.]); R=np.array([62.,25.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=55., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
        coincidence_and_enabled=True, fire_kill_bridge_radius=30.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def n_br(w):
    return sum(1 for b in range(w.b_count) if w.b_alive[b])

def train(w,rng):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,L1,Mor,400.,1500.,rng)
        apply_ilw_pair_write(w,L2,Mor,800.,1500.,rng)
    idle(w,6)
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,Mor,R,1500.,5000.,rng)
    idle(w,6)
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,L1,Mand,400.,2200.,rng)
        apply_ilw_pair_write(w,L2,Mand,800.,2200.,rng)
    idle(w,6)
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        if float(np.linalg.norm(w.k_pos[i]-Mand))<=8:
            w.k_coincidence_gate[i]=1
            w.k_kill_bridge_emitter[i]=1

def fire_phase(w, targets, n=T_PROP):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(n):
        if t%6==0:
            for c in targets:
                for i in range(w.k_count):
                    if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=8:
                        w.k_charge[i]=thr+5.
        tick(w,dt)

def end_R(w):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-R))<=8:
            m=max(m,float(w.k_latch[i]))
    return m

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1311,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E42 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*64071+ti*283)
            w=World(cfg(seed)); train(w,rng)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,[L1]); b1s.append(end_R(w)>=1.0)
            w2=World(cfg(seed)); train(w2,rng)
            w2.k_charge[:]=0; w2.k_latch[:]=0
            fire_phase(w2,[L2]); b2s.append(end_R(w2)>=1.0)
            w3=World(cfg(seed)); train(w3,rng)
            n0=n_br(w3)
            w3.k_charge[:]=0; w3.k_latch[:]=0
            fire_phase(w3,[L1,L2])  # both → Mand cut
            n1=n_br(w3)
            w3.k_charge[:]=0; w3.k_latch[:]=0
            fire_phase(w3,[L1])
            b3s.append(n1<n0 and end_R(w3)<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.85,a2>=0.85,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E42","bars":{
        "B1_L1":{"value":a1,"threshold":0.85,"pass":p1},
        "B2_L2":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_both_cut":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E42"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E42: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
