"""BP-E3 last-written ILW side. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick, apply_ilw_port_event
from world.state import World

SEEDS, TRIALS = (231, 241), 10
N_W, T_IDLE, MID = 15, 150, 40.0
PL, PR = np.array([20.,25.,25.]), np.array([60.,25.,25.])


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.),
        n_vibrations_max=2048, n_nodes_max=2048, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8.0, ilw_delta_strength=0.5,
    )


def strengths(w):
    sL=sR=0.0; nL=nR=0
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        s=float(w.k_strength[i])
        if float(w.k_pos[i,0])<MID: sL+=s; nL+=1
        else: sR+=s; nR+=1
    return sL,sR,nL,nR


def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n):
        tick(w,dt); w.t+=dt


def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((231,),4) if args.smoke else (SEEDS,TRIALS)
    print(f"BP-E3 start smoke={args.smoke} seeds={seeds} trials={trials}")
    ok, imb, pop = [], [], []
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*9001+ti*17)
            last=int(rng.integers(0,2))  # 0=L last, 1=R last
            w=World(cfg(seed))
            # first the other side, then last
            first=1-last
            seq=[(PL,500.) if first==0 else (PR,5000.), (PL,500.) if last==0 else (PR,5000.)]
            for port,freq in seq:
                for _ in range(N_W):
                    apply_ilw_port_event(w, port, rng, seed_freq=freq)
            idle(w, T_IDLE)
            sL,sR,nL,nR=strengths(w)
            pred=0 if sL>sR else 1
            ok.append(pred==last)
            pop.append(nL>=1 and nR>=1)
            # equal control
            w2=World(cfg(seed))
            for _ in range(N_W):
                apply_ilw_port_event(w2, PL, rng, seed_freq=500.)
                apply_ilw_port_event(w2, PR, rng, seed_freq=5000.)
            idle(w2, T_IDLE)
            a,b,_,_=strengths(w2)
            imb.append(abs(a-b)/(a+b+1e-9))
    a1=float(np.mean(ok)); a2=float(np.mean(imb)); a3=float(np.mean(pop))
    b1,b2,b3=a1>=0.85, a2<=0.25, a3>=0.90
    verdict="PASS" if all([b1,b2,b3]) else "NULL"
    result={"id":"BP-E3","bars":{
        "B1_last":{"value":a1,"threshold":0.85,"pass":b1},
        "B2_eq_imb":{"value":a2,"threshold":0.25,"pass":b2},
        "B3_pop":{"value":a3,"threshold":0.90,"pass":b3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-E3"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E3: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
