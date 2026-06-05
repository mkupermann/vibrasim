"""induce_construction — learn a new sentence pattern from a few (sentence -> fact) examples, then apply it to
unseen sentences (breakthrough attack A). Established method: anti-unification / template generalisation. Tokens
that stay the SAME across examples are the template's fixed words; tokens that VARY are slots; each fact element is
either a slot (varies) or a constant (fixed). No transformer, no pretrained model.
"""
import re


def _toks(s):
    return re.sub(r"[.,;:!?]", " ", s.lower()).split()


def induce(examples):
    """examples = [(sentence, (s, r, o)), ...] of ONE construction. Returns a template dict, or None if it can't
    align (different lengths / fixed words)."""
    toklists = [_toks(s) for (s, _) in examples]
    n = len(toklists[0])
    if any(len(t) != n for t in toklists):
        return None
    fixed = {}           # position -> fixed word
    slots = []           # positions that vary
    for i in range(n):
        vals = {t[i] for t in toklists}
        if len(vals) == 1:
            fixed[i] = toklists[0][i]
        else:
            slots.append(i)
    # map each fact role to ('slot', position) or ('const', value)
    mapping = []
    for role_idx in range(3):                                 # s, r, o
        vals = [ex[1][role_idx].lower() for ex in examples]
        if len(set(vals)) == 1:                               # constant across examples
            mapping.append(("const", vals[0]))
        else:
            # find the slot position whose captured value equals this role's value in every example
            hit = None
            for p in slots:
                if all(toklists[k][p] == vals[k] for k in range(len(examples))):
                    hit = p; break
            if hit is None:
                return None                                   # can't ground this role -> induction fails
            mapping.append(("slot", hit))
    return {"n": n, "fixed": fixed, "mapping": mapping}


_ARTICLES = {"a", "an", "the"}


def apply_template(tpl, sentence, flex_articles=False):
    """Return the (s, r, o) fact extracted from `sentence` if it matches `tpl`, else None. With flex_articles, an
    article (a/an/the) at a fixed position matches ANY article — function-word abstraction (JEP-355)."""
    if tpl is None:
        return None
    t = _toks(sentence)
    if len(t) != tpl["n"]:
        return None
    for pos, word in tpl["fixed"].items():
        if flex_articles and word in _ARTICLES:
            if t[pos] not in _ARTICLES:                       # must be SOME article
                return None
        elif t[pos] != word:                                  # fixed words must match in order
            return None
    fact = []
    for kind, v in tpl["mapping"]:
        fact.append(t[v] if kind == "slot" else v)
    return tuple(fact)
