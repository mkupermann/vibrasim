"""BP-E46 multi-trial path switch soft cut/restore. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (1441, 1451), 8
N_WRITE, T_PROP, N_RES = 12, 50, 6
L1=np.array([12.,18.,25.]); M1=np.array([35.,18.,25.]); R1=np.array([58.,18.,25.])
L2=np.array([12.,38.,25.]); M2=np.array([35.,38.,25.]); R2=np.array([58.,38.,25.])
I1=np.array([35.,22.,25.]); I2=np.array([35.,34.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=5., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0.5, charge_latch_enabled=True, charge_latch_tau=0.,
        fire_weaken_bridge_radius=12.0, fire_weaken_bridge_frac=1.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb,n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,5)

def train_both(w,rng):
    link(w,rng,L1,M1,400.,1500.); link(w,rng,M1,R1,1500.,5000.)
    link(w,rng,L2,M2,800.,2500.); link(w,rng,M2,R2,2500.,7000.)

def seed_I(w,rng,pos,tag=True):
    for _ in range(N_WRITE):
        apply_ilw_port_event(w,pos,rng,seed_freq=9000.)
    idle(w,3)
    if tag:
        for i in range(w.k_count):
            if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=6:
                w.k_weaken_bridge_emitter[i]=1

def clear_emitters(w):
    if hasattr(w,"k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:]=0

def restore(w,rng, path=1):
    if path==1:
        link(w,rng,L1,M1,400.,1500.,N_RES); link(w,rng,M1,R1,1500.,5000.,N_RES)
    else:
        link(w,rng,L2,M2,800.,2500.,N_RES); link(w,rng,M2,R2,2500.,7000.,N_RES)

def fire_phase(w, target, n=T_PROP):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(n):
        if t%6==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-target))<=7:
                    w.k_charge[i]=thr+5.
        tick(w,dt)

def end_near(w,c):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=7:
            m=max(m,float(w.k_latch[i]))
    return m

def probe(w, L, R):
    w.k_charge[:]=0; w.k_latch[:]=0
    fire_phase(w,L)
    return end_near(w,R)

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1441,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E46 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*69089+ti*317)
            w=World(cfg(seed)); train_both(w,rng)
            seed_I(w,rng,I1,True); seed_I(w,rng,I2,False)  # only I1 emitter for now
            # tag both emitters after seeding
            clear_emitters(w)
            for i in range(w.k_count):
                if not w.k_alive[i] or int(w.k_level[i])<4: continue
                if float(np.linalg.norm(w.k_pos[i]-I1))<=6: w.k_weaken_bridge_emitter[i]=1
            # B1 both on
            b1s.append(probe(w,L1,R1)>=1.0 and probe(w,L2,R2)>=1.0)
            # cut path1
            fire_phase(w,I1)
            b2s.append(probe(w,L1,R1)<=0.25 and probe(w,L2,R2)>=1.0)
            # restore path1, cut path2
            restore(w,rng,1)
            clear_emitters(w)
            for i in range(w.k_count):
                if not w.k_alive[i] or int(w.k_level[i])<4: continue
                if float(np.linalg.norm(w.k_pos[i]-I2))<=6: w.k_weaken_bridge_emitter[i]=1
            fire_phase(w,I2)
            b3s.append(probe(w,L1,R1)>=1.0 and probe(w,L2,R2)<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.85,a2>=0.85,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E46","bars":{
        "B1_both":{"value":a1,"threshold":0.85,"pass":p1},
        "B2_cut1":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_switch":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E46"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E46: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
