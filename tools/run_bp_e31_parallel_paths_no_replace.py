"""BP-E31 parallel two-chain path isolation. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (1001, 1011), 10
N_WRITE, T_PROP = 12, 60
# Chain1 / Chain2 positions
L1,M1,R1 = np.array([12.,20.,25.]), np.array([35.,20.,25.]), np.array([58.,20.,25.])
L2,M2,R2 = np.array([18.,35.,25.]), np.array([42.,35.,25.]), np.array([65.,35.,25.])

def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=50., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=False,
        ilw_enabled=True, ilw_radius=6., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
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
    idle(w,10)

def train_both(w,rng):
    link(w,rng,L1,M1,400.,1500.); link(w,rng,M1,R1,1500.,5000.)
    link(w,rng,L2,M2,800.,2500.); link(w,rng,M2,R2,2500.,7000.)

def n_bridges(w):
    return sum(1 for b in range(w.b_count) if w.b_alive[b])

def peak_near(w, center, rad=8.):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    # caller sets fires; we only measure after a prop window if needed
    m=0.
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        if float(np.linalg.norm(w.k_pos[i]-center))<=rad:
            m=max(m, float(w.k_latch[i]))
    return m

def fire_and_peak(w, fire_centers, measure_R1=True, measure_R2=True):
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    w.k_charge[:w.k_count]=0.; w.k_latch[:w.k_count]=0.
    p1=p2=0.
    for t in range(T_PROP):
        if t%8==0:
            for c in fire_centers:
                for i in range(w.k_count):
                    if not w.k_alive[i] or int(w.k_level[i])<4: continue
                    if float(np.linalg.norm(w.k_pos[i]-c))<=8.:
                        w.k_charge[i]=thr+5.
        tick(w,dt)
        if measure_R1: p1=max(p1, peak_near(w,R1))
        if measure_R2: p2=max(p2, peak_near(w,R2))
    return p1,p2

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((1001,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E31 start smoke={args.smoke}")
    b1s,b2s,b3s,b4s=[],[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*50017+ti*211)
            w=World(make_cfg(seed)); train_both(w,rng)
            b4s.append(n_bridges(w)>=4)
            p1,p2=fire_and_peak(w,[L1])
            b1s.append(p1>=1.0); b2s.append(p2<=0.25)
            w2=World(make_cfg(seed)); train_both(w2,rng)
            q1,q2=fire_and_peak(w2,[L1,L2])
            b3s.append(q1>=1.0 and q2>=1.0)
    a1,a2,a3,a4=map(float,(np.mean(b1s),np.mean(b2s),np.mean(b3s),np.mean(b4s)))
    p1,p2,p3,p4=a1>=0.85,a2>=0.85,a3>=0.80,a4>=0.90
    verdict="PASS" if all([p1,p2,p3,p4]) else "NULL"
    result={"id":"BP-E31","bars":{
        "B1_R1_on":{"value":a1,"threshold":0.85,"pass":p1},
        "B2_R2_off":{"value":a2,"threshold":0.85,"pass":p2},
        "B3_both_on":{"value":a3,"threshold":0.80,"pass":p3},
        "B4_bridges":{"value":a4,"threshold":0.90,"pass":p4},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E31"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E31: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
