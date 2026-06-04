"""JEP-3 — diagnose JEPA model accuracy + simulation-based MPC (decode predicted state, plan to goal)."""
import numpy as np
rng=np.random.default_rng(0)
N=10; D=48
W1=rng.normal(0,1,(2,96)); W2=rng.normal(0,1,(96,D))
def enc(x,y):
    h=np.tanh(np.array([x/N,y/N])@W1); e=np.tanh(h@W2); return e/(np.linalg.norm(e)+1e-9)
CELLS={(x,y):enc(x,y) for x in range(N) for y in range(N)}
EMB=np.array([CELLS[(x,y)] for x in range(N) for y in range(N)])
KEYS=[(x,y) for x in range(N) for y in range(N)]
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)
def decode(emb): return KEYS[int(np.argmax(emb@EMB.T))]


def train_jepa():
    X=[];Y=[]
    for _ in range(8000):
        x,y=rng.integers(0,N),rng.integers(0,N); a=rng.integers(0,4); nx,ny=step(x,y,a)
        X.append(np.concatenate([CELLS[(x,y)],np.eye(4)[a]])); Y.append(CELLS[(nx,ny)])
    X=np.array(X);Y=np.array(Y); Din=D+4;H=160
    Wa=rng.normal(0,.1,(Din,H));Wb=rng.normal(0,.1,(H,D));lr=0.1
    for ep in range(500):
        Hh=np.tanh(X@Wa);P=Hh@Wb;P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
        g=(P-Y)/len(X); Wb-=lr*Hh.T@g; Wa-=lr*X.T@((g@Wb.T)*(1-Hh**2))
    def model(emb,a):
        h=np.tanh(np.concatenate([emb,np.eye(4)[a]])@Wa); p=h@Wb; return p/(np.linalg.norm(p)+1e-9)
    return model


def main():
    print("=== JEP-3: model accuracy + simulation-based MPC ===", flush=True)
    model=train_jepa()
    # DIAGNOSE: does the JEPA model predict the correct next CELL?
    acc=0; T=500
    for _ in range(T):
        x,y=rng.integers(0,N),rng.integers(0,N); a=rng.integers(0,4)
        pred=decode(model(CELLS[(x,y)],a)); acc+= int(pred==step(x,y,a))
    macc=acc/T
    print(f"  JEPA model next-cell accuracy = {macc:.2f}", flush=True)
    # SIMULATION-BASED MPC: BFS over actions using the learned model (decode each predicted state); reach goal
    def plan_reach(s,g,budget=2*N):
        x,y=s
        for _ in range(budget):
            # 1-step greedy via model: pick action whose predicted decoded cell is closest (true grid dist proxy via model rollouts depth 2)
            best=None;ba=0
            for a in range(4):
                p1=decode(model(CELLS[(x,y)],a))
                # depth-2 lookahead by model
                d2=min(abs(decode(model(CELLS[p1],a2))[0]-g[0])+abs(decode(model(CELLS[p1],a2))[1]-g[1]) for a2 in range(4))
                score=abs(p1[0]-g[0])+abs(p1[1]-g[1])+0.5*d2
                if best is None or score<best: best=score;ba=a
            x,y=step(x,y,ba)
            if (x,y)==g: return True
        return False
    pairs=[((rng.integers(0,N),rng.integers(0,N)),(rng.integers(0,N),rng.integers(0,N))) for _ in range(40)]
    reached=sum(plan_reach(s,g) for s,g in pairs if s!=g)+sum(1 for s,g in pairs if s==g)
    n=len(pairs)
    print(f"  simulation-MPC goals reached = {reached/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if macc>=0.9 and reached/n>=0.7:
        print(f"JEP-3: PASS - the JEPA model predicts next-states accurately ({macc:.2f}) and simulation-based MPC (roll the learned model forward, decode states, plan to goal) REACHES {reached/n:.2f} of goals. The fix: plan via the model-as-simulator (decode to cells), since the random-encoder energy was uninformative (JEP-2). JEPA world model + model-predictive planning works at PC scale.", flush=True)
    else:
        print(f"JEP-3: PARTIAL - model acc {macc:.2f}, MPC {reached/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
