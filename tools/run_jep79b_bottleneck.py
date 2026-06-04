"""JEP-79b - capacity-bottleneck regime: does JEPA beat generative when unpredictable content dominates?"""
import numpy as np, torch, torch.nn as nn
torch.manual_seed(791); np.random.seed(791); g=torch.Generator().manual_seed(791)
PRED_D, DIST_D, LAT = 32, 96, 4
P=torch.randn(PRED_D,2,generator=g); Q=torch.randn(DIST_D,2*8,generator=g)  # distractor is higher-dim latent
def make(n=4000,T=6,sig_d=2.0):
    O,A,O2,S=[],[],[],[]
    dd_dim=2*8
    for _ in range(n):
        s=torch.rand(1,2,generator=g)*2-1; d=torch.rand(1,dd_dim,generator=g)*2-1
        for _ in range(T):
            a=(torch.rand(1,2,generator=g)*2-1)*0.3
            s2=torch.clamp(s+a,-1,1); d2=torch.clamp(d+(torch.rand(1,dd_dim,generator=g)*2-1)*sig_d,-3,3)
            def ob(ss,dd): return torch.cat([torch.tanh(ss@P.T),torch.tanh(dd@Q.T)],1)+0.03*torch.randn(1,PRED_D+DIST_D,generator=g)
            O.append(ob(s,d)); A.append(a); O2.append(ob(s2,d2)); S.append(s); s,d=s2,d2
    return torch.cat(O),torch.cat(A),torch.cat(O2),torch.cat(S)
def enc_net(): return nn.Sequential(nn.Linear(PRED_D+DIST_D,64),nn.ReLU(),nn.Linear(64,LAT))
class Head(nn.Module):
    def __init__(s,o): super().__init__(); s.f=nn.Sequential(nn.Linear(LAT+2,64),nn.ReLU(),nn.Linear(64,o))
    def forward(s,z,a): return s.f(torch.cat([z,a],-1))
def vicreg(z):
    std=torch.sqrt(z.var(0)+1e-4); v=torch.relu(1-std).mean()
    zc=z-z.mean(0); C=(zc.T@zc)/(zc.shape[0]-1); off=C-torch.diag(torch.diag(C)); return v+0.04*(off**2).sum()/z.shape[1]
def train(O,A,O2,mode,epochs=300):
    enc=enc_net(); head=Head(LAT if mode=="jepa" else PRED_D+DIST_D)
    opt=torch.optim.Adam(list(enc.parameters())+list(head.parameters()),lr=2e-3); n=O.shape[0]
    for ep in range(epochs):
        idx=torch.randperm(n,generator=g)[:1024]; z=enc(O[idx])
        if mode=="jepa": loss=((head(z,A[idx])-enc(O2[idx]))**2).mean()+vicreg(z)
        else: loss=((head(z,A[idx])-O2[idx])**2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return enc
def probe(enc,O,S):
    with torch.no_grad(): Z=enc(O).numpy()
    Sn=S.numpy(); X=np.hstack([Z,np.ones((len(Z),1))]); W,_,_,_=np.linalg.lstsq(X,Sn,rcond=None); pr=X@W
    return 1-((Sn-pr)**2).sum()/((Sn-Sn.mean(0))**2).sum()
def main():
    print("=== JEP-79b: capacity bottleneck (latent=4, distractor 96-d dominant) - JEPA vs generative ===",flush=True)
    O,A,O2,S=make()
    rj=probe(train(O,A,O2,"jepa"),O,S); rg=probe(train(O,A,O2,"gen"),O,S)
    print(f"   JEPA state-R2 = {rj:.3f}   GENERATIVE state-R2 = {rg:.3f}   gap = {rj-rg:+.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if (rj-rg)>=0.20 and rj>=0.70:
        print(f"JEP-79b: PASS - in the BOTTLENECK regime (4-d latent, 96-d unpredictable distractor dominating recon",flush=True)
        print(f"loss) JEPA beats generative on state fidelity (R2 {rj:.2f} vs {rg:.2f}, gap {rj-rg:+.2f}). HERE latent",flush=True)
        print(f"prediction's feature-suppression pays off: the generative model spends scarce latent on noise. This",flush=True)
        print(f"LOCATES the JEPA advantage - it needs a capacity bottleneck, not just unpredictability. Established, named.",flush=True)
    else:
        print(f"JEP-79b: NULL - even bottlenecked, gap {rj-rg:+.2f} (JEPA {rj:.2f}, gen {rg:.2f}) < 0.20 bar. The JEPA-",flush=True)
        print(f"over-generative advantage stays small at this scale - stronger honest deflation of the standard story.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
