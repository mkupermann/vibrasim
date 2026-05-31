"""EQMOD — learn code FRAGMENTS from real source files, then recombine them.

Extends the knowledge system from retrieval to COMPOSITION that is learned from
sources: read Python source, mine the primitive operations actually present (filters,
maps, reducers) with trigger words taken from the function names, and recombine them on
demand into NEW code that was never written as a whole. Ingesting a new source file
GROWS what can be generated (online source-learning).

NO LLM, NO transformer. Honest provenance: AST-based fragment mining + rule/grammar
program synthesis (inductive program synthesis / library learning), decades old.
"""
from __future__ import annotations

import ast

# tokens too generic to be useful triggers
_STOP = {"numbers", "number", "the", "of", "a", "an", "list", "xs", "values",
         "value", "items", "get", "compute", "all", "elements", "nums", "func", "fn"}

_REDUCER_BUILTINS = {
    "sum": "sum(xs)",
    "max": "max(xs) if xs else None",
    "min": "min(xs) if xs else None",
    "len": "len(xs)",
}


class _Rename(ast.NodeTransformer):
    def __init__(self, old):
        self.old = old

    def visit_Name(self, node):
        if node.id == self.old:
            node.id = "x"
        return node


def _name_tokens(name: str):
    raw = name.replace("__", "_").replace("-", "_").split("_")
    out = []
    for part in raw:
        # split simple camelCase
        cur = ""
        for ch in part:
            if ch.isupper() and cur:
                out.append(cur)
                cur = ch.lower()
            else:
                cur += ch.lower()
        if cur:
            out.append(cur)
    return [t for t in out if t and t not in _STOP]


class CodeLibrary:
    """Mined fragments: filters {trigger->predicate}, maps {trigger->expr},
    reducers {trigger->reduce-expression}. Triggers come from source function names."""

    def __init__(self):
        self.filters: dict[str, str] = {}
        self.maps: dict[str, str] = {}
        self.reducers: dict[str, str] = {}
        self.learned_funcs: list[str] = []

    # --- ingestion / mining --------------------------------------------------
    def learn_source(self, source: str) -> int:
        tree = ast.parse(source)
        n_before = len(self.filters) + len(self.maps) + len(self.reducers)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                self._mine_function(node)
        return (len(self.filters) + len(self.maps) + len(self.reducers)) - n_before

    def _register(self, table, triggers, value):
        for t in triggers:
            table.setdefault(t, value)

    def _mine_function(self, fn: ast.FunctionDef):
        triggers = _name_tokens(fn.name)
        if not triggers:
            return
        self.learned_funcs.append(fn.name)
        for sub in ast.walk(fn):
            # list comprehensions -> map expr and/or filter predicate(s)
            if isinstance(sub, (ast.ListComp, ast.GeneratorExp)):
                gen = sub.generators[0]
                if isinstance(gen.target, ast.Name):
                    var = gen.target.id
                    # filter predicates
                    for cond in gen.ifs:
                        pred = ast.unparse(_Rename(var).visit(ast.parse(ast.unparse(cond), mode="eval").body))
                        self._register(self.filters, triggers, pred)
                    # map expression (skip identity)
                    elt_src = ast.unparse(_Rename(var).visit(ast.parse(ast.unparse(sub.elt), mode="eval").body))
                    if elt_src != "x":
                        self._register(self.maps, triggers, elt_src)
            # reducer call: sum/max/min/len over the argument
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                if sub.func.id in _REDUCER_BUILTINS:
                    expr = _REDUCER_BUILTINS[sub.func.id]
                    self._register(self.reducers, triggers, expr)
                    self.reducers.setdefault(sub.func.id, expr)   # builtin word as trigger too

    # --- generation ----------------------------------------------------------
    def generate(self, query: str):
        toks = query.lower().replace("-", " ").replace(",", " ").split()
        filters = [self.filters[t] for t in toks if t in self.filters]
        maps = [self.maps[t] for t in toks if t in self.maps]
        reducer = next((self.reducers[t] for t in toks if t in self.reducers), None)
        # de-duplicate while preserving order
        filters = list(dict.fromkeys(filters))
        maps = list(dict.fromkeys(maps))
        if reducer is None and not maps and not filters:
            return None
        lines = ["def f(xs):"]
        for p in filters:
            lines.append(f"    xs = [x for x in xs if {p}]")
        for m in maps:
            lines.append(f"    xs = [{m} for x in xs]")
        lines.append(f"    return {reducer if reducer else 'xs'}")
        return "\n".join(lines)
