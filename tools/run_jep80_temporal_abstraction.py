"""JEP-80 - H-JEPA building block: direct K-step latent prediction vs iterated 1-step (compounding) prediction."""
import numpy as np, torch, torch.nn as nn
torch.manual_seed(80); np.random.seed(80); g=torch.Generator().manual_seed(80)
P=torch.randn(32,2,generator=g); SIG=0.05; KS=[1,2,4,8,12]; KMAX=max(KS)
def ob(s): return torch.tanh(s@P.T)+0.03*torch.randn(s.shape[0],32,generator=g)
def rollouts(n=3000,T=KMAX+1):
    Os,As,Ss=[],[],[]
    for _ in range(n):
        s=torch.rand(1,2,generator=g)*2-1; os_,as_,ss_=[],[],[]
        for t in range(T):
            os_.append(ob(s)); ss_.append(s.clone())
            a=(torch.rand(1,2,generator=g)*2-1)*0.25
            s=torch.clamp(s+a+SIG*torch.randn(1,2,generator=g),-1,1); as_.append(a)
        Os.append(torch.cat(os_)); As.append(torch.cat(as_)); Ss.append(torch.cat(ss_))
    return torch.stack(Os),torch.stack(As),torch.stack(Ss)  # [n,T,*]
def enc_net(): return nn.Sequential(nn.Linear(32,32),nn.ReLU(),nn.Linear(32,8))
class P1(nn.Module):
    def __init__(s): super().__init__(); s.f=nn.Sequential(nn.Linear(10,32),nn.ReLU(),nn.Linear(32,8))
    def forward(s,z,a): return s.f(torch.cat([z,a],-1))
class PK(nn.Module):
    def __init__(s,k): super().__init__(); s.f=nn.Sequential(nn.Linear(8+2*k,48),nn.ReLU(),nn.Linear(48,8)); s.k=k
    def forward(s,z,A): return s.f(torch.cat([z,A],-1))
def vicreg(z):
    std=torch.sqrt(z.var(0)+1e-4); zc=z-z.mean(0); C=(zc.T@zc)/(zc.shape[0]-1); off=C-torch.diag(torch.diag(C))
    return torch.relu(1-std).mean()+0.04*(off**2).sum()/z.shape[1]
def main():
    print("=== JEP-80: direct K-step vs iterated 1-step latent prediction (H-JEPA building block) ===",flush=True)
    O,A,S=rollouts(); n=O.shape[0]
    enc=enc_net(); p1=P1()
    opt=torch.optim.Adam(list(enc.parameters())+list(p1.parameters()),lr=2e-3)
    for ep in range(220):  # train encoder + 1-step jointly
        idx=torch.randperm(n,generator=g)[:512]; t=int(torch.randint(0,KMAX,(1,),generator=g))
        z=enc(O[idx,t]); zt=enc(O[idx,t+1]); loss=((p1(z,A[idx,t])-zt)**2).mean()+vicreg(z)
        opt.zero_grad(); loss.backward(); opt.step()
    for p_ in enc.parameters(): p_.requires_grad_(False)
    # probe trained on encoder latents -> true state, fit once on z_t over all t
    with torch.no_grad():
        Zall=enc(O.reshape(-1,32)).numpy(); Sall=S.reshape(-1,2).numpy()
    X=np.hstack([Zall,np.ones((len(Zall),1))]); Wp,_,_,_=np.linalg.lstsq(X,Sall,rcond=None)
    def decode_r2(Zpred,Strue):
        Xp=np.hstack([Zpred,np.ones((len(Zpred),1))]); pr=Xp@Wp
        return 1-((Strue-pr)**2).sum()/((Strue-Strue.mean(0))**2).sum()
    print("    K    iterated-1step R2    direct-Kstep R2     gap",flush=True)
    rows=[]
    for K in KS:
        # direct predK trained for this K
        pk=PK(K); opt2=torch.optim.Adam(pk.parameters(),lr=2e-3)
        for ep in range(180):
            idx=torch.randperm(n,generator=g)[:512]
            with torch.no_grad(): z0=enc(O[idx,0]); zK=enc(O[idx,K])
            Aseq=A[idx,0:K].reshape(len(idx),-1)
            loss=((pk(z0,Aseq)-zK)**2).mean(); opt2.zero_grad(); loss.backward(); opt2.step()
        with torch.no_grad():
            z0=enc(O[:,0])
            zi=z0.clone()
            for t in range(K): zi=p1(zi,A[:,t])           # iterated
            zd=pk(z0,A[:,0:K].reshape(n,-1))               # direct
        sK=S[:,K].numpy()
        ri=decode_r2(zi.numpy(),sK); rd=decode_r2(zd.numpy(),sK); rows.append((K,ri,rd))
        print(f"   {K:>2}      {ri:>10.3f}        {rd:>10.3f}     {rd-ri:>+.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    K,ri,rd=rows[-1]
    if (rd-ri)>=0.15 and rd>=0.50:
        print(f"JEP-80: PASS - at horizon K={K}, DIRECT K-step prediction decodes the future state far better than",flush=True)
        print(f"ITERATING the 1-step predictor (R2 {rd:.2f} vs {ri:.2f}, gap {rd-ri:+.2f}): iterating COMPOUNDS model",flush=True)
        print(f"error, the direct temporal-abstraction predictor does not. This is the H-JEPA building block - predict",flush=True)
        print(f"the JUMP, don't iterate the step, for long horizons. Established (H-JEPA, LeCun), named; no novelty.",flush=True)
    else:
        print(f"JEP-80: NULL/PARTIAL - K={K} gap {rd-ri:+.2f} (direct {rd:.2f}, iter {ri:.2f}); bars 0.15/0.50.",flush=True)
        print(f"Compounding cost is smaller than the standard story at this scale - reported honestly.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
