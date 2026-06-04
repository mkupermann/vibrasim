"""JEP-149 - spatial reasoning + frames of reference. Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-149: spatial reasoning + perspective, target 100% ===", flush=True)
    e=UnderstandingEngine(seed=149)
    e.tell_spatial("cup","left","plate")
    e.tell_spatial("plate","left","fork")
    e.tell_spatial("lamp","above","table")
    res=[]; ck=lambda n,g,x: res.append((n,g==x,g,x))
    ck("cup left plate (direct)", e.spatial_holds("cup","left","plate"), True)
    ck("cup left fork (transitive)", e.spatial_holds("cup","left","fork"), True)
    ck("plate right cup (inverse)", e.spatial_holds("plate","right","cup"), True)
    ck("fork right cup (transitive inverse)", e.spatial_holds("fork","right","cup"), True)
    ck("cup NOT right plate (default view)", e.spatial_holds("cup","right","plate"), False)
    # PERSPECTIVE: from the opposite side, left<->right flip
    ck("from opposite view, cup is RIGHT of plate", e.spatial_holds("cup","right","plate",viewpoint="opposite"), True)
    ck("from opposite view, cup NOT left of plate", e.spatial_holds("cup","left","plate",viewpoint="opposite"), False)
    # above/below viewpoint-INVARIANT
    ck("lamp above table (default)", e.spatial_holds("lamp","above","table"), True)
    ck("lamp STILL above table from opposite view (invariant)", e.spatial_holds("lamp","above","table",viewpoint="opposite"), True)
    npass=0
    for n,ok,g,x in res:
        npass+=ok
        if not ok: print(f"   FAIL {n}: got {g} exp {x}", flush=True)
        else: print(f"   [ok] {n}", flush=True)
    print(f"\n   spatial battery: {npass}/{len(res)} = {npass/len(res)*100:.0f}%", flush=True)
    print("JEP-149: PASS - spatial transitive + inverse + perspective transform (allocentric left/right flip)." if npass==len(res)
          else f"JEP-149: NOT YET - {npass}/{len(res)}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
