"""BET-143 — learn code fragments FROM SOURCES, recombine, and grow online."""
import json
from pathlib import Path
from world.codelearn import CodeLibrary

# --- a real source file the system reads to LEARN its primitive operations ---
SOURCE = """
def positive(xs):
    return [x for x in xs if x > 0]

def negative(xs):
    return [x for x in xs if x < 0]

def even(xs):
    return [x for x in xs if x % 2 == 0]

def odd(xs):
    return [x for x in xs if x % 2 == 1]

def squared(xs):
    return [x * x for x in xs]

def doubled(xs):
    return [2 * x for x in xs]

def total(xs):
    return sum(xs)

def largest(xs):
    return max(xs)

def smallest(xs):
    return min(xs)

def how_many(xs):
    return len(xs)
"""

# a SECOND source, ingested later, to test online growth (new op -> new ability)
SOURCE2 = """
def cubed(xs):
    return [x ** 3 for x in xs]
"""

# queries: compositions NEVER written as a whole function in the sources
# (query, expected reference function)
CASES = [
    ("the total of the squared positive", lambda xs: sum(x * x for x in xs if x > 0)),
    ("the largest of the doubled even", lambda xs: (lambda v: max(v) if v else None)([2 * x for x in xs if x % 2 == 0])),
    ("how many negative", lambda xs: len([x for x in xs if x < 0])),
    ("the smallest of the squared odd", lambda xs: (lambda v: min(v) if v else None)([x * x for x in xs if x % 2 == 1])),
    ("the total of the doubled positive", lambda xs: sum(2 * x for x in xs if x > 0)),
]
TESTS = [[3, -2, 4, -5, 6, 1, -1, 0, 7, -8], [1, 2, 3, 4, 5], [-3, -1, 2], [], [10, -10, 5, -5]]


def run_and_check(code, ref):
    if code is None:
        return False, False
    ns = {}
    try:
        exec(code, ns)
        for t in TESTS:
            if ns["f"](list(t)) != ref(list(t)):
                return True, False
        return True, True
    except Exception:
        return False, False


if __name__ == "__main__":
    print("=== BET-143: learn code fragments from sources + recombine ===", flush=True)
    lib = CodeLibrary()
    n = lib.learn_source(SOURCE)
    n_ops = len(set(lib.filters.values()) | set(lib.maps.values()) | set(lib.reducers.values()))
    print(f"  learned {len(lib.learned_funcs)} functions -> {n_ops} distinct operations", flush=True)
    print(f"   filters: {sorted(set(lib.filters.values()))}", flush=True)
    print(f"   maps   : {sorted(set(lib.maps.values()))}", flush=True)
    print(f"   reducers:{sorted(set(lib.reducers.values()))}", flush=True)

    correct = 0
    for q, ref in CASES:
        code = lib.generate(q)
        ran, ok = run_and_check(code, ref)
        correct += ok
        print(f"  [{'OK ' if ok else ('RUNS' if ran else 'FAIL')}] {q}", flush=True)

    # online growth: a query needing 'cubed' should FAIL before, SUCCEED after
    grow_q = "the largest of the cubed positive"
    grow_ref = lambda xs: (lambda v: max(v) if v else None)([x ** 3 for x in xs if x > 0])
    before = run_and_check(lib.generate(grow_q), grow_ref)[1]
    lib.learn_source(SOURCE2)
    after = run_and_check(lib.generate(grow_q), grow_ref)[1]
    print(f"  online growth: '{grow_q}' correct before/after new source: {before} -> {after}", flush=True)

    T143a = n_ops >= 8
    T143b = correct / len(CASES) >= 0.80
    T143c = correct >= 1   # all CASES are multi-op recombinations not present as whole funcs
    T143d = (not before) and after
    passed = T143a and T143b and T143c and T143d
    print("\n--- VERDICT ---", flush=True)
    print(f"T143a mined >=8 ops    : {T143a} ({n_ops})", flush=True)
    print(f"T143b recombine correct: {T143b} ({correct}/{len(CASES)})", flush=True)
    print(f"T143c new combinations : {T143c}", flush=True)
    print(f"T143d online growth    : {T143d} ({before} -> {after})", flush=True)
    verdict = ("PASS - learns operations FROM sources, recombines them into new correct "
               "code, and grows when given new sources") if passed else "NULL/partial"
    print(f"\nBET-143: {verdict}", flush=True)

    code = lib.generate("the total of the squared positive")
    print("\n  example (operations mined from source, recombined):", flush=True)
    print("\n".join("    " + l for l in code.split("\n")), flush=True)
    out = Path.home() / ".eqmod" / "bet" / "BET-143"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"n_ops": n_ops, "correct": correct, "total": len(CASES),
         "grow_before": before, "grow_after": after, "passed": passed}, indent=2))
    print("DONE", flush=True)
