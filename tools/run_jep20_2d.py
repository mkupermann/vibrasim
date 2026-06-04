"""JEP-20 - 2D relational inference: recover latent 2D grid of concepts from local relations via SR. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(123)
K=8; S=K*K
CELLS=[(x,y) for x in range(K) for y in range(K)]; ID={c:i for i,c in enumerate(CELLS)}
ADJ={c:set() for c in CELLS}
for (x,y) in CELLS:
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        if 0<=x+dx<K and 0<=y+dy<K: ADJ[(x,y)].add((x+dx,y+dy))
gamma=0.97
def sr_td(steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; Mt[ID[c]]+=alpha*(I[ID[c]]+gamma*Mt[ID[nb]]-Mt[ID[c]]); c=nb
    return Mt
def main():
    print(f"=== JEP-20: 2D relational inference from cognitive map (K={K} grid, S={S}) ===",flush=True)
    Mt=sr_td()
    A=0.5*(Mt+Mt.T); Ac=A-A.mean(0,keepdims=True)-A.mean(1,keepdims=True)+A.mean()
    w,V=np.linalg.eigh(Ac); order=np.argsort(w)[::-1]
    # leading 2 non-trivial eigenvectors as recovered 2D coords
    rec=V[:,order[:2]]
    truex=np.array([c[0] for c in CELLS],float); truey=np.array([c[1] for c in CELLS],float)
    # align recovered axes to (x,y): try both assignments + signs, pick best by |corr|
    def corr(a,b): return abs(np.corrcoef(a,b)[0,1])
    best=None
    for ax in [(0,1),(1,0)]:
        cx=corr(rec[:,ax[0]],truex); cy=corr(rec[:,ax[1]],truey)
        if best is None or cx+cy>best[0]: best=(cx+cy,ax,cx,cy)
    _,ax,cx,cy=best
    rx=rec[:,ax[0]]*np.sign(np.corrcoef(rec[:,ax[0]],truex)[0,1])
    ry=rec[:,ax[1]]*np.sign(np.corrcoef(rec[:,ax[1]],truey)[0,1])
    print(f"  recovered-coord vs true correlation:  x-axis={cx:.3f}  y-axis={cy:.3f}",flush=True)
    # relational inference on NON-adjacent pairs: relative direction (east = larger x, north = larger y)
    okE=0;okN=0;tot=0
    for _ in range(3000):
        i=rng.integers(S); j=rng.integers(S)
        if i==j: continue
        ci,cj=CELLS[i],CELLS[j]
        if cj in ADJ[ci]: continue   # skip adjacent
        if ci[0]!=cj[0]:
            tot+=1
            predE = rx[i]>rx[j]; trueE = ci[0]>cj[0]; okE+=int(predE==trueE)
        if ci[1]!=cj[1]:
            predN = ry[i]>ry[j]; trueN = ci[1]>cj[1]; okN+=int(predN==trueN)
    accE=okE/max(tot,1); 
    # count N separately
    totN=0;okN2=0
    for _ in range(3000):
        i=rng.integers(S); j=rng.integers(S)
        if i==j: continue
        ci,cj=CELLS[i],CELLS[j]
        if cj in ADJ[ci] or ci[1]==cj[1]: continue
        totN+=1; okN2+=int((ry[i]>ry[j])==(ci[1]>cj[1]))
    accN=okN2/max(totN,1)
    print(f"  relational inference (non-adjacent):  east-of acc={accE:.3f}   north-of acc={accN:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if cx>=0.9 and cy>=0.9 and accE>=0.9 and accN>=0.9:
        print(f"JEP-20: PASS - the cognitive map recovers 2D structure from LOCAL relations: recovered coords",flush=True)
        print(f"correlate with true 2D at x={cx:.2f}, y={cy:.2f} (grid-cell-like codes from the SR eigenvectors),",flush=True)
        print(f"and 2D relational inference on NON-adjacent concept pairs (never co-observed) reaches east={accE:.2f},",flush=True)
        print(f"north={accN:.2f}. 2D relational generalization from purely local structure - extends JEP-17 (1D) to",flush=True)
        print(f"2D. SR grid-cells (Stachenfeld 2017), spectral embedding established - named as such.",flush=True)
    else:
        print(f"JEP-20: PARTIAL/NULL - corr x{cx:.2f}/y{cy:.2f}, infer E{accE:.2f}/N{accN:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
