"""BP-C9 stationary vs moving free dual-band talent. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_SIDE, T, SEEDS, TRIALS = 400, 1000, (1201, 1211, 1221), 3
MID = 40.0
LOW, HIGH = (100.0, 2000.0), (500.0, 10000.0)

def cfg(seed, moving):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=8192, n_nodes_max=4096,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0.,
        speed_min=5. if moving else 0., speed_max=25. if moving else 0.,
        midplane_wall_enabled=True, midplane_wall_x=MID,
    )

def inject(w, rng, birth, n, x0, x1, f0, f1, tag, moving):
    dead = np.where(~w.s_alive)[0]
    slots = dead[:n] if len(dead)>=n else np.arange(int(w.n_alive), min(int(w.n_alive)+n, w.config.n_vibrations_max))
    for k,i in enumerate(slots):
        i=int(i)
        w.s_pos[i]=[rng.uniform(x0,x1), rng.uniform(8,42), rng.uniform(8,42)]
        w.s_freq[i]=float(np.exp(rng.uniform(np.log(f0), np.log(f1))))
        w.s_pol[i]=k%2==0
        if moving:
            z,phi=rng.uniform(-1,1), rng.uniform(0,2*np.pi)
            sq=float(np.sqrt(max(1-z*z,0))); sp=float(rng.uniform(5,25))
            w.s_vel[i]=sp*np.array([sq*np.cos(phi), sq*np.sin(phi), z])
        else:
            w.s_vel[i]=0.
        w.s_alive[i]=True
        if birth is not None: birth[i]=tag
    w.n_alive=int(w.s_alive.sum())

def sides_ok(w):
    L,R=[],[]
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        d=int(math.floor(math.log10(max(float(w.k_freq[i]),1.))))
        (L if float(w.k_pos[i,0])<MID else R).append(d)
    pop=len(L)>=1 and len(R)>=1
    if not pop: return False, False, 0.
    ok=float(np.mean(L))<float(np.mean(R))
    return pop, ok, 0.

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

def run(seed, ti, ticks, moving):
    w=World(cfg(seed, moving))
    birth=np.zeros(w.config.n_vibrations_max, dtype=np.int8)
    rng=np.random.default_rng(seed*1501+ti*43+int(moving))
    inject(w,rng,birth,N_SIDE,8,32,LOW[0],LOW[1],1,moving)
    inject(w,rng,birth,N_SIDE,48,72,HIGH[0],HIGH[1],2,moving)
    chi=evolve(w,birth,ticks)
    pop,ok,_=sides_ok(w)
    return ok,pop,chi

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials,ticks=((1201,),1,250) if args.smoke else (SEEDS,TRIALS,T)
    print(f"BP-C9 start smoke={args.smoke}")
    st,mv=[],[]
    for s in seeds:
        for ti in range(trials):
            st.append(run(s,ti,ticks,False)); mv.append(run(s,ti,ticks,True))
    b1=float(np.mean([1 if r[0] else 0 for r in st]))
    b2=float(np.mean([1 if r[0] else 0 for r in mv]))
    b3=float(np.mean([1 if r[1] else 0 for r in st]))
    b4=float(np.mean([r[2] for r in st]))
    p1,p2,p3,p4=b1>=0.90,b2<=0.80,b3>=0.80,b4<=0.15
    verdict="PASS" if all([p1,p2,p3,p4]) else "NULL"
    result={"id":"BP-C9","bars":{
        "B1_stat":{"value":b1,"threshold":0.90,"pass":p1},
        "B2_moving":{"value":b2,"threshold":0.80,"pass":p2},
        "B3_pop":{"value":b3,"threshold":0.80,"pass":p3},
        "B4_chi":{"value":b4,"threshold":0.15,"pass":p4},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-C9"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C9: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
