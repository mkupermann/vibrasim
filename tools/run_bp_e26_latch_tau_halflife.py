"""BP-E26 latch half-life under charge_latch_tau. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (821, 831), 8
N_WRITE, T_PROP, T_END, MID = 12, 40, 200, 40.0
PORT_L, PORT_R = np.array([20.,25.,25.]), np.array([60.,25.,25.])

def make_cfg(seed, tau):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_pair_link_enabled=True,
        ilw_pair_link_delta=1., neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0,
        bridge_charge_prop_rate=2., bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=tau,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def max_R_latch(w):
    m=0.
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])>=MID:
            m=max(m, float(w.k_latch[i]))
    return m

def run_arm(seed, ti, tau):
    w = World(make_cfg(seed, tau))
    rng = np.random.default_rng(seed*44093+ti*181)
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w, PORT_L, PORT_R, 500., 5000., rng)
    idle(w, 20)
    thr=float(w.config.theta_fire); dt=float(w.config.dt)
    peak=0.
    for t in range(T_PROP):
        if t%10==0:
            for i in range(w.k_count):
                if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])<MID:
                    w.k_charge[i]=thr+5.
        tick(w, dt)
        peak=max(peak, max_R_latch(w))
    idle(w, T_END)
    end = max_R_latch(w)
    return peak, end

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((821,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E26 start smoke={args.smoke}")
    b1s,b2s,b3s=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            p2,e2 = run_arm(seed, ti, 2.0)
            p0,e0 = run_arm(seed, ti, 0.0)
            b1s.append(p2>0 and e2<=0.50*p2)
            b2s.append(p0>0 and e0>=0.90*p0)
            b3s.append(p2>=1.0 and p0>=1.0)
    a1,a2,a3=float(np.mean(b1s)),float(np.mean(b2s)),float(np.mean(b3s))
    p1,p2,p3=a1>=0.90,a2>=0.90,a3>=0.90
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"BP-E26","bars":{
        "B1_tau2_decay":{"value":a1,"threshold":0.90,"pass":p1},
        "B2_tau0_hold":{"value":a2,"threshold":0.90,"pass":p2},
        "B3_peaks":{"value":a3,"threshold":0.90,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E26"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E26: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
