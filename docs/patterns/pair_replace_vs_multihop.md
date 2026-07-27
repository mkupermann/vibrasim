# Pattern: Pair-replace vs multi-hop

## Source
E28 PASS (replace ON curriculum) · E29 PASS two-hop replace OFF · E30 NULL replace ON multi-hop · E31 PASS parallel paths replace OFF

## Doctrine
- **`ilw_pair_replace_enabled=True`**: forgets other partners — use for **curriculum overwrite** (E28). **Breaks multi-hop** (kills L–M when adding M–R).
- **`ilw_pair_replace_enabled=False`**: keeps chain — use for **two-hop / parallel paths** (E29/E31).

Do not enable both goals with one global replace flag without a scoped replace policy.