"""JEP-91 - grounded understanding: parse->ground(perception)->bind+closure->comprehension from a scene."""
import numpy as np
rng=np.random.default_rng(91); FD=32; DIM=2048
CONCEPTS=["poodle","collie","dog","cat","mouse","salmon","fish","animal","living_thing"]
proto={c:rng.normal(0,1,FD) for c in CONCEPTS}
parents={"poodle":"dog","collie":"dog","dog":"animal","cat":"animal","salmon":"fish","fish":"animal","animal":"living_thing"}
_v={}
def vec(w):
    if w not in _v: _v[w]=rng.normal(0,1/np.sqrt(DIM),DIM)
    return _v[w]
SUBJ,REL,OBJ=(rng.normal(0,1/np.sqrt(DIM),DIM) for _ in range(3))
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
def ground(feat):  # perception: nearest prototype
    return min(CONCEPTS, key=lambda c: np.linalg.norm(feat-proto[c]))
def anc(x):
    out=set(); seen=set()
    while x in parents and x not in seen: seen.add(x); x=parents[x]; out.add(x)
    return out
fact=lambda s,r,o: cconv(SUBJ,vec(s))+cconv(REL,vec(r))+cconv(OBJ,vec(o))
def main():
    print("=== JEP-91: grounded understanding - comprehension from PERCEPTION (symbol grounding) ===",flush=True)
    SIG=0.6
    # (i) grounding accuracy under noise
    trials=400; ok=0
    for _ in range(trials):
        c=rng.choice(CONCEPTS); feat=proto[c]+rng.normal(0,SIG,FD); ok+=int(ground(feat)==c)
    gacc=ok/trials
    # (ii-A) same-bag truth from a grounded scene
    sceneA=[("dog","chases","cat"),("cat","eats","mouse"),("salmon","swims","fish")]
    A=[(("dog","chases","cat"),("cat","chases","dog")),(("cat","eats","mouse"),("mouse","eats","cat"))]
    okA=0
    for (t,f) in A:
        # perceive the scene (noisy features), ground, build fact memory
        mem=[]
        for s,r,o in sceneA:
            gs=ground(proto[s]+rng.normal(0,SIG,FD)); go=ground(proto[o]+rng.normal(0,SIG,FD))
            mem.append(fact(gs,r,o if go not in CONCEPTS else go))
        st=max(cos(fact(*t),m) for m in mem); sf=max(cos(fact(*f),m) for m in mem)
        okA+=int(st>sf)
    accA=okA/len(A)
    # (ii-B) grounded multi-hop: perceive entity -> ground -> IS-A closure
    Bpos=[("poodle","animal"),("poodle","living_thing"),("collie","living_thing"),("salmon","animal")]
    Bneg=[("poodle","fish"),("salmon","dog"),("cat","fish"),("fish","poodle")]
    def grounded_isa(cname,cat):
        g=ground(proto[cname]+rng.normal(0,SIG,FD))  # perceive then ground
        return cat in anc(g)
    accB=(sum(int(grounded_isa(x,c)) for x,c in Bpos)+sum(int(not grounded_isa(x,c)) for x,c in Bneg))/(len(Bpos)+len(Bneg))
    print(f"   (i)  perceptual grounding accuracy (sigma={SIG}) = {gacc:.3f}",flush=True)
    print(f"   (ii-A) grounded same-bag truth                  = {accA:.3f}",flush=True)
    print(f"   (ii-B) grounded multi-hop IS-A                   = {accB:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if gacc>=0.90 and accA>=0.90 and accB>=0.90:
        print(f"JEP-91: PASS - the understanding machinery works GROUNDED in perception: nouns recognized from noisy",flush=True)
        print(f"features ({gacc:.2f}), then the SAME parse->bind+closure answers same-bag truth ({accA:.2f}) and grounded",flush=True)
        print(f"multi-hop inference ({accB:.2f}) from a PERCEPTUAL scene, not text symbols. Symbol grounding closed on the",flush=True)
        print(f"understanding pipeline. Established (VSA, prototype perception, closure), named; no novelty.",flush=True)
    else:
        print(f"JEP-91: NULL/PARTIAL - ground={gacc:.2f}, A={accA:.2f}, B={accB:.2f}. Recorded honestly.",flush=True)
    print("HONEST BOUND: prototypes given/learned-from-features (JEP-54..63); toy perception; relation labels given.",flush=True)
    print("Learning concepts AND relations from raw embodied experience is the open frontier.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
