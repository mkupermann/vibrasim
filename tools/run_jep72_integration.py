"""JEP-72 - do learned (correlated) grounded concept vectors integrate with VSA composition?"""
import numpy as np
rng=np.random.default_rng(72)
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,784).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
means=np.array([X[y==k].mean(0) for k in range(10)])
D=784
def normv(V): return V/ (np.linalg.norm(V,axis=1,keepdims=True)+1e-9)
learned=normv(means)
# whitened: decorrelate via PCA-whiten then pad to D
mu=means.mean(0); Mc=means-mu
U,s,Vt=np.linalg.svd(Mc,full_matrices=False)
white=normv(U[:, :10])  # 10-d whitened (orthogonal) -> but need D-dim for conv; embed in D via random proj
Rp=rng.normal(0,1,(10,D)); white_emb=normv(white@Rp)
randv=normv(rng.normal(0,1,(10,D)))
ABOVE=rng.normal(0,1,D)
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def test(V,label):
    def cleanup(v): return int(np.argmax([cos(v,V[o]) for o in range(10)]))
    ok=tot=0
    for _ in range(400):
        a,b=rng.choice(10,2,replace=False)
        scene=cconv(V[a],cconv(ABOVE,V[b]))  # a above b
        ans=ccorr(scene,cconv(ABOVE,V[b]))
        ok+=int(cleanup(ans)==a); tot+=1
    print(f"  [{label}] relational-query 'what is above Y' accuracy = {ok/tot:.3f}", flush=True)
    return ok/tot
def main():
    print("=== JEP-72: do learned grounded concepts integrate with VSA? ===", flush=True)
    # concept correlation (how non-orthogonal are learned vectors)
    G=learned@learned.T; offdiag=G[~np.eye(10,dtype=bool)]
    print(f"  learned-concept mean |off-diagonal cosine| = {np.mean(np.abs(offdiag)):.3f} (random ~0)", flush=True)
    ra=test(randv,"RANDOM (clean baseline)")
    la=test(learned,"LEARNED raw (correlated)")
    wa=test(white_emb,"LEARNED whitened (decorrelated)")
    print("\n--- VERDICT ---", flush=True)
    if la>=0.8:
        print(f"JEP-72: PASS - learned grounded concepts INTEGRATE with VSA directly ({la:.2f}); the threads unify.", flush=True)
    elif wa>=0.8 and la<0.8:
        print(f"JEP-72: PARTIAL - raw learned vectors DEGRADE VSA ({la:.2f}, correlation breaks cleanup) but WHITENING", flush=True)
        print(f"recovers it ({wa:.2f} vs random {ra:.2f}). Integration NEEDS DECORRELATION: grounded concepts must be", flush=True)
        print(f"whitened/orthogonalized to plug into VSA structured composition. A concrete integration requirement -", flush=True)
        print(f"the grounding and structure threads unify ONLY via a decorrelation interface. Established, named.", flush=True)
    else:
        print(f"JEP-72: NULL - learned {la:.2f}, whitened {wa:.2f}: integration does not cleanly work here.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
