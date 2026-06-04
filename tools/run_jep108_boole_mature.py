"""JEP-108 - run the mature UnderstandingEngine parser over REAL Boole sentences; measure the parse gate."""
from collections import Counter
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-108: mature engine on REAL Boole prose (re-measure the parse gate) ===", flush=True)
    sents=open("data/sources/boole_clean.txt",encoding="utf-8").read().split("\n")
    e=UnderstandingEngine(seed=108)
    kinds=Counter(); parsed=[]
    for s in sents:
        t=e.tell(s); kinds[t[0]]+=1
        if t[0]!="none" and len(parsed)<25: parsed.append((t, s[:70]))
    n=len(sents); facts=n-kinds["none"]
    print(f"   sentences: {n}; parsed into facts: {facts} ({facts/n*100:.1f}%); none: {kinds['none']}", flush=True)
    print(f"   by kind: {dict(kinds)}", flush=True)
    print("   sample parses:", flush=True)
    for t,s in parsed[:18]:
        print(f"      {t[0]:>8} {t[1:]!s:38} <- {s!r}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    pct=facts/n*100
    if pct<5:
        print(f"JEP-108: PASS (prediction HIT) - STILL SPARSE: only {pct:.1f}% of Boole parses into facts. The mature",flush=True)
        print(f"engine's grammar is for SIMPLE declaratives; Boole's dense argumentative/mathematical prose mostly",flush=True)
        print(f"returns none. The parse gate PERSISTS - more engine capability did not crack real prose. Honest.",flush=True)
    else:
        print(f"JEP-108: prediction MISS - {pct:.1f}% parsed (predicted <5%). The mature engine does better than expected.",flush=True)
    print("   And many 'parses' will be SPURIOUS (the simple grammar mis-fitting complex sentences) - parse RATE is",flush=True)
    print("   not parse QUALITY; real-prose understanding needs robust parsing the no-transformer rule forbids learning.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
