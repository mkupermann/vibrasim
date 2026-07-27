"""BP-E25 table-free K=3 multi-sample; bridge ablation control. Headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import apply_ilw_pair_write, tick
from world.state import World

SEEDS, TRIALS = (801, 811), 8
N_WRITE, T_TRAIN, T_PROP, T_END, MID = 6, 9, 40, 30, 40.0
PAIRS = ((400.0, 7000.0), (1500.0, 2500.0), (5000.0, 800.0))
Y_SLOTS = (13.0, 37.0)
K_CLASS = 3

def make_cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80.,50.,50.), n_vibrations_max=2048, n_nodes_max=2048,
        rng_seed=seed, r_1=5., r_2=28., freq_tolerance=0.03, pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., speed_min=0., speed_max=0., midplane_wall_enabled=True, midplane_wall_x=MID,
        ilw_enabled=True, ilw_radius=8., ilw_delta_strength=0.5, atom_valence=0, ilw_multislot_enabled=True,
        ilw_multislot_rel_freq=0.35, ilw_pair_link_enabled=True, ilw_pair_link_delta=1.0,
        neuron_dynamics_enabled=True, theta_fire=2., t_refractory=0.02, n_emit=0, bridge_charge_prop_rate=2.,
        bridge_prop_min_strength=0., charge_latch_enabled=True, charge_latch_tau=0.,
    )

def idle(w, n):
    dt = float(w.config.dt)
    for _ in range(n):
        tick(w, dt)

def ports(y):
    return np.array([20., y, 25.]), np.array([60., y, 25.])

def train(w, rng):
    schedule = [(c, y) for c in range(K_CLASS) for y in Y_SLOTS]
    for _ in range(max(0, T_TRAIN - len(schedule))):
        schedule.append((int(rng.integers(0, K_CLASS)), float(rng.choice(Y_SLOTS))))
    rng.shuffle(schedule)
    for c, y in schedule:
        fL, fR = PAIRS[c]
        pl, pr = ports(float(y))
        for __ in range(N_WRITE):
            apply_ilw_pair_write(w, pl, pr, fL, fR, rng)
        idle(w, 8)

def bridged_L(w):
    out = set()
    for b in range(w.b_count):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if not w.k_alive[i] or not w.k_alive[j]:
            continue
        xi, xj = float(w.k_pos[i,0]), float(w.k_pos[j,0])
        if (xi < MID) == (xj < MID):
            continue
        if xi < MID: out.add(i)
        if xj < MID: out.add(j)
    return list(out)

def all_L4_left(w):
    return [i for i in range(w.k_count) if w.k_alive[i] and int(w.k_level[i])>=4 and float(w.k_pos[i,0])<MID]

def kill_bridges(w):
    for b in range(w.b_count):
        w.b_alive[b] = False

def latch_partner_freq(w, L_idx):
    thr = float(w.config.theta_fire); dt = float(w.config.dt)
    w.k_charge[:w.k_count] = 0.; w.k_latch[:w.k_count] = 0.
    for t in range(T_PROP):
        if t % 10 == 0 and w.k_alive[L_idx]:
            w.k_charge[L_idx] = thr + 5.
        tick(w, dt)
    idle(w, T_END)
    best_i, best_v = -1, -1.
    for i in range(w.k_count):
        if not w.k_alive[i] or int(w.k_level[i])<4 or float(w.k_pos[i,0])<MID: continue
        v = float(w.k_latch[i])
        if v > best_v: best_v, best_i = v, i
    return float(w.k_freq[best_i]) if best_i>=0 and best_v>0 else 0.

def collect(w, Ls):
    out = []
    for Li in Ls:
        fR = latch_partner_freq(w, Li)
        if fR > 0: out.append((float(w.k_freq[Li]), fR))
    return out

def multi_ok(routes):
    if len(routes) < 4: return False
    fLs = np.array([r[0] for r in routes])
    qs = np.quantile(fLs, [0., 1/3, 2/3, 1.])
    counts = [int(np.sum((fLs>=a)&(fLs<=b+1e-9))) for a,b in zip(qs[:-1], qs[1:])]
    return sum(1 for c in counts if c>=2) >= 2

def score(routes):
    if len(routes) < 3: return 0., 0.
    fLs = np.array([r[0] for r in routes]); fRs = np.array([r[1] for r in routes])
    t1, t2 = np.quantile(fLs, [1/3, 2/3])
    groups = []
    for gi, mask in enumerate([fLs<=t1, (fLs>t1)&(fLs<=t2), fLs>t2]):
        g = fRs[mask]
        groups.append(float(np.mean(g)) if len(g) else None)
    means = [g for g in groups if g is not None]
    if len(means) < 2: return 0., 0.
    gaps = [abs(means[i]-means[j])/max(means[i],means[j],1.) for i in range(len(means)) for j in range(i+1,len(means))]
    min_gap = float(min(gaps))
    ok = 0
    for fL, fR in routes:
        gi = 0 if fL<=t1 else (1 if fL<=t2 else 2)
        m = groups[gi]
        if m is None: continue
        own = abs(fR-m)
        if all(own <= abs(fR-g)+1e-9 for k,g in enumerate(groups) if g is not None and k!=gi):
            ok += 1
    return ok/len(routes), min_gap

def main(argv=None):
    p = argparse.ArgumentParser(); p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, trials = ((801,), 3) if args.smoke else (SEEDS, TRIALS)
    print(f"BP-E25 start smoke={args.smoke}")
    b1s,b2s,b3s,b4s = [],[],[],[]
    for seed in seeds:
        for ti in range(trials):
            rng = np.random.default_rng(seed*43091+ti*179)
            w = World(make_cfg(seed)); train(w, rng)
            routes = collect(w, bridged_L(w))
            c,g = score(routes); b1s.append(c); b2s.append(g); b4s.append(multi_ok(routes))
            w2 = World(make_cfg(seed)); train(w2, rng); kill_bridges(w2)
            # probe all L4 left (bridges gone)
            routes2 = collect(w2, all_L4_left(w2))
            c2,_ = score(routes2) if routes2 else (0., 0.)
            # if no partner charge, cons=0
            if not routes2: c2 = 0.
            b3s.append(c2)
    a1,a2,a3,a4 = map(float, (np.mean(b1s),np.mean(b2s),np.mean(b3s),np.mean(b4s)))
    p1,p2,p3,p4 = a1>=0.80, a2>=0.20, a3<=0.40, a4>=0.90
    verdict = "PASS" if all([p1,p2,p3,p4]) else "NULL"
    result = {"id":"BP-E25","bars":{
        "B1_self_cons":{"value":a1,"threshold":0.80,"pass":p1},
        "B2_min_gap":{"value":a2,"threshold":0.20,"pass":p2},
        "B3_ablation_cons":{"value":a3,"threshold":0.40,"pass":p3},
        "B4_multisample":{"value":a4,"threshold":0.90,"pass":p4},
    },"verdict":verdict}
    out = Path.home()/".eqmod"/"bet"/"BP-E25"; out.mkdir(parents=True, exist_ok=True)
    path = out/("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k,v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-E25: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
