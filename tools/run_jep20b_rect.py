"""JEP-20b - 2D relational inference on a RECTANGULAR grid (breaks square-grid eigen-degeneracy). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(123)
KX=9; KY=6; S=KX*KY   # rectangular -> non-degenerate axes
CELLS=[(x,y) for x in range(KX) for y in range(KY)]; ID={c:i for i,c in enumerate(CELLS)}
ADJ={c:set() for c in CELLS}
for (x,y) in CELLS:
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        if 0<=x+dx<KX and 0<=y+dy<KY: ADJ[(x,y)].add((x+dx,y+dy))
gamma=0.97
def sr_td(steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; Mt[ID[c]]+=alpha*(I[ID[c]]+gamma*Mt[ID[nb]]-Mt[ID[c]]); c=nb
    return Mt
def main():
    print(f"=== JEP-20b: 2D relational inference, RECTANGULAR grid {KX}x{KY} (S={S}) ===",flush=True)
    Mt=sr_td()
    A=0.5*(Mt+Mt.T); Ac=A-A.mean(0,keepdims=True)-A.mean(1,keepdims=True)+A.mean()
    w,V=np.linalg.eigh(Ac); order=np.argsort(w)[::-1]; rec=V[:,order[:2]]
    truex=np.array([c[0] for c in CELLS],float); truey=np.array([c[1] for c in CELLS],float)
    def corr(a,b): return abs(np.corrcoef(a,b)[0,1])
    best=None
    for ax in [(0,1),(1,0)]:
        cx=corr(rec[:,ax[0]],truex); cy=corr(rec[:,ax[1]],truey)
        if best is None or cx+cy>best[0]: best=(cx+cy,ax,cx,cy)
    _,ax,cx,cy=best
    rx=rec[:,ax[0]]*np.sign(np.corrcoef(rec[:,ax[0]],truex)[0,1])
    ry=rec[:,ax[1]]*np.sign(np.corrcoef(rec[:,ax[1]],truey)[0,1])
    print(f"  recovered-coord vs true correlation:  x-axis={cx:.3f}  y-axis={cy:.3f}",flush=True)
    totE=0;okE=0;totN=0;okN=0
    for _ in range(6000):
        i=rng.integers(S); j=rng.integers(S)
        if i==j: continue
        ci,cj=CELLS[i],CELLS[j]
        if cj in ADJ[ci]: continue
        if ci[0]!=cj[0]: totE+=1; okE+=int((rx[i]>rx[j])==(ci[0]>cj[0]))
        if ci[1]!=cj[1]: totN+=1; okN+=int((ry[i]>ry[j])==(ci[1]>cj[1]))
    accE=okE/max(totE,1); accN=okN/max(totN,1)
    print(f"  relational inference (non-adjacent):  east-of acc={accE:.3f}   north-of acc={accN:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if cx>=0.9 and cy>=0.9 and accE>=0.9 and accN>=0.9:
        print(f"JEP-20b: PASS - on a rectangular grid (breaking square-grid degeneracy), the cognitive map recovers",flush=True)
        print(f"2D structure cleanly (x={cx:.2f}, y={cy:.2f}) and infers global 2D relations on never-co-observed",flush=True)
        print(f"non-adjacent pairs (east={accE:.2f}, north={accN:.2f}). 2D relational generalization from local",flush=True)
        print(f"structure confirmed; JEP-20's shortfall WAS the eigen-degeneracy. SR grid-cells (Stachenfeld 2017),",flush=True)
        print(f"established - named as such.",flush=True)
    else:
        print(f"JEP-20b: PARTIAL/NULL - corr x{cx:.2f}/y{cy:.2f}, infer E{accE:.2f}/N{accN:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
