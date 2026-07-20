"""BP-C8 sequential vs simultaneous free dual-band talent. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T_HALF, SEEDS, TRIALS = 400, 500, (931, 941, 951), 3
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=8192, n_nodes_max=4096,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25., midplane_wall_enabled=True, midplane_wall_x=MID,
    )

def inject(w, rng, birth, n, x0, x1, f0, f1, tag):
    dead = np.where(~w.s_alive)[0]
    slots = dead[:n] if len(dead)>=n else np.arange(int(w.n_alive), min(int(w.n_alive)+n, w.config.n_vibrations_max))
    for k,i in enumerate(slots):
        i=int(i)
        w.s_pos[i]=[rng.uniform(x0,x1), rng.uniform(8,42), rng.uniform(8,42)]
        w.s_freq[i]=float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i]=k%2==0
        z,phi=rng.uniform(-1,1), rng.uniform(0,2*np.pi)
        sq=float(np.sqrt(max(1-z*z,0))); sp=float(rng.uniform(5,25))
        w.s_vel[i]=sp*np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        w.s_alive[i]=True
        if birth is not None: birth[i]=tag
    w.n_alive=int(w.s_alive.sum())

def sides_md(w):
    L,R=[],[]
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        d=int(math.floor(math.log10(max(float(w.k_freq[i]),1.))))
        (L if float(w.k_pos[i,0])<MID else R).append(d)
    mL=float(np.mean(L)) if L else None; mR=float(np.mean(R)) if R else None
    pop=len(L)>=1 and len(R)>=1
    ok=pop and mL is not None and mR is not None and mL<mR
    return pop, ok

def evolve(w, birth, ticks):
    dt=float(w.config.dt); wrong=free=0
    for _ in range(ticks):
        for i in np.where(w.s_alive)[0]:
            tag=int(birth[i])
            if tag==0: continue
            free+=1; x=float(w.s_pos[i,0])
            if tag==1 and x>=MID: wrong+=1
            if tag==2 and x<MID: wrong+=1
        tick(w,dt); w.t+=dt
    return float(wrong/free) if free else 0.

def run_seq(seed, ti, th):
    w=World(cfg(seed)); birth=np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng=np.random.default_rng(seed*1403+ti*37)
    inject(w,rng,birth,N_SIDE,8,32,LOW[0],LOW[1],1)
    evolve(w,birth,th)
    inject(w,rng,birth,N_SIDE,48,72,HIGH[0],HIGH[1],2)
    chi=evolve(w,birth,th)
    pop,ok=sides_md(w)
    return ok,pop,chi

def run_sim(seed, ti, th):
    w=World(cfg(seed)); birth=np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng=np.random.default_rng(seed*1409+ti*41)
    inject(w,rng,birth,N_SIDE,8,32,LOW[0],LOW[1],1)
    inject(w,rng,birth,N_SIDE,48,72,HIGH[0],HIGH[1],2)
    chi=evolve(w,birth,2*th)
    pop,ok=sides_md(w)
    return ok,pop,chi

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials,th=((931,),1,150) if args.smoke else (SEEDS,TRIALS,T_HALF)
    print(f"BP-C8 start smoke={args.smoke}")
    seq,sim=[],[]
    for s in seeds:
        for ti in range(trials):
            seq.append(run_seq(s,ti,th)); sim.append(run_sim(s,ti,th))
    b1=float(np.mean([1 if r[0] else 0 for r in seq]))
    b2=float(np.mean([1 if r[0] else 0 for r in sim]))
    b3=float(np.mean([1 if r[1] else 0 for r in seq]))
    b4=float(np.mean([r[2] for r in seq]))
    p1,p2,p3,p4=b1>=0.90,b2<=0.80,b3>=0.80,b4<=0.15
    verdict="PASS" if all([p1,p2,p3,p4]) else "NULL"
    result={"id":"BP-C8","bars":{
        "B1_seq":{"value":b1,"threshold":0.90,"pass":p1},
        "B2_sim":{"value":b2,"threshold":0.80,"pass":p2},
        "B3_pop":{"value":b3,"threshold":0.80,"pass":p3},
        "B4_chi":{"value":b4,"threshold":0.15,"pass":p4},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-C8"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C8: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
