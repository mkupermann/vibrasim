# Communication programme summary (G97–G105)

## One-line
The quiet substrate is a usable CO-LOCATED spatial codec — multiple independent spatial channels at one
site, encoding multi-symbol messages at ~4 bits/symbol and reading them back in the same tick — provided
each symbol is actively reset. NOT transport across distance (G105): vibrations are absorbed locally.
This is the constructive complement to the closed memory deadlock: encode-without-an-LLM works as
real-time, same-site transduction, not storage and not spatial transmission.

## The arc
| G   | question | verdict | key number |
|-----|----------|---------|-----------|
| G97 | how many independent spatial channels, crosstalk-free? | PASS | pitch d~3 (box=30) → ~10 channels/axis; 2 channels @ 1.00 |
| G98 | can it carry a message free-running (decay clears ISI)? | NULL | sub-chance (0.17); vibrations accumulate & blow up |
| G99 | can it carry a message WITH a per-symbol reset?         | PASS | alphabet K=16 (4 bits/symbol), acc 0.94–1.00 both seeds |
| G100| how few ticks per symbol (bit rate)?                    | PASS | WIN=1 tick/symbol @ 1.00 → 3–4 bits per injection tick |
| G101| robust to interference?                                 | PASS | 1.00 up to interferer=signal (random-location noise; not adversarial) |
| G102| transmit a real ASCII string?                           | PARTIAL | seed 7 verbatim, seed 42 garbled — K=16 violates the pitch |
| G103| fix it with a repetition code?                          | NULL | fixes random errors only; seed 7 errors are systematic |
| G104| recover text VERBATIM by respecting the pitch (K=4)?    | PASS | `EQMOD SUBSTRATE SPEAKS` recovered exactly, both seeds, no ECC |
| G105| is it transport over DISTANCE or co-located readout?    | PARTIAL | far-end = chance; co-located = 1.00 → CO-LOCATED, not transport |

**End-to-end demonstration achieved (G104), with scope set by G105:** a text string is written into the
substrate as localized excitations and read back verbatim on both seeds, no LLM/transformer/embedding —
using K=4 to stay within G97's pitch. This is CO-LOCATED encode/decode (same site, same tick), NOT
transmission across distance — G105 shows free vibrations are absorbed locally and do not carry the symbol
downstream. G102/G103 are the instructive failures (operating past the pitch; coding can't fix systematic
confusion).

Channel spec (quiet substrate + active reset): ~10 parallel spatial channels × up to 4 bits/symbol ×
1 tick/symbol. Bounded everywhere by the reset requirement, never by integration time.

## What it is, honestly
- Standard digital communication over a linear channel (linear MIMO + multiclass linear decode). Named
  as established methods; NOT presented as novel mechanism. The contribution is the in-substrate
  MEASUREMENT: spatial pitch, ISI failure mode, and symbol alphabet.
- The decoder is LINEAR. The substrate reads and routes parallel inputs but does not combine them
  nonlinearly in real time (spatial XOR is NULL: G82/G83/G87). It is a channel, not a computer.

## The through-line to the memory result
The SAME physical accumulation that defeated selective persistent memory (G88–G96) reappears here as
inter-symbol interference (G98): the substrate RETAINS and SUPERIMPOSES signal rather than
storing-and-recalling it. Selective memory needs to keep one engram while staying blank elsewhere — the
substrate can't (active → contaminated, quiet → eroded). Communication needs the opposite: transmit and
CLEAR. The active reset (a cull) that ruins it as a memory is exactly what makes it work as a channel.
The substrate's nature is a fast, leaky, resettable medium — good for transduction, wrong for storage.

## Reusable
- docs/patterns/parallel_spatial_channel.md — the channel recipe + caveats.

## Open next
- The core primitive (encode → read-back at one site → decode, no LLM, no persistence) is demonstrated
  and SCOPED (co-located, not transport). A genuine TRANSMISSION line would need a carrier that survives
  propagation — G105 shows free vibrations don't. Open question: does any substrate quantity (a bridge
  wavefront, a charge front) propagate far enough to carry a symbol? Until then the honest claim is a
  co-located spatial codec, not a transmission line.
