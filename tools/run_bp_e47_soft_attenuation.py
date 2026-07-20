"""BP-E47 graded soft weaken: one half-cut keeps path; many silence. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (1461, 1471), 8
N_WRITE, T_PROP, PROP_MIN = 12, 50, 0.5
L=np.array([15.,25.,25.]); M=np.array([40.,25.,25.]); R=np.array([65.,25.,25.])
I=np.array([40.,40.,25.])

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=PROP_MIN, charge_latch_enabled=True, charge_latch_tau=0.,
        fire_weaken_bridge_radius=18.0, fire_weaken_bridge_frac=0.5,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def train(w,rng):
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,L,M,400.,1500.,rng)
    idle(w,6)
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,M,R,1500.,5000.,rng)
    idle(w,6)
    for _ in range(N_WRITE):
        apply_ilw_port_event(w,I,rng,seed_freq=9000.)
    idle(w,4)
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-I))<=8:
            w.k_weaken_bridge_emitter[i]=1

def fire_phase(w, target, n=T_PROP):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(n):
        if t%6==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-target))<=8:
                    w.k_charge[i]=thr+5.
        tick(w,dt)

def end_R(w):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-R))<=8:
            m=max(m,float(w.k_latch[i]))
    return m

def max_br_str(w):
    m=0.
    for b in range(w.b_count):
        if w.b_alive[b]:
            m=max(m,float(w.b_strength[b]))
    return m

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1461,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E47 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*70091+ti*331)
            w=World(cfg(seed)); train(w,rng)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L); b1s.append(end_R(w)>=1.0)
            # one half-weaken
            fire_phase(w,I,n=20)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L); b2s.append(end_R(w)>=1.0)
            # many weakens until silent or 10 rounds
            ok3=False
            for _ in range(12):
                fire_phase(w,I,n=15)
                if max_br_str(w)<PROP_MIN:
                    break
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L)
            b3s.append(end_R(w)<=0.25)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.90,a2>=0.85,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E47","bars":{
        "B1_full":{"value":a1,"threshold":0.90,"pass":p1},
        "B2_half_still_on":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_many_off":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E47"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E47: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
