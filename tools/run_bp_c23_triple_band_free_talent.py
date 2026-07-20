"""BP-C23 free triple-band ordered specialisation vs same-band control. Headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

N_REG, T_FULL = 300, 1200
SEEDS, TRIALS = (3101, 3111, 3121), 3
BOX = (90., 50., 50.)
W1, W2 = 30.0, 60.0  # third boundaries
LOW, MID, HIGH = (100.0, 1000.0), (1000.0, 4000.0), (4000.0, 12000.0)
SAME = (100.0, 12000.0)

def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=BOX, n_vibrations_max=8192, n_nodes_max=4096,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=5., speed_max=25.,
        midplane_wall_enabled=True, midplane_wall_x=W1,  # only one wall in config - use custom walls via...
        repulsion_cell_size=100.0,
    )

# WorldConfig may only have one midplane wall. Check if dual walls exist.
# If only one wall, use single wall at W1 and inject three regions without second wall,
# or use wall at W1 only for partial segregation.

def inject(w, rng, n, x0, x1, f0, f1):
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
    w.n_alive=int(w.s_alive.sum())

def evolve(w, n):
    dt=float(w.config.dt)
    for _ in range(n):
        tick(w,dt); w.t+=dt

def thirds(w):
    L,M,R=[],[],[]
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4: continue
        d=int(math.floor(math.log10(max(float(w.k_freq[i]),1.))))
        x=float(w.k_pos[i,0])
        if x < W1: L.append(d)
        elif x < W2: M.append(d)
        else: R.append(d)
    pop=len(L)>=1 and len(M)>=1 and len(R)>=1
    ordered=pop and float(np.mean(L))<float(np.mean(M))<float(np.mean(R))
    return pop, ordered

def run_one(seed, ti, ordered_bands, t_total):
    w=World(cfg(seed))
    rng=np.random.default_rng(seed*1501+ti*113+int(ordered_bands)*17)
    if ordered_bands:
        inject(w,rng,N_REG,5,25,LOW[0],LOW[1])
        inject(w,rng,N_REG,35,55,MID[0],MID[1])
        inject(w,rng,N_REG,65,85,HIGH[0],HIGH[1])
    else:
        inject(w,rng,N_REG,5,25,SAME[0],SAME[1])
        inject(w,rng,N_REG,35,55,SAME[0],SAME[1])
        inject(w,rng,N_REG,65,85,SAME[0],SAME[1])
    evolve(w,t_total)
    return thirds(w)

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke",action="store_true")
    args=p.parse_args(argv)
    seeds,trials,t_tot=((3101,),1,300) if args.smoke else (SEEDS,TRIALS,T_FULL)
    print(f"BP-C23 start smoke={args.smoke}")
    on,off=[],[]
    for s in seeds:
        for ti in range(trials):
            on.append(run_one(s,ti,True,t_tot))
            off.append(run_one(s,ti,False,t_tot))
    b1=float(np.mean([1 if r[1] else 0 for r in on]))
    b2=float(np.mean([1 if r[1] else 0 for r in off]))
    b3=float(np.mean([1 if r[0] else 0 for r in on]))
    b4=b1-b2
    p1,p2,p3,p4=b1>=0.80,b2<=0.40,b3>=0.80,b4>=0.30
    verdict="PASS" if all([p1,p2,p3,p4]) else "NULL"
    result={"id":"BP-C23","bars":{
        "B1_triple_ordered":{"value":b1,"threshold":0.80,"pass":p1},
        "B2_ctrl_ordered":{"value":b2,"threshold":0.40,"pass":p2},
        "B3_triple_pop":{"value":b3,"threshold":0.80,"pass":p3},
        "B4_delta":{"value":b4,"threshold":0.30,"pass":p4},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"BP-C23"; out.mkdir(parents=True,exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result,indent=2),encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-C23: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
