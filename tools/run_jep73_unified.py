"""JEP-73 - unified system: learn Fashion-MNIST concepts -> whiten -> structured composition (relations+analogy)."""
import numpy as np
rng=np.random.default_rng(73)
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,784).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
means=np.array([X[y==k].mean(0) for k in range(10)])
D=512
# learn concepts -> WHITEN -> embed in D (the decorrelation bridge)
mu=means.mean(0); Mc=means-mu; U,s,Vt=np.linalg.svd(Mc,full_matrices=False)
white=U[:,:10]  # decorrelated 10-d
Rp=rng.normal(0,1,(10,D)); V=white@Rp; V=V/(np.linalg.norm(V,axis=1,keepdims=True)+1e-9)  # 10 concept vectors in D
ABOVE=rng.normal(0,1/np.sqrt(D),D)
# a transformation relation (e.g. 'worn-with' mapping) as a unitary operator for analogy
def unitary():
    ph=rng.uniform(0,2*np.pi,D); ph[0]=0
    if D%2==0: ph[D//2]=0
    ph[D//2+1:]=-ph[1:D//2][::-1] if D%2==0 else -ph[1:(D+1)//2][::-1]
    return np.real(np.fft.ifft(np.exp(1j*ph)))
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def cleanup(v): return int(np.argmax([cos(v,V[o]) for o in range(10)]))
def main():
    print("=== JEP-73: unified grounded+structured system on real Fashion-MNIST concepts ===", flush=True)
    # (a) relational query on learned concepts
    rok=tot=0
    for _ in range(400):
        a,b=rng.choice(10,2,replace=False)
        scene=cconv(V[a],cconv(ABOVE,V[b]))
        rok+=int(cleanup(ccorr(scene,cconv(ABOVE,V[b])))==a); tot+=1
    ra=rok/tot
    print(f"  relational query ('what is above Y') on LEARNED concepts = {ra:.3f}", flush=True)
    # (b) one-shot analogy on learned concepts (unitary transformation)
    aok=atot=0
    for _ in range(400):
        T=unitary(); a,c=rng.choice(10,2,replace=False)
        A=V[a]; B=cconv(T,A); C=V[c]; Dtrue=cconv(T,C)
        Tinf=ccorr(B,A); Dpred=cconv(Tinf,C)
        # cleanup target among concepts: nearest to Dtrue (the analogy answer in concept space)
        aok+=int(cleanup(Dpred)==cleanup(Dtrue)); atot+=1
    aa=aok/atot
    print(f"  one-shot analogy (A:B::C:?) on LEARNED concepts = {aa:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ra>=0.9 and aa>=0.9:
        print(f"JEP-73: PASS - the UNIFIED grounded+structured system works on REAL data: concepts LEARNED from", flush=True)
        print(f"Fashion-MNIST, DECORRELATED (the JEP-72 bridge), then composed STRUCTURALLY - relational queries", flush=True)
        print(f"({ra:.2f}) and one-shot analogy ({aa:.2f}) on the learned concepts. The grounding thread (form concepts", flush=True)
        print(f"from perception) and the structure thread (VSA composition) UNIFY into one pipeline via decorrelation.", flush=True)
        print(f"Established methods (clustering, PCA-whitening, VSA/HRR), named as such - the unified ARCHITECTURE is", flush=True)
        print(f"the step, no new method.", flush=True)
    else:
        print(f"JEP-73: PARTIAL/NULL - relational {ra:.2f}, analogy {aa:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
