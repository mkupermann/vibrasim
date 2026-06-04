"""JEP-78 - four-pillar capstone: regularized JEPA (VICReg) + latent MPC, with a collapse negative control."""
import numpy as np, torch, torch.nn as nn
torch.manual_seed(78); np.random.seed(78)
g=torch.Generator().manual_seed(78)
P=torch.randn(32,2,generator=g)
def obs(s): return torch.tanh(s@P.T)+0.05*torch.randn(s.shape[0],32,generator=g)
def rollouts(n=4000,T=6):
    O,A,O2=[],[],[]
    for _ in range(n):
        s=torch.rand(1,2,generator=g)*2-1
        for _ in range(T):
            a=(torch.rand(1,2,generator=g)*2-1)*0.3
            s2=torch.clamp(s+a,-1,1)
            O.append(obs(s)); A.append(a); O2.append(obs(s2)); s=s2
    return torch.cat(O),torch.cat(A),torch.cat(O2)
class Enc(nn.Module):
    def __init__(s): super().__init__(); s.f=nn.Sequential(nn.Linear(32,32),nn.ReLU(),nn.Linear(32,8))
    def forward(s,x): return s.f(x)
class Pred(nn.Module):
    def __init__(s): super().__init__(); s.f=nn.Sequential(nn.Linear(10,32),nn.ReLU(),nn.Linear(32,8))
    def forward(s,z,a): return s.f(torch.cat([z,a],-1))
def vicreg(z,zt):
    def var(Z):
        std=torch.sqrt(Z.var(0)+1e-4); return torch.relu(1.0-std).mean()
    def cov(Z):
        Zc=Z-Z.mean(0); C=(Zc.T@Zc)/(Zc.shape[0]-1); off=C-torch.diag(torch.diag(C)); return (off**2).sum()/Z.shape[1]
    return var(z)+var(zt), cov(z)+cov(zt)
def train(O,A,O2,reg=True,epochs=250):
    enc,pred=Enc(),Pred(); opt=torch.optim.Adam(list(enc.parameters())+list(pred.parameters()),lr=2e-3)
    n=O.shape[0]
    for ep in range(epochs):
        idx=torch.randperm(n,generator=g)[:1024]
        z=enc(O[idx]); zt=enc(O2[idx]); zp=pred(z,A[idx])
        predL=((zp-zt)**2).mean()
        v,c=vicreg(z,zt)
        loss=predL+(1.0*v+0.04*c if reg else 0.0*v)
        opt.zero_grad(); loss.backward(); opt.step()
    return enc,pred
def state_probe(enc,O,S):
    with torch.no_grad(): Z=enc(O).numpy()
    Sn=S.numpy(); X=np.hstack([Z,np.ones((len(Z),1))])
    W,_,_,_=np.linalg.lstsq(X,Sn,rcond=None); pred=X@W
    ss_res=((Sn-pred)**2).sum(); ss_tot=((Sn-Sn.mean(0))**2).sum(); return 1-ss_res/ss_tot
def mpc(enc,pred,n=200,H=10,rand=False):
    tot=0
    for _ in range(n):
        s=torch.rand(1,2,generator=g)*2-1; sg=torch.rand(1,2,generator=g)*2-1
        with torch.no_grad(): zg=enc(obs(sg))
        for _ in range(H):
            if rand: a=(torch.rand(1,2,generator=g)*2-1)*0.3
            else:
                cand=(torch.rand(64,2,generator=g)*2-1)*0.3
                with torch.no_grad():
                    z=enc(obs(s)).repeat(64,1); zp=pred(z,cand)
                    d=((zp-zg)**2).sum(1); a=cand[d.argmin()].unsqueeze(0)
            s=torch.clamp(s+a,-1,1)
        tot+=float(((s-sg)**2).sum().sqrt())
    return tot/n
def main():
    print("=== JEP-78: regularized JEPA (VICReg) + latent MPC, with collapse negative control ===",flush=True)
    O,A,O2=rollouts()
    # probe/eval states
    Se=torch.rand(2000,2,generator=g)*2-1; Oe=obs(Se)
    res={}
    for reg in [True,False]:
        enc,pred=train(O,A,O2,reg=reg)
        with torch.no_grad(): std=float(enc(Oe).std(0).mean())
        r2=state_probe(enc,Oe,Se); md=mpc(enc,pred); rb=mpc(enc,pred,rand=True)
        res[reg]=(std,r2,md,rb)
        tag="REGULARIZED (VICReg)" if reg else "CONTROL (no regularizer)"
        print(f"   {tag:<26} emb-std={std:.3f}  state-R2={r2:.3f}  MPC-dist={md:.3f}  (random={rb:.3f})",flush=True)
    print("\n--- VERDICT ---",flush=True)
    rstd,rr2,rmd,rrb=res[True]; cstd,cr2,cmd,crb=res[False]
    reg_ok = rstd>=0.30 and rr2>=0.80 and rmd<=0.30 and rmd<rrb
    ctl_collapse = cstd<=0.05 or cr2<=0.30
    if reg_ok and ctl_collapse:
        print(f"JEP-78: PASS - regularized JEPA gives a non-collapsed, state-decodable embedding (std={rstd:.2f},",flush=True)
        print(f"R2={rr2:.2f}) and supports latent MPC to goals (dist={rmd:.2f} < random {rrb:.2f}). The UNregularized",flush=True)
        print(f"control COLLAPSES (std={cstd:.2f}, R2={cr2:.2f}) - VICReg regularization is what prevents collapse.",flush=True)
        print(f"All four pillars together: joint-embedding + energy(prediction) + REGULARIZED + MPC. Established, named.",flush=True)
    else:
        print(f"JEP-78: NULL/PARTIAL - reg_ok={reg_ok}, ctl_collapse={ctl_collapse}. reg={res[True]} ctl={res[False]}",flush=True)
    print("HONEST SCOPE: encoder trained by gradient descent (torch), not substrate plasticity here; substrate-native",flush=True)
    print("predictor training shown separately (predictive coding, JEP-19). VICReg/JEPA/MPC established; no novelty.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
