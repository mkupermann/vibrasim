"""PRIM8-D0: pair replace kills old bridges. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (891, 901), 8
N_WRITE, MID = 10, 40.0
PORT_L, PORT_R = np.array([20.,25.,25.]), np.array([60.,25.,25.])
MAP_A, MAP_B = (400., 7000.), (400., 2500.)

def make_cfg(seed, replace):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_multislot_rel_freq=0.35, ilw_pair_link_enabled=True, ilw_pair_link_delta=1.,
        ilw_pair_replace_enabled=replace,
    )

def idle(w,n):
    dt=float(w.config.dt)
    for _ in range(n): tick(w,dt)

def n_cross(w):
    n=0
    for b in range(w.b_count):
        if not w.b_alive[b]: continue
        i,j=int(w.b_atom_i[b]),int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]: continue
        if (float(w.k_pos[i,0])<MID)!=(float(w.k_pos[j,0])<MID): n+=1
    return n

def write_map(w,rng,pair):
    fL,fR=pair
    for _ in range(N_WRITE):
        apply_ilw_pair_write(w,PORT_L,PORT_R,fL,fR,rng)
    idle(w,10)

def bridge_is_B(w):
    # any cross bridge closer to Map B R than Map A R for L~400
    for b in range(w.b_count):
        if not w.b_alive[b]: continue
        i,j=int(w.b_atom_i[b]),int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]: continue
        xi,xj=float(w.k_pos[i,0]),float(w.k_pos[j,0])
        if (xi<MID)==(xj<MID): continue
        if xi<MID: fL,fR=float(w.k_freq[i]),float(w.k_freq[j])
        else: fL,fR=float(w.k_freq[j]),float(w.k_freq[i])
        if abs(fL-400)>abs(fL-1500): continue
        return abs(fR-2500)<abs(fR-7000)
    return False

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args=p.parse_args(argv)
    seeds,trials=((891,),3) if args.smoke else (SEEDS,TRIALS)
    print(f"PRIM8-D0 start smoke={args.smoke}")
    r1,r2,r3=[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng=np.random.default_rng(seed*46099+ti*193)
            w=World(make_cfg(seed,True))
            write_map(w,rng,MAP_A); write_map(w,rng,MAP_B)
            r1.append(n_cross(w)==1)
            r3.append(bridge_is_B(w))
            w0=World(make_cfg(seed,False))
            write_map(w0,rng,MAP_A); write_map(w0,rng,MAP_B)
            r2.append(n_cross(w0)>=2)
    a1,a2,a3=float(np.mean(r1)),float(np.mean(r2)),float(np.mean(r3))
    p1,p2,p3=a1>=0.90,a2>=0.80,a3>=0.85
    verdict="PASS" if all([p1,p2,p3]) else "NULL"
    result={"id":"PRIM8-D0","bars":{
        "R1_replace_one_bridge":{"value":a1,"threshold":0.90,"pass":p1},
        "R2_off_multi":{"value":a2,"threshold":0.80,"pass":p2},
        "R3_endpoints_B":{"value":a3,"threshold":0.85,"pass":p3},
    },"verdict":verdict}
    out=Path.home()/".eqmod"/"bet"/"PRIM8-D0"; out.mkdir(parents=True, exist_ok=True)
    path=out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nPRIM8-D0: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
