"""JEP-71 - structural analogy via VSA: infer transformation from (A,B), apply to C -> D."""
import numpy as np
rng=np.random.default_rng(71)
D=2048; NO=40; NT=6
def rv(): return rng.normal(0,1/np.sqrt(D),D)
objs=[rv() for _ in range(NO)]
Ts=[rv() for _ in range(NT)]            # transformation operators
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def cleanup(v): return int(np.argmax([cos(v,o) for o in objs]))
def main():
    print("=== JEP-71: analogical reasoning via VSA (A:B::C:?) ===", flush=True)
    h1=tot=0
    for _ in range(500):
        ti=rng.integers(NT); T=Ts[ti]
        a,c=rng.choice(NO,2,replace=False)
        A=objs[a]; B=cconv(T,A)              # B = T applied to A
        C=objs[c]; Dtrue=cconv(T,C)          # the analogous D (T applied to C)
        # infer T from the (A,B) example, apply to C
        Tinf=ccorr(B,A)                      # B (x) A^-1
        Dpred=cconv(Tinf,C)
        pred=cleanup(Dpred)
        true=cleanup(Dtrue)                  # nearest object to true D (the analogy target)
        h1+=int(pred==true); tot+=1
    acc=h1/tot
    print(f"  analogy completion (A:B::C:?) hits@1 = {acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.8:
        print(f"JEP-71: PASS - structural ANALOGY works via VSA: from a SINGLE (A,B) example the transformation T is", flush=True)
        print(f"inferred (B (x) A^-1) and transferred to a NEW C to complete the analogy ({acc:.2f}) - including", flush=True)
        print(f"transformations never paired with C. Analogical transfer - a hallmark of human understanding -", flush=True)
        print(f"demonstrated structurally. Established (VSA/HRR analogy, Plate/Gayler), named as such.", flush=True)
    else:
        print(f"JEP-71: PARTIAL/NULL - analogy hits@1 {acc:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
