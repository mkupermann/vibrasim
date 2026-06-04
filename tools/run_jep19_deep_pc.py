"""JEP-19 - deep predictive coding vs backprop on Fashion-MNIST, on the AMD GPU (torch-directml)."""
import time, torch, torch.nn as nn, torch.nn.functional as F
import torch_directml as tdml
dev=tdml.device(0)
import torchvision, torchvision.transforms as T
def load():
    tr=torchvision.datasets.FashionMNIST("data",train=True,download=True)
    te=torchvision.datasets.FashionMNIST("data",train=False,download=True)
    Xtr=(tr.data.float()/255.0).reshape(-1,784); ytr=tr.targets
    Xte=(te.data.float()/255.0).reshape(-1,784); yte=te.targets
    return Xtr,ytr,Xte,yte
Xtr,ytr,Xte,yte=load()
def acc_of(net,X,y):
    with torch.no_grad():
        out=[]
        for i in range(0,len(X),2000): out.append(net(X[i:i+2000].to(dev)).argmax(1).cpu())
        return (torch.cat(out)==y).float().mean().item()

def backprop(hidden, epochs=12, bs=256):
    torch.manual_seed(0)
    layers=[]; dims=[784]+hidden+[10]
    for i in range(len(dims)-1):
        layers.append(nn.Linear(dims[i],dims[i+1]))
        if i<len(dims)-2: layers.append(nn.Tanh())
    net=nn.Sequential(*layers).to(dev); opt=torch.optim.Adam(net.parameters(),1e-3); lf=nn.CrossEntropyLoss()
    Xg=Xtr.to(dev); yg=ytr.to(dev); n=len(Xg)
    for ep in range(epochs):
        perm=torch.randperm(n,device=dev)
        for b in range(0,n,bs):
            idx=perm[b:b+bs]; opt.zero_grad(); lf(net(Xg[idx]),yg[idx]).backward(); opt.step()
    return acc_of(net,Xte,yte)

def pred_coding(hidden, epochs=12, bs=256, infer=20, beta=0.5, lr=0.02):
    # hierarchical PC: activities x_l, predictions pred_l=W_l tanh(x_{l-1}), errors e_l=x_l-pred_l
    torch.manual_seed(0)
    dims=[784]+hidden+[10]; L=len(dims)-1
    Ws=[ (torch.randn(dims[i+1],dims[i],device=dev)*(1.0/dims[i]**0.5)) for i in range(L) ]
    Xg=Xtr.to(dev); Yg=F.one_hot(ytr,10).float().to(dev); n=len(Xg)
    def f(x): return torch.tanh(x)
    def df(x): return 1-torch.tanh(x)**2
    for ep in range(epochs):
        perm=torch.randperm(n,device=dev)
        for b in range(0,n,bs):
            idx=perm[b:b+bs]; x0=Xg[idx]; tgt=Yg[idx]
            # init activities by feedforward
            acts=[x0]
            for l in range(L): acts.append(Ws[l]@f(acts[-1]).T if False else f(acts[-1])@Ws[l].T)
            # clamp output to target
            acts[-1]=tgt.clone()
            # inference: relax hidden activities (1..L-1)
            for _ in range(infer):
                # predictions and errors
                preds=[None]+[ f(acts[l])@Ws[l].T for l in range(L) ]
                errs=[None]+[ acts[l+1-0]-preds[l+1-0] if False else acts[l]-preds[l] for l in range(1,L+1) ]
                for l in range(1,L):  # update hidden layer l
                    e_l=acts[l]-preds[l]
                    e_lp1=acts[l+1]-preds[l+1]
                    top=(e_lp1@Ws[l])*df(acts[l])
                    acts[l]=acts[l]+beta*(-e_l+top)
            # learn: dW_l ∝ e_{l+1} outer f(acts[l])
            preds=[None]+[ f(acts[l])@Ws[l].T for l in range(L) ]
            for l in range(L):
                e=acts[l+1]-preds[l+1]
                Ws[l]=Ws[l]+lr*(e.T@f(acts[l]))/len(idx)
    # build a forward net for eval
    def net(x):
        a=x
        for l in range(L): a=f(a)@Ws[l].T if l<L-1 else f(a)@Ws[l].T
        return a
    # eval uses tanh between layers, linear last (match training f on inputs)
    def fwd(x):
        a=x
        for l in range(L-1): a=torch.tanh(a)@Ws[l].T
        return torch.tanh(a)@Ws[L-1].T
    return acc_of(fwd,Xte,yte)

def main():
    print("=== JEP-19: deep PC vs backprop on Fashion-MNIST (AMD GPU) ===",flush=True)
    res={}
    for hid,lbl in [([1024],"1-hidden"),([1024,1024],"2-hidden")]:
        ab=backprop(hid); ap=pred_coding(hid)
        res[lbl]=(ab,ap); print(f"  {lbl}:  backprop={ab:.4f}   pred-coding={ap:.4f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    ok=all(ab>=0.86 and ap>=ab-0.04 for ab,ap in res.values())
    deg = res["2-hidden"][1] < res["1-hidden"][1]-0.02 and res["2-hidden"][1] < res["2-hidden"][0]-0.04
    if ok:
        print(f"JEP-19: PASS - local predictive coding matches backprop at BOTH depths on harder Fashion-MNIST",flush=True)
        print(f"(1-hidden {res['1-hidden'][1]:.3f} vs {res['1-hidden'][0]:.3f}; 2-hidden {res['2-hidden'][1]:.3f} vs",flush=True)
        print(f"{res['2-hidden'][0]:.3f}), all within 0.04. Substrate-compatible local learning scales with depth +",flush=True)
        print(f"harder data, trained on the AMD GPU. Whittington-Bogacz (2017) established, named as such.",flush=True)
    elif deg:
        print(f"JEP-19: PARTIAL - PC matches backprop at 1-hidden but DEGRADES at 2-hidden (2h PC",flush=True)
        print(f"{res['2-hidden'][1]:.3f} vs bp {res['2-hidden'][0]:.3f}) - the known depth limitation of PC's backprop",flush=True)
        print(f"approximation. Honest finding.",flush=True)
    else:
        print(f"JEP-19: PARTIAL/NULL - {res}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
