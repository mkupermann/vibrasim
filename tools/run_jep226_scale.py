"""JEP-226 - large-scale multi-domain validation: hundreds of concepts/facts across ALL domains, correctness + speed.
NOTE: the fixed-relation extractors use an [a-z]-only concept regex (they REJECT alphanumeric names like 'covid19' -
a genuine limitation), so this test uses LETTER-only concept names (3-letter base-26 codes)."""
import time, string
from itertools import product
from world.understanding import UnderstandingEngine
def names(n, pre=""):
    return [pre + "".join(t) for t in product(string.ascii_lowercase, repeat=3)][:n]
def main():
    print("=== JEP-226: large-scale multi-domain (letter-only names) ===", flush=True)
    e = UnderstandingEngine(seed=226)
    C = names(200); P = names(50, "p"); E2 = names(50, "e"); B = names(50, "b")
    T = names(50, "t"); N = names(50, "n"); CI = names(30, "x"); CO = names(30, "y")
    lines = []
    for i in range(199): lines.append(f"A {C[i]} is a {C[i+1]}.")
    for i in range(49): lines.append(f"A {P[i]} is part of a {P[i+1]}.")
    for i in range(49): lines.append(f"A {E2[i]} causes an {E2[i+1]}.")
    for i in range(49): lines.append(f"A {B[i]} is bigger than a {B[i+1]}.")
    for i in range(49): lines.append(f"The {T[i]} happened before the {T[i+1]}.")
    for i in range(50): lines.append(f"A {N[i]} has {i%9+1} legs.")
    for i in range(30): lines.append(f"{CI[i].capitalize()} is the capital of {CO[i].capitalize()}.")
    passage = " ".join(lines)
    t0 = time.time(); out = e.read(passage); t_read = time.time()-t0
    print(f"read {len(lines)} sentences in {t_read*1000:.0f}ms -> is_a {out['is_a']}, part {out['part_of']}, "
          f"causal {out['causal']}, num {out.get('numeric')}, cmp {out.get('comparison')}, "
          f"temporal {out.get('temporal')}, open {out.get('open')}", flush=True)
    t0 = time.time()
    checks = [
        ("deep is-a (200-hop)", e.is_a(C[0], C[199]), True),
        ("part-of (50-hop)", e.part_of(P[0], P[49]), True),
        ("causal (50-hop)", e.causes_effect(E2[0], E2[49]), True),
        ("comparison (50-hop)", e._order_holds("bigger", B[0], B[49]), True),
        ("temporal (50-hop)", e._order_holds("before", T[0], T[49]), True),
        ("numeric", e.respond(f"how many legs does a {N[7]} have?") == f"A {N[7]} has 8 legs.", True),
        ("open relation", e.relation_true(CI[5], "is capital of", CO[5]), True),
        ("NEG (reverse is-a)", e.is_a(C[199], C[0]), False),
    ]
    t_query = time.time()-t0
    ok = sum(1 for _, g, exp in checks if g == exp)
    for d, g, exp in checks: print(f"  [{'OK' if g == exp else 'XX'}] {d}: {g}", flush=True)
    print(f"\n{ok}/{len(checks)} correct; {len(checks)} queries (incl 200-hop) in {t_query*1000:.0f}ms; "
          f"KB={len(e.parents)} is-a concepts", flush=True)
    print("DONE", flush=True)
if __name__ == "__main__":
    main()
