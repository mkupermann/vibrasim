"""show_binding — answer Michael's question: if 'Germany has politics' and 'Hungary has politics' share the SAME
'politics', they'd share the same weights, so learning 'this politics is corrupt' would smear onto BOTH. How does
the substrate keep them apart and learn like a human -- WITHOUT an LLM (the rule)?

Answer = role-filler BINDING (the substrate's own primitive, world/vsa.py: bind(a,b)=a*b, Hadamard). 'German
politics' is stored as bind(GERMANY, POLITICS) -- a DIFFERENT pattern from bind(HUNGARY, POLITICS) -- even though
both share POLITICS. So 'corrupt' attaches to the BOUND instance, not to bare 'politics'. This is exactly how the
brain avoids the 'binding problem' (superposition catastrophe): same concept, separate instances.

No transformer, no pretrained model -- only the substrate's VSA primitives. Run:
  PYTHONPATH=. .venv/Scripts/python.exe tools/show_binding.py
"""
import numpy as np
from world.vsa import rand_hv, bind, unbind, bundle, sim, CleanupMemory

D = 4096


def main():
    rng = np.random.default_rng(0)
    GERMANY, HUNGARY, POLITICS = (rand_hv(D, rng) for _ in range(3))
    CORRUPT, CLEAN = rand_hv(D, rng), rand_hv(D, rng)
    clean = CleanupMemory()                       # the 'dictionary' that maps a noisy vector back to a known word
    for name, v in [("GERMANY", GERMANY), ("HUNGARY", HUNGARY), ("POLITICS", POLITICS),
                    ("CORRUPT", CORRUPT), ("CLEAN", CLEAN)]:
        clean.add(name, v)

    print("=== Michael's case: German politics is corrupt, Hungarian politics is not ===\n")

    # ---- THE NAIVE WAY (what Michael feared): one shared 'politics' node ----
    # 'corrupt' gets attached to bare POLITICS -> both countries' politics read as corrupt. COLLISION.
    naive = bundle([bind(POLITICS, CORRUPT)])
    g_naive = clean.cleanup(unbind(naive, POLITICS))     # ask: German politics? (but politics is shared)
    h_naive = clean.cleanup(unbind(naive, POLITICS))     # ask: Hungarian politics? -> SAME query, SAME answer
    print("NAIVE (one shared 'politics' weight):")
    print(f"   German politics -> {g_naive} | Hungarian politics -> {h_naive}")
    print("   -> COLLISION: they share the weight, so both read the SAME. Cannot learn like a human.\n")

    # ---- THE SUBSTRATE WAY: BIND the instance ----
    gp = bind(GERMANY, POLITICS)                  # 'German politics' -- its OWN pattern
    hp = bind(HUNGARY, POLITICS)                  # 'Hungarian politics' -- a DIFFERENT pattern
    # store the facts: German politics IS corrupt; Hungarian politics IS clean
    mem = bundle([bind(gp, CORRUPT), bind(hp, CLEAN)])

    g_prop = clean.cleanup(unbind(mem, gp))       # ask: is German politics corrupt?
    h_prop = clean.cleanup(unbind(mem, hp))       # ask: is Hungarian politics corrupt?
    print("SUBSTRATE (bind the instance: German-politics is its OWN pattern):")
    print(f"   sim(German-politics, Hungarian-politics) = {sim(gp, hp):+.3f}   (~0 -> DIFFERENT patterns)")
    print(f"   German politics    -> {g_prop}")
    print(f"   Hungarian politics -> {h_prop}")
    print("   -> DISTINCT: 'corrupt' stuck to GERMANY's politics only. Hungary's is untouched.\n")

    # ---- and yet they SHARE the concept 'politics' (the human-like part) ----
    print("Both still SHARE the concept 'politics' (same concept, separate instances):")
    print(f"   unbind(German-politics, GERMANY) -> {clean.cleanup(unbind(gp, GERMANY))}")
    print(f"   unbind(Hungarian-politics, HUNGARY) -> {clean.cleanup(unbind(hp, HUNGARY))}")

    print("\nWHERE this lives: gp, hp, mem are numpy vectors in RAM (a few arrays), NOT files. The 'memory' is the")
    print("bundle vector `mem` -- one list of numbers holding BOTH facts at once, separable by WHICH key you unbind.")


if __name__ == "__main__":
    main()
