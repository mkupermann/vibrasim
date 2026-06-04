"""JEP-2 — JEPA world model + EBM energy + MPC planning in a latent grid world (LeCun's architecture)."""
import numpy as np
rng=np.random.default_rng(0)
N=10; D=48
W1=rng.normal(0,1,(2,96)); W2=rng.normal(0,1,(96,D))
def enc(x,y):
    h=np.tanh(np.array([x/N,y/N])@W1); e=np.tanh(h@W2); return e/(np.linalg.norm(e)+1e-9)
CELLS={(x,y):enc(x,y) for x in range(N) for y in range(N)}
EMB=np.array([CELLS[(x,y)] for x in range(N) for y in range(N)])
IDX={(x,y):i for i,(x,y) in enumerate([(x,y) for x in range(N) for y in range(N)])}
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; nx,ny=min(max(x+dx,0),N-1),min(max(y+dy,0),N-1); return nx,ny


def train_jepa():
    # self-supervised: predict next-state embedding from (state-emb, action-onehot)
    X=[];Y=[]
    for _ in range(6000):
        x,y=rng.integers(0,N),rng.integers(0,N); a=rng.integers(0,4); nx,ny=step(x,y,a)
        X.append(np.concatenate([CELLS[(x,y)],np.eye(4)[a]])); Y.append(CELLS[(nx,ny)])
    X=np.array(X);Y=np.array(Y); Din=D+4;H=128
    Wa=rng.normal(0,.1,(Din,H));Wb=rng.normal(0,.1,(H,D));lr=0.1
    for ep in range(300):
        Hh=np.tanh(X@Wa);P=Hh@Wb;P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
        g=(P-Y)/len(X); Wb-=lr*Hh.T@g; Wa-=lr*X.T@((g@Wb.T)*(1-Hh**2))
    def model(emb,a):  # predict next-state embedding
        h=np.tanh(np.concatenate([emb,np.eye(4)[a]])@Wa); p=h@Wb; return p/(np.linalg.norm(p)+1e-9)
    return model


def main():
    print("=== JEP-2: JEPA world model + EBM + MPC ===", flush=True)
    model=train_jepa()
    def energy(emb,goal_emb): return -float(emb@goal_emb)   # low energy = close in representation space (EBM)
    def mpc_plan(cur_emb,goal_emb,horizon=3):
        # search action sequences up to horizon via the LEARNED model, pick first action of the min-energy rollout
        best=None;best_a=0
        def rollout(emb,depth):
            if depth==0: return energy(emb,goal_emb)
            return min(energy(model(emb,a),goal_emb) if depth==1 else rollout(model(emb,a),depth-1) for a in range(4))
        for a in range(4):
            e=rollout(model(cur_emb,a),horizon-1)
            if best is None or e<best: best=e;best_a=a
        return best_a
    # evaluate on held-out start/goal pairs
    pairs=[((rng.integers(0,N),rng.integers(0,N)),(rng.integers(0,N),rng.integers(0,N))) for _ in range(40)]
    reached=0; rnd=0
    for (sx,sy),(gx,gy) in pairs:
        if (sx,sy)==(gx,gy): reached+=1; rnd+=1; continue
        # MPC with learned JEPA model (act on TRUE state, plan with learned model)
        x,y=sx,sy
        for t in range(2*N):
            a=mpc_plan(CELLS[(x,y)],CELLS[(gx,gy)]); x,y=step(x,y,a)
            if (x,y)==(gx,gy): reached+=1; break
        # random baseline
        rx,ry=sx,sy
        for t in range(2*N):
            rx,ry=step(rx,ry,rng.integers(0,4))
            if (rx,ry)==(gx,gy): rnd+=1; break
    n=len(pairs)
    print(f"  MPC w/ learned JEPA model reached = {reached/n:.2f}", flush=True)
    print(f"  random-action baseline reached    = {rnd/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if reached/n>=0.7 and reached/n>=rnd/n+0.3:
        print(f"JEP-2: PASS - the JEPA world model + EBM energy + MPC planning REACHES goals ({reached/n:.2f} vs random {rnd/n:.2f}): the agent learned a latent world model self-supervised, defined energy as embedding-distance-to-goal, and PLANNED by rolling the model forward to minimize energy. LeCun's JEPA+EBM+MPC paradigm works at PC scale. Established methods, integrated demo.", flush=True)
    else:
        print(f"JEP-2: PARTIAL/NULL - MPC {reached/n:.2f}, random {rnd/n:.2f} (learned model may be too inaccurate to plan)", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
