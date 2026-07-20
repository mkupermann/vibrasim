"""BP-E92 soft DEMUX dual-cut then full restore all three arms. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, apply_ilw_port_event, tick
from world.state import World

SEEDS, TRIALS = (2681, 2691), 6
N_WRITE, T_PROP, N_RES = 10, 45, 6
L = np.array([12., 25., 25.])
ARMS = []
for y in (12., 25., 38.):
    ARMS.append({
        "M": np.array([35., y, 25.]),
        "R": np.array([58., y, 25.]),
        "I": np.array([35., y + (3.5 if y < 30 else -3.5), 25.]),
        "fM": 1500. + y * 10, "fR": 5000. + y * 5,
    })
fL = 400.

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=4.5, ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_pair_link_enabled=True, ilw_pair_link_delta=1., ilw_pair_replace_enabled=False,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0.5, charge_latch_enabled=True, charge_latch_tau=0.,
        fire_weaken_bridge_radius=10.0, fire_weaken_bridge_frac=1.0,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def link(w,rng,a,b,fa,fb,n=N_WRITE):
    for _ in range(n):
        apply_ilw_pair_write(w,a,b,fa,fb,rng)
    idle(w,4)

def train_all(w,rng):
    for a in ARMS:
        link(w,rng,L,a["M"],fL,a["fM"])
        link(w,rng,a["M"],a["R"],a["fM"],a["fR"])
        for _ in range(N_WRITE):
            apply_ilw_port_event(w,a["I"],rng,seed_freq=9000.)
        idle(w,3)

def set_emitter(w, k):
    if hasattr(w,"k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:]=0
    pos=ARMS[k]["I"]
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-pos))<=5.5:
            w.k_weaken_bridge_emitter[i]=1

def disarm(w):
    if hasattr(w,"k_weaken_bridge_emitter"):
        w.k_weaken_bridge_emitter[:]=0

def restore(w,rng,k):
    a=ARMS[k]
    link(w,rng,L,a["M"],fL,a["fM"],N_RES)
    link(w,rng,a["M"],a["R"],a["fM"],a["fR"],N_RES)

def fire_phase(w, target, n=T_PROP):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    for t in range(n):
        if t%6==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-target))<=6:
                    w.k_charge[i]=thr+5.
        tick(w,dt)

def end_near(w,c):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(np.linalg.norm(w.k_pos[i]-c))<=6:
            m=max(m,float(w.k_latch[i]))
    return m

def soft_cut(w, k):
    set_emitter(w,k)
    fire_phase(w,ARMS[k]["I"], n=28)
    disarm(w)

def dual_cut_all(w):
    for k in range(3):
        soft_cut(w,k)

def all_off(w):
    w.k_charge[:]=0; w.k_latch[:]=0
    fire_phase(w,L)
    return all(end_near(w,ARMS[j]["R"])<=0.25 for j in range(3))

def all_on(w):
    w.k_charge[:]=0; w.k_latch[:]=0
    fire_phase(w,L)
    return all(end_near(w,ARMS[j]["R"])>=1.0 for j in range(3))

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((2681,),2) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E92 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*115151+ti*617)
            w=World(cfg(seed)); train_all(w,rng)
            dual_cut_all(w)
            b1s.append(all_off(w))
            for k in range(3):
                restore(w,rng,k)
            b2s.append(all_on(w))
            soft_cut(w,0)
            w.k_charge[:]=0; w.k_latch[:]=0
            fire_phase(w,L)
            b3s.append(end_near(w,ARMS[0]["R"])<=0.25 and end_near(w,ARMS[1]["R"])>=1.0 and end_near(w,ARMS[2]["R"])>=1.0)
    a1,a2,a3=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s)))
    p1,p2,p3=a1>=0.80,a2>=0.80,a3>=0.75
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E92","bars":{
        "B1_all_off":{"value":a1,"threshold":0.80,"pass":p1},
        "B2_all_on":{"value":a2,"threshold":0.80,"pass":p2},
        "B3_cut0_after":{"value":a3,"threshold":0.75,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E92"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E92: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
