"""BET-124 — emergent generalization via substrate reservoir + online learning."""
import json
from pathlib import Path
import numpy as np
from world.reservoir import SubstrateReservoir

def task(seed=0):
    a=np.arange(10); b=np.arange(10)
    A,B=np.meshgrid(a,b); cells=np.column_stack([A.ravel(),B.ravel()])
    u=cells[:,0]/4.5-1; v=cells[:,1]/4.5-1                       # value-code to [-1,1]
    y=np.sin(2*u)*np.cos(2*v)+0.3*u*v                            # smooth nonlinear compositional
    X=np.column_stack([u,v])
    rng=np.random.default_rng(seed); idx=rng.permutation(len(X))
    tr,te=idx[:60],idx[60:]                                      # 60 seen / 40 held-out combos
    return X,y,tr,te

def r2(yt,yp):
    ss=np.sum((yt-yp)**2); s0=np.sum((yt-np.mean(yt))**2); return 1-ss/s0

def run(reservoir):
    X,y,tr,te=task()
    in_dim=X.shape[1]
    if reservoir:
        net=SubstrateReservoir(in_dim,1,D=800,spectral=1.6,seed=1,ridge=1e-2)
    else:
        net=SubstrateReservoir(in_dim,1,D=in_dim,seed=1,ridge=1e-4)
        net.R=np.eye(in_dim); net.bias=np.zeros(in_dim)         # linear: identity 'features'
        net.features=lambda x: np.asarray(x,float)
        net.P=np.eye(in_dim)/1e-4; net.Wout=np.zeros((1,in_dim))
    errs=[]
    for i in tr:                                                 # ONLINE: one example at a time
        errs.append(net.learn_online(X[i], [y[i]]))
    yp=np.array([net.predict(X[i])[0] for i in te])
    return r2(y[te],yp), errs[:5], errs[-5:]

if __name__=="__main__":
    print("=== BET-124: emergent generalization via substrate reservoir ===", flush=True)
    res_r2, e0, e1 = run(reservoir=True)
    lin_r2, le0, le1 = run(reservoir=False)
    print(f"  reservoir held-out R^2 : {res_r2:.3f}", flush=True)
    print(f"  linear    held-out R^2 : {lin_r2:.3f}", flush=True)
    print(f"  online MSE first->last : {np.mean(e0):.3f} -> {np.mean(e1):.4f}", flush=True)
    T124a=res_r2>=0.85; T124b=lin_r2<0.40; T124c=np.mean(e1)<0.5*np.mean(e0); T124d=(res_r2-lin_r2)>=0.4
    passed=T124a and T124b and T124c and T124d
    print("\n--- VERDICT ---", flush=True)
    print(f"T124a reservoir generalizes (R2>=0.85): {T124a}", flush=True)
    print(f"T124b linear cannot (R2<0.40)        : {T124b}", flush=True)
    print(f"T124c online learning (MSE drops)    : {T124c}", flush=True)
    print(f"T124d clear gap (>=0.4)              : {T124d}", flush=True)
    print(f"\nBET-124: {'PASS - emergent generalization + online learning on the substrate' if passed else 'NULL'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-124'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps({"res_r2":res_r2,"lin_r2":lin_r2,"passed":passed},indent=2))
    print("DONE", flush=True)
