# Pattern: Port wipe → restore → selective re-cut

## Source
E71–E98 port-circuit chain (soft/hard dual-cut curricula on 2×2, DEMUX, MUX, hybrid)

## Doctrine

### 1. Emitter disarm before rewrite
Residual `k_weaken_bridge_emitter` / `k_kill_bridge_emitter` re-zeros rewritten bridges (E71 NULL → E72 PASS).  
**Always clear emitters before ILW restore.**

### 2. Selective vs full restore after wipe
| Topology | Soft selective | Hard selective | Soft full | Hard full |
|----------|----------------|----------------|-----------|-----------|
| 2×2 | E79/E80 PASS | E84/E85 PASS | E81 PASS | — |
| DEMUX shared-L | E86 PASS | E88 PASS | E92 partial* | E95 PASS |
| MUX multi-L | E87 PASS | E89 PASS | E90 PASS | E91 PASS |
| Hybrid AND/OR | E75–E78 PASS | E73 PASS | E77 PASS | — |

\*E92: full restore PASS; soft re-cut after full NULL on tight sep.

### 3. Soft re-cut after full restore
Soft mid-radius collaterals when **neighbor mid distance ≤ soft radius** (E92, E96).

**Fixes (do not retune failed bars):**
- **Widen mid spacing** so dist > soft radius (E94 DEMUX, E97 MUX)  
- **Hard local kill** after full restore (E93, E95, E98)

Separate-L alone does **not** fix soft mid-collateral (E96).

### 4. Multi-trial reconfig after wipe
Identity↔swap after total soft wipe works both orders (E82/E83). Hybrid OR↔AND path-switch works (E78).

### 5. Shared bipartite endpoints (2×2)
Single-arm re-cut after full fan-out restore fails (E101–E103).  
**Cut all in-edges** of a shared output (e.g. 00+10 into R0) to silence that R for all L (E104 PASS).  
**Diagonal cuts after full restore:** soft-cut 00+11 → pure swap (E105); soft-cut 01+10 → pure identity (E106); multi-trial switch (E107); hard identity-diag (E108); hard swap-diag (E109). Soft+hard matrix closed.

**Selective vs dual restore after shared-endpoint edit (E110–E119):** After dual-cut into **shared** R0 or after identity-diag cut, restoring a **single** arm reopens L0 but **does not preserve L1 isolation** (E110/E111/E113 B3=0). Hard dual-cut + soft selective same leak (E113). **Dual restore all cut arms** recovers cleanly: soft/hard R0 silence (E112/E115), both diags (E114/E116). Multi-trial soft/hard silence cycles (E117/E118 PASS).

**Non-shared endpoints unlock selective restore (E119–E121 PASS):** Split R0→R0a/R0b (separate spatial ends for arms 00/10). Soft-cut both + restore only 00 → L0→R0a ON and L1→R0b still OFF (E119). Hard dual-cut + soft selective same (E120). Multi-trial silence→restore 00→re-cut 00 keeps L1 isolated (E121). Shared bipartite R was the E110 leak cause.

Doctrine: (1) shared R → restore **all** cut in-edges (or re-cut all for multi-trial silence); (2) non-shared R copies → single-arm selective restore and multi-trial selective re-cut are L-selective (soft/hard).

**Dual 3-hop wipe-restore-recut CLOSED NULL (E123–E127):** Soft or hard dual wipe + full restore both PASS. Re-cut path0 after full restore fails for: soft single I0 (E123), hard single I0 after soft wipe (E124), wide soft (E125), hard wipe + hard single I0 (E126), multi-site hard hop mids (E127) — all B3=0. Hard selective on **pristine** dual 3-hop (E56) still stands. **After wipe-restore, dual 3-hop path0 re-cut does not work under current mid-port kill/weaken doctrine** (single or multi-site). Boundary locked; reopen only with a genuinely new re-cut mechanism.

## Not free talent
All wipe/restore is engineered §4.8 ports + ILW + bridges + latch. Free dual talent remains CLOSED PARTIAL (C16 family).

## Value
Reusable operating rules for durable port graphs under soft/hard structural edit.
