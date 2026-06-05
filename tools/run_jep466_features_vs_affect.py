"""JEP-466 — does the reservoir's NUMBER OF FEATURES raise the order-3 affect ceiling over clouds?
The last untested lever (the energy model's main hyperparameter). Pre-reg bars in the amendment doc.
"""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import atom_vector
from world.valence_reservoir import ValenceReservoirLearner

D, K, K_FILL, N_FILL = 4096, 3, 4, 200
N_TR, N_TE = 1200, 600
NFS = [600, 1500, 3000, 6000]

def run(seed, nf):
    rng = np.random.default_rng(seed*100+nf)
    slots=[(atom_vector(f"slot{i}_0",D),atom_vector(f"slot{i}_1",D)) for i in range(K)]
    FILL=np.stack([atom_vector(f"fill_{i}",D) for i in range(N_FILL)]); seen=set()
    def concept():
        while True:
            f=frozenset(int(x) for x in rng.choice(N_FILL,size=K_FILL,replace=False))
            if f not in seen: break
        seen.add(f); ch=rng.integers(2,size=K)
        v=sum(slots[i][ch[i]] for i in range(K))+FILL[list(f)].sum(axis=0)
        v=v/(np.linalg.norm(v)+1e-9)
        return v.astype(np.float64),(1.0 if ch.sum()%2==0 else -1.0)
    res=ValenceReservoirLearner(n_inputs=D,n_features=nf,seed=seed)
    for _ in range(N_TR):
        x,val=concept(); res.experience(x,val)
    ok=0
    for _ in range(N_TE):
        x,val=concept(); ok+=(np.sign(res.feel(x))==val)
    return ok/N_TE

if __name__=="__main__":
    print(f"=== JEP-466: reservoir n_features vs order-3 affect ceiling (D={D}) ===",flush=True)
    seeds=[0,7]; R={}
    for s in seeds:
        R[s]={nf:run(s,nf) for nf in NFS}
        print(f"  seed {s}: "+" ".join(f"M{nf}={R[s][nf]:.3f}" for nf in NFS),flush=True)
    J466a=all(R[s][6000]>=R[s][600]+0.10 for s in seeds)
    J466b=all(R[s][6000]>=0.80 for s in seeds)
    passed=J466a
    print("\n--- VERDICT ---",flush=True)
    print(f"J466a more features help (M6000>=M600+0.10): {J466a}",flush=True)
    print(f"J466b M6000 crosses 0.80                   : {J466b}",flush=True)
    verdict=("PASS - reservoir feature count IS the lever for order-3 affect (at C(P,k) cost)" if passed
             else "NULL - even 6000 features don't crack order-3 over clouds (cloud noise floor)")
    print(f"\nJEP-466: {verdict}",flush=True)
    out=Path.home()/".eqmod"/"bet"/"JEP466"; out.mkdir(parents=True,exist_ok=True)
    (out/"result.json").write_text(json.dumps({"R":{str(s):{str(nf):R[s][nf] for nf in NFS} for s in seeds},
        "passed":passed,"J466a":J466a,"J466b":J466b},indent=2,default=str))
    print("DONE",flush=True)
