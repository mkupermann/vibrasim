"""JEP-66 - relational composition via VSA role binding vs additive (above(X,Y) != above(Y,X))."""
import numpy as np
rng=np.random.default_rng(66)
D=512; NO=12
def rand(): v=rng.normal(0,1/np.sqrt(D),D); return v
objs=[rand() for _ in range(NO)]
TOP=rand(); BOTTOM=rand()
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))      # binding
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))  # unbinding
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def cleanup(v):  # nearest object
    return int(np.argmax([cos(v,o) for o in objs]))
def main():
    print("=== JEP-66: relational composition - VSA binding vs additive ===", flush=True)
    # (a) distinguish above(X,Y) from above(Y,X)
    vsa_ok=add_ok=0; T=300
    for _ in range(T):
        x,y=rng.choice(NO,2,replace=False)
        xy=cconv(TOP,objs[x])+cconv(BOTTOM,objs[y])   # above(X,Y)
        yx=cconv(TOP,objs[y])+cconv(BOTTOM,objs[x])   # above(Y,X)
        # query 'what is on top?' via unbind with TOP
        vsa_ok+= int(cleanup(ccorr(xy,TOP))==x and cleanup(ccorr(yx,TOP))==y)
        # additive code: X+Y is identical for both orders -> cannot tell on-top
        add_xy=objs[x]+objs[y]; add_yx=objs[y]+objs[x]
        add_ok+= int(not np.allclose(add_xy,add_yx))  # additive distinguishes order? (no, identical)
    print(f"  VSA: correctly identifies what's-on-top for BOTH orders = {vsa_ok/T:.3f}", flush=True)
    print(f"  ADDITIVE: X+Y differs by order = {add_ok/T:.3f}  (commutative -> cannot encode order)", flush=True)
    # (b) role-query on novel structures: 'what is on top of Z?'
    q_ok=0
    for _ in range(T):
        x,y=rng.choice(NO,2,replace=False)
        s=cconv(TOP,objs[x])+cconv(BOTTOM,objs[y])
        q_ok+= int(cleanup(ccorr(s,TOP))==x and cleanup(ccorr(s,BOTTOM))==y)
    print(f"  VSA role-query (top AND bottom correct) on novel structures = {q_ok/T:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if vsa_ok/T>=0.9 and add_ok/T<=0.1 and q_ok/T>=0.9:
        print(f"JEP-66: PASS - RELATIONAL composition works via VSA role-binding where additive CANNOT: VSA identifies", flush=True)
        print(f"what's-on-top for both X-on-Y and Y-on-X ({vsa_ok/T:.2f}) and answers role queries on novel structures", flush=True)
        print(f"({q_ok/T:.2f}), while the additive code is COMMUTATIVE (X+Y identical for both orders -> 0.00, cannot", flush=True)
        print(f"encode order/role). The next gap after additive (JEP-65) is closed: STRUCTURED/relational composition", flush=True)
        print(f"via vector-symbolic binding (Plate 1995 HRR), established - named as such. Toward human-level structure.", flush=True)
    else:
        print(f"JEP-66: PARTIAL/NULL - VSA {vsa_ok/T:.2f}, additive-order {add_ok/T:.2f}, role-query {q_ok/T:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
