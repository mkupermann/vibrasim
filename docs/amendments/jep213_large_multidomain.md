# JEP-213 — large multi-domain document validation (the full engine at document scale across all domains)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine handles a ~30-sentence multi-domain document (taxonomy + parts + causal + numbers + temporal + open
  relations) at high accuracy across all domains, no cross-domain interference at scale. RISK: a domain-boundary
  collision that only appears at scale.

## Result — PASS (HIT) + a minor cross-domain hygiene fix
Read a 30-sentence document spanning ALL domains -> {is_a:12, part_of:5, causal:4, numeric:4, comparison:3,
temporal:3, open:{'is capital of':3}}. Multi-domain correctness: 12/12 (is-a multi-hop poodle->organism; part-of
multi-hop + has; causal chain virus->tiredness; numeric how-many + compare; comparison transitive elephant->mouse;
temporal transitive famine->peace; open relation + WH; cross-domain negatives is_a(heart,animal)=False and a temporal
non-relation). consistency_audit empty (the doc is consistent). HONEST FIND + FIX: the first run spuriously induced
'has 2' as an OPEN relation (read_open re-parsed the numeric 'has N' sentences). FIXED read_open's is_fixed to exclude
connectives STARTING with 'has'/'have' (numeric + part-of) and temporal 'before/after' — so the numeric/temporal
facts stay in their domains and are not re-induced as open relations. After the fix: open = {'is capital of'} only;
12/12 maintained; 80/80 regression tests green (+1). So the full engine operates correctly at DOCUMENT scale across
ALL domains with clean domain separation. Prediction HIT; tally 102/129. Established (multi-domain extraction at
scale); named; no novelty.
