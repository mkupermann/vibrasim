"""visualize — the durable brain DRAWS what it knows (Michael's teaching rule #3: visual aids).

Renders the stored is-a taxonomy + properties as a hierarchy image. Pure plotting of the substrate's own facts —
no neural net, no transformer.
"""
import os


def _isa_edges(mem):
    return [(a, b) for (a, r, b) in mem.facts if r == "isa"]


def _depths(edges):
    """Longest distance from a root (no outgoing is-a) to each node; cycle-safe."""
    parents = {}
    for c, p in edges:
        parents.setdefault(c, []).append(p)
    nodes = set([x for e in edges for x in e])
    depth = {}

    def d(n, seen):
        if n in depth:
            return depth[n]
        if n in seen or n not in parents:
            return 0
        depth[n] = 1 + max((d(p, seen | {n}) for p in parents[n]), default=0)
        return depth[n]

    for n in nodes:
        d(n, set())
    for n in nodes:
        depth.setdefault(n, 0)
    return depth


def draw_knowledge(mem, path=None, title="What I know"):
    """Render the is-a hierarchy + properties to a PNG. Returns the path (or None if nothing to draw / no mpl)."""
    edges = _isa_edges(mem)
    if not edges:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    if path is None:
        path = os.path.join(os.path.expanduser("~"), ".eqmod", "brain", "knowledge.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    depth = _depths(edges)
    maxd = max(depth.values()) if depth else 0
    # group nodes by depth, spread on x
    by_depth = {}
    for n, dd in depth.items():
        by_depth.setdefault(dd, []).append(n)
    pos = {}
    for dd, ns in by_depth.items():
        ns = sorted(ns)
        for i, n in enumerate(ns):
            x = (i + 1) / (len(ns) + 1)
            pos[n] = (x, maxd - dd)            # roots (high depth) at top

    props = {}
    for (s, r, o) in mem.facts:
        if r == "hasprop":
            props.setdefault(s, []).append(o)

    fig, ax = plt.subplots(figsize=(max(7, len(by_depth.get(0, [])) * 1.2 + 4), 1.6 * (maxd + 1) + 2))
    for c, p in edges:
        if c in pos and p in pos:
            x1, y1 = pos[c]; x2, y2 = pos[p]
            ax.annotate("", xy=(x2, y2 - 0.08), xytext=(x1, y1 + 0.08),
                        arrowprops=dict(arrowstyle="->", color="#888", lw=1.2))
    for n, (x, y) in pos.items():
        label = n + (f"\n({', '.join(props[n][:3])})" if n in props else "")
        ax.text(x, y, label, ha="center", va="center", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc="#e8f0fe", ec="#06c"))
    ax.set_xlim(0, 1); ax.set_ylim(-0.6, maxd + 0.8); ax.axis("off")
    ax.set_title(title + f"  ({len(set([x for e in edges for x in e]))} concepts, {len(edges)} is-a links)")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path
