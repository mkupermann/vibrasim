"""JEP-71b - structural analogy via VSA with UNITARY vectors (exact unbinding)."""
import numpy as np
rng=np.random.default_rng(711)
D=1024; NO=40; NT=6
def unitary():
    ph=rng.uniform(0,2*np.pi,D); ph[0]=0
    if D%2==0: ph[D//2]=0
    # enforce conjugate symmetry for real vector
    ph[D//2+1:]=-ph[1:D//2][::-1] if D%2==0 else -ph[1:(D+1)//2][::-1]
    return np.real(np.fft.ifft(np.exp(1j*ph)))
objs=[unitary() for _ in range(NO)]
Ts=[unitary() for _ in range(NT)]
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def cleanup(v): return int(np.argmax([cos(v,o) for o in objs]))
def main():
    print("=== JEP-71b: analogy via VSA with UNITARY vectors ===", flush=True)
    h1=tot=0
    for _ in range(500):
        T=Ts[rng.integers(NT)]; a,c=rng.choice(NO,2,replace=False)
        A=objs[a]; B=cconv(T,A); C=objs[c]; Dtrue=cconv(T,C)
        Tinf=ccorr(B,A); Dpred=cconv(Tinf,C)
        h1+=int(cleanup(Dpred)==cleanup(Dtrue)); tot+=1
    acc=h1/tot
    print(f"  analogy completion (A:B::C:?) hits@1 = {acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.8:
        print(f"JEP-71b: PASS - structural ANALOGY works via VSA with unitary vectors: from a SINGLE (A,B) example", flush=True)
        print(f"the transformation is inferred and transferred to a NEW C ({acc:.2f}) - one-shot analogical transfer,", flush=True)
        print(f"a hallmark of human understanding, demonstrated structurally. JEP-71 NULL was non-unitary vectors", flush=True)
        print(f"(noisy unbinding). Established (VSA/HRR analogy with unitary HRR, Plate), named as such.", flush=True)
    else:
        print(f"JEP-71b: PARTIAL/NULL - analogy hits@1 {acc:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
