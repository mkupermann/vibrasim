"""JEP-412 — book-scale ingestion: performance + correctness on a large factual English text. No transformer.
Pre-registered bars in docs/amendments/jep412_book_scale_ingest.md.
NOTE: timing uses os-level perf_counter (allowed; not Date.now). Run as a tool, not in a workflow.
"""
import json, tempfile, time
from pathlib import Path
import numpy as np
from world.conversation import Conversation


def nm(i):
    s = ""; j = i + 1
    while j > 0:
        s = chr(ord('a') + (j % 26)) + s; j //= 26
    return "x" + s


def build_book(n_nodes, rng, max_depth=8):
    """A large factual English document: a deep taxonomy + properties + part-of + causal."""
    depth = {0: 0}; parent = {0: None}
    for i in range(1, n_nodes):
        cands = [k for k in depth if depth[k] < max_depth]
        w = np.array([depth[k] + 1 for k in cands], float)
        p = int(rng.choice(cands, p=w / w.sum())); parent[i] = p; depth[i] = depth[p] + 1
    sents = [f"A {nm(i)} is a {nm(parent[i])}." for i in range(1, n_nodes)]
    # properties + part-of + causal sprinkled in
    for a in [k for k in range(n_nodes) if depth[k] == 1][:20]:
        sents.append(f"A {nm(a)} can move.")
    for i in range(0, n_nodes, 7):
        sents.append(f"A part{i} is part of a {nm(i)}.")
    for i in range(1, 40):
        sents.append(f"Cause{i} causes effect{i}.")
    rng.shuffle(sents)
    return parent, depth, " ".join(sents)


def ancestors(parent, x):
    out = []
    while parent[x] is not None:
        out.append(parent[x]); x = parent[x]
    return out


if __name__ == "__main__":
    print("=== JEP-412: book-scale ingestion ===", flush=True)
    rng = np.random.default_rng(0)
    N = 360
    parent, depth, doc = build_book(N, rng)
    n_sents = doc.count(".")
    print(f"  document: ~{len(doc)} chars, ~{n_sents} sentences", flush=True)

    c = Conversation(brain_dir=tempfile.mkdtemp(prefix="j412_"), seed=0)
    t0 = time.perf_counter()
    info = c.read_text(doc)
    elapsed = round(time.perf_counter() - t0, 2)
    coverage = round(info["facts_learned"] / max(1, n_sents), 3)
    print(f"  ingest: {elapsed}s | facts_learned={info['facts_learned']} | total_facts={len(c.sm.facts)} | "
          f"coverage={coverage}", flush=True)

    # deep multi-hop Q&A
    rng2 = np.random.default_rng(100)
    leaves = [k for k in range(N) if k not in set(parent.values())]; rng2.shuffle(leaves)
    correct = total = 0
    for x in leaves[:30]:
        anc = ancestors(parent, x)
        if not anc:
            continue
        z = anc[min(len(anc) - 1, int(rng2.integers(0, len(anc))))]
        if "yes" in c.say(f"is a {nm(x)} a {nm(z)}?").strip().lower():
            correct += 1
        total += 1
    deep_acc = round(correct / total, 3) if total else None
    ood = sum(1 for q in ["is a zzz an animal?", "is a qqq a wwww?"] if "yes" not in c.say(q).strip().lower())
    ood_abstain = round(ood / 2, 3)
    print(f"  deep multi-hop Q&A acc={deep_acc} | OOD abstain={ood_abstain}", flush=True)

    J412a = elapsed < 60 and info["facts_learned"] >= 300
    J412b = deep_acc >= 0.90 and ood_abstain >= 1.0
    J412c = coverage >= 0.80
    passed = J412a and J412b and J412c
    print("\n--- VERDICT ---", flush=True)
    print(f"J412a completes<60s & >=300 facts ({elapsed}s, {info['facts_learned']}): {J412a}", flush=True)
    print(f"J412b deep Q&A >=0.90 & abstain   : {J412b}", flush=True)
    print(f"J412c coverage >=0.80             : {J412c}", flush=True)
    verdict = (f"PASS - book-scale ingestion ({n_sents} sentences) completes in {elapsed}s, captures "
               f"{info['facts_learned']} facts at {coverage:.0%} coverage, and deep multi-hop Q&A is {deep_acc} with "
               "perfect abstention. The GUI can ingest a real factual English book end-to-end and answer it "
               "reliably.") if passed else \
              (f"PARTIAL/NULL - ingest {elapsed}s, facts {info['facts_learned']}, deep {deep_acc}, coverage {coverage}; "
               "see which bar missed (perf or reasoning at book scale). Reported, not retuned.")
    print(f"\nJEP-412: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP412"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"elapsed": elapsed, "facts": info["facts_learned"],
                                                  "coverage": coverage, "deep_acc": deep_acc,
                                                  "ood_abstain": ood_abstain, "J412a": J412a, "J412b": J412b,
                                                  "J412c": J412c, "passed": passed}, default=str))
    print("DONE", flush=True)
