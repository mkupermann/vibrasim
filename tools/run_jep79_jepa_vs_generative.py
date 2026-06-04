"""JEP-79 - JEPA (latent prediction) vs GENERATIVE (obs prediction) under unpredictable distractors."""
import numpy as np, torch, torch.nn as nn
torch.manual_seed(79); np.random.seed(79); g=torch.Generator().manual_seed(79)
P=torch.randn(32,2,generator=g); Q=torch.randn(32,2,generator=g)
def make(sig_d,n=3500,T=6):
    O,A,O2,S=[],[],[],[]
    for _ in range(n):
        s=torch.rand(1,2,generator=g)*2-1; d=torch.rand(1,2,generator=g)*2-1
        for _ in range(T):
            a=(torch.rand(1,2,generator=g)*2-1)*0.3
            s2=torch.clamp(s+a,-1,1); d2=torch.clamp(d+(torch.rand(1,2,generator=g)*2-1)*sig_d,-3,3)
            def ob(ss,dd): return torch.cat([torch.tanh(ss@P.T),torch.tanh(dd@Q.T)],1)+0.03*torch.randn(1,64,generator=g)
            O.append(ob(s,d)); A.append(a); O2.append(ob(s2,d2)); S.append(s)
            s,d=s2,d2
    return torch.cat(O),torch.cat(A),torch.cat(O2),torch.cat(S)
def enc_net(): return nn.Sequential(nn.Linear(64,48),nn.ReLU(),nn.Linear(48,8))
class Pred(nn.Module):
    def __init__(s,o): super().__init__(); s.f=nn.Sequential(nn.Linear(8+2,48),nn.ReLU(),nn.Linear(48,o))
    def forward(s,z,a): return s.f(torch.cat([z,a],-1))
def vicreg(z):
    std=torch.sqrt(z.var(0)+1e-4); v=torch.relu(1-std).mean()
    zc=z-z.mean(0); C=(zc.T@zc)/(zc.shape[0]-1); off=C-torch.diag(torch.diag(C)); c=(off**2).sum()/z.shape[1]
    return v+0.04*c
def train(O,A,O2,mode,epochs=250):
    enc=enc_net(); head=Pred(8 if mode=="jepa" else 64)
    opt=torch.optim.Adam(list(enc.parameters())+list(head.parameters()),lr=2e-3); n=O.shape[0]
    for ep in range(epochs):
        idx=torch.randperm(n,generator=g)[:1024]
        z=enc(O[idx])
        if mode=="jepa":
            zt=enc(O2[idx]); loss=((head(z,A[idx])-zt)**2).mean()+vicreg(z)
        else:
            loss=((head(z,A[idx])-O2[idx])**2).mean()  # reconstruct next obs
        opt.zero_grad(); loss.backward(); opt.step()
    return enc
def probe(enc,O,S):
    with torch.no_grad(): Z=enc(O).numpy()
    Sn=S.numpy(); X=np.hstack([Z,np.ones((len(Z),1))]); W,_,_,_=np.linalg.lstsq(X,Sn,rcond=None)
    pr=X@W; return 1-((Sn-pr)**2).sum()/((Sn-Sn.mean(0))**2).sum()
def main():
    print("=== JEP-79: JEPA (latent) vs GENERATIVE (obs) under unpredictable distractors ===",flush=True)
    print("   sigma_d   JEPA state-R2   GENERATIVE state-R2   gap",flush=True)
    rows=[]
    for sd in [0.0,0.5,1.0,2.0]:
        O,A,O2,S=make(sd)
        ej=train(O,A,O2,"jepa"); eg=train(O,A,O2,"gen")
        rj=probe(ej,O,S); rg=probe(eg,O,S); rows.append((sd,rj,rg))
        print(f"   {sd:>5.1f}     {rj:>9.3f}       {rg:>13.3f}     {rj-rg:>+.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    sd,rj,rg=rows[-1]
    if rj>=0.80 and (rj-rg)>=0.20:
        print(f"JEP-79: PASS - at high distractor (sigma_d={sd}), JEPA stays state-faithful (R2={rj:.2f}) while the",flush=True)
        print(f"GENERATIVE model degrades (R2={rg:.2f}, gap {rj-rg:+.2f}). Predicting in LATENT space lets JEPA SUPPRESS",flush=True)
        print(f"unpredictable features; the generative model wastes capacity modeling them. LeCun's core JEPA argument,",flush=True)
        print(f"demonstrated with a generative negative control. Established rationale, named; no novelty.",flush=True)
    else:
        print(f"JEP-79: NULL/PARTIAL - high-distractor JEPA R2={rj:.2f}, gap {rj-rg:+.2f} (bars 0.80 / 0.20). The",flush=True)
        print(f"generative model is more robust here than the standard story claims - reported honestly.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
