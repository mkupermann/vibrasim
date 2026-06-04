"""GEO-48b — symbolic keyword/regex intent router (intent is structural, not semantic)."""
import re
from run_geo48_routing import CLASSES


def route(q):
    ql=q.lower()
    if re.search(r"\b(how many|count|number of|headcount)\b",ql): return "COUNT"
    if re.search(r"\b(in 20\d\d|during 20\d\d|was .* on|did .* (join|run)|hired in|changed in)\b",ql): return "TEMPORAL"
    if re.search(r"\b(same .* as|share[sd]?|else on|teammates|colleagues|work with|list (people|everyone))\b",ql): return "JOIN"
    if re.search(r"\b(is there|does any|are there|anybody|anyone|any team)\b",ql): return "EXISTS"
    if re.search(r"\b(more|bigger|larger|older|taller|faster|senior to|first|earns more|than)\b",ql) and re.search(r"\bor\b|\bthan\b",ql): return "COMPARE"
    return "FACTOID"


def main():
    print("=== GEO-48b: symbolic keyword intent router ===", flush=True)
    tot=0;ok=0;miss=[]
    for cls,qs in CLASSES.items():
        for q in qs:
            tot+=1; p=route(q); ok+= int(p==cls)
            if p!=cls: miss.append((cls,p,q[:40]))
    print(f"  keyword-router intent accuracy = {ok/tot:.2f}  (n={tot}, vs geometric 0.56)", flush=True)
    if miss:
        for mm in miss[:6]: print(f"    miss: {mm}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok/tot>=0.85:
        print(f"GEO-48b: PASS - a simple SYMBOLIC keyword router classifies intent at {ok/tot:.2f}, far above geometric 0.56. Confirms: route by structure (keywords) symbolically, resolve content geometrically. Auto-dispatch works with the right (symbolic) signal.", flush=True)
    else:
        print(f"GEO-48b: PARTIAL - keyword router {ok/tot:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
