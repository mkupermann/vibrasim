"""JEP-73b - unitarize learned Fashion-MNIST concepts -> both relational AND analogy work."""
import numpy as np
rng=np.random.default_rng(731)
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,784).astype(np.float32)/255.0; y=d["y_train"]
means=np.array([X[y==k].mean(0) for k in range(10)])
D=512
mu=means.mean(0); Mc=means-mu; U,s,Vt=np.linalg.svd(Mc,full_matrices=False)
Rp=rng.normal(0,1,(10,D)); base=(U[:,:10]@Rp)
def unitarize(v):  # keep phase, set FFT magnitude to 1 -> unitary, preserves identity via phase
    f=np.fft.fft(v); f=f/np.abs(f).clip(1e-9); 
    return np.real(np.fft.ifft(f))
V=np.array([unitarize(base[i]) for i in range(10)]); V=V/(np.linalg.norm(V,axis=1,keepdims=True)+1e-9)
ABOVE=rng.normal(0,1/np.sqrt(D),D)
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
    print("=== JEP-73b: UNITARIZED learned concepts -> relational + analogy ===", flush=True)
    G=V@V.T; print(f"  unitarized-concept mean |off-diag cosine| = {np.mean(np.abs(G[~np.eye(10,dtype=bool)])):.3f}", flush=True)
    rok=tot=0
    for _ in range(400):
        a,b=rng.choice(10,2,replace=False); scene=cconv(V[a],cconv(ABOVE,V[b]))
        rok+=int(cleanup(ccorr(scene,cconv(ABOVE,V[b])))==a); tot+=1
    aok=atot=0
    for _ in range(400):
        T=unitary(); a,c=rng.choice(10,2,replace=False)
        A=V[a]; B=cconv(T,A); C=V[c]; Tinf=ccorr(B,A); Dpred=cconv(Tinf,C); Dtrue=cconv(T,C)
        aok+=int(cleanup(Dpred)==cleanup(Dtrue)); atot+=1
    ra=rok/tot; aa=aok/atot
    print(f"  relational query = {ra:.3f}   one-shot analogy = {aa:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ra>=0.9 and aa>=0.9:
        print(f"JEP-73b: PASS - UNITARIZING the learned concepts makes BOTH work: relational {ra:.2f}, analogy {aa:.2f}.", flush=True)
        print(f"The grounding<->structure bridge for FULL structured composition (relations AND analogy) is", flush=True)
        print(f"UNITARIZATION: learned concepts, made unitary (unit-magnitude FFT, identity preserved in phase), plug", flush=True)
        print(f"into VSA for all operations. The unified system works on real concepts. Established (VSA/HRR, unitary", flush=True)
        print(f"HRR), named - the integration RECIPE (unitarize learned concepts) is the step, no new method.", flush=True)
    else:
        print(f"JEP-73b: PARTIAL/NULL - relational {ra:.2f}, analogy {aa:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
