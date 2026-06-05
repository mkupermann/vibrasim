# EQMOD / vibrasim — Complete History & Handoff (single self-contained document)

> **Purpose.** This file is written so that a fresh AI instance, given **only this document and the repo**,
> can understand the entire project and continue it correctly. It assumes no memory of prior chats. If this
> document ever disagrees with the live code or the per-experiment docs, **the code and `docs/amendments/*.md`
> win** — but this is the map that tells you where to look. Last fully updated: **2026-06-06.**
>
> Repo root: `C:\Users\nicet\Documents\GitHub\vibrasim` · Owner: **Michael Kupermann** (michael@kupermann.com)
> · Git: branch `main`, remote synced. · The owner is a hobbyist working four disciplines outside his training;
> treat him as the scientific authority on direction, and be ruthlessly honest with him (he values that most).

---

## 0. TL;DR — read this first
EQMOD is a **bottom-up substrate simulator** (a 3D physics-like sandbox of "vibrations" that bind into
"atoms/molecules/bridges") plus several **cognition stacks** built on or beside it. The stated research goal is
**"developing a deadlock-breaking process, not necessarily succeeding at the simulation."** After ~150 substrate
experiments and ~150 cognition experiments, the honest, repeatedly-stress-tested conclusion is:

> **The substrate's own physics is computationally DECORATIVE everywhere tested. Standard, established methods
> (linear readouts, VSA/HRR, reservoirs, simulated annealing, RNNs) carry every win. The real deliverable is
> the rigorous, self-correcting *process* — pre-registration, matched negative controls, and retracting
> over-claims rather than making them.**

This is not a failure to the project; per the README it is the honest, intended result. Your job continuing it
is to **keep that honesty**, not to manufacture a win.

---

## 1. What EQMOD actually is (and the names caveat)
- **The primitive** is a *vibration*: a 4-property unit (frequency, polarity, position, velocity) moving in a 3D
  box. On top sit **explicit, hand-written binding rules** at six levels: electron → pair → triad → atom →
  molecule → bridge. Plasticity on bridges: **STDP** (Bi & Poo 1998) + a **BTSP-inspired eligibility trace**
  (Magee 2026 time-constant, but NOT the full plateau-potential mechanism).
- **CRUCIAL HONESTY (Michael's own framing in `README.md`):** the words *vibration, electron, atom, molecule,
  bridge* are **nomenclature, not ontology** — labels for abstract nodes following rules he wrote by hand, one
  parameter at a time. They are **not** the physics they sound like. The hierarchy does **not** emerge from the
  primitive; the binding rules are first-class engineering (`docs/CONCEPT.md`).
- **The five "consciousness markers"** (low bars, deliberately): `len(self_model) ≥ 2`, `workspace_winner > 0`,
  `prediction_error ∈ (0,1)`, `btsp_potentiation drifted by 0.5`, `n_patterns_now > n_patterns_at_start`. They
  fire under trained engrams and **not** under a matched no-engram negative control. A low bar that passes a
  fair control is still a low bar — Michael says this out loud. See `docs/marker_protocol.md`.
- **Meta-goal:** the transferable half is the *process* (the `LOGBOOK.md`, pre-registration docs, the autopilot
  pipeline spun out to `github.com/mkupermann/single-mac-autopilot`). README §intro says this meta-half "held up
  better" than the substrate.

## 2. HARD CONSTRAINTS (from `CLAUDE.md` — obey exactly for the substrate & cognition programmes)
- **NO LLM, NO transformer, NO pretrained embedding model, NO BPTT tokenizer** in any *substrate/cognition*
  solution. Stay within substrate primitives: STDP, BTSP eligibility, dream consolidation (G15/G18),
  k_pattern_id segregation (G10), SubstrateLibrary (mixture-of-experts memory), engineered port topology.
- **Ports are engineered; internals must emerge.** When new capability is wanted (e.g. text output), propose
  amendments that *reuse* these primitives — never bolt on neural-net layers.
- **EXCEPTION — the GEOMETRIC programme (EQMOD-3, "GEO-*"):** Michael explicitly opened a *separate* track where
  the substrate is redefined as a geometric concept-space **over an LLM**, and **ML/LLM ARE allowed**. Do not
  confuse the two regimes. If you are doing G-/BET-/JEP- work, no LLM. If GEO-, LLM allowed.

## 3. Environment & how to run
- macOS-arm64 originally; now also runs on Windows 11 + PowerShell (this machine). Python 3.13, `.venv` at repo
  root (`.venv/Scripts/python.exe` on Windows).
- Numba JIT cache live for physics hot paths. pyvista 0.48 (no PyQt) for the GUI.
- **Default `WorldConfig` saturates node capacity fast** (1000 vibrations, 60³, n_nodes_max=1024). For
  tests/smokes use `renders/calibration_session3.toml`.
- Tests: `pytest -m "not slow"` for the fast slice. Interactive GUI: `python -m world gui`.
- **Known bug (still live):** F3b-Test silent-pass — `if n_strong_before == 0: persistence_fractions.append(1.0)`
  → the test can never fail when no strong structures formed.
- **Two persisted "brains":** `~/.eqmod/brain/talk` (Conversation default) and `~/.eqmod/brain/web` (GUI, port
  8765). Experiment results stream to `~/.eqmod/bet/<NAME>/result.json`.

## 4. Methodology / discipline (NON-NEGOTIABLE — this IS the project)
- Every experiment is **pre-registered**: acceptance bars written in `docs/amendments/<name>.md` **BEFORE** the
  run. **Post-hoc threshold tuning is forbidden.**
- **PASS / NULL / PARTIAL are all valid verdicts.** NULL is a finding, not a failure to retry.
- **Negative controls** (matched-wallclock, no-engram) must FAIL for a trained result to mean anything.
- Name **established methods as established**; reserve "new" for genuine novelty. Michael has repeatedly,
  correctly, challenged dressing known methods (VSA/reservoir/RLS/SA/e-prop) as novel. See the memory
  `[[no-dressing-known-as-novel]]`.
- Reusable mechanisms → `docs/patterns/*.md`, never hidden in code.
- **Numbering schemes:** `G###` = substrate physics thread (G1–G153). `BET-###` and `JEP-###` = cognition
  threads (BET to ~146, JEP to ~476). `GEO-##` = geometric/LLM track. They are *separate, overlapping* counters
  — do not assume a global order. **803 amendment docs, 785 tool scripts exist** — always `ls docs/amendments/`
  and read the highest few before claiming a "new" number (see Lesson 11.1).

---

## 5. THE PROGRAMMES — full thread-by-thread history & verdicts

### 5A. EQMOD substrate physics (G-thread) — the original "does matter compute / remember?" programme
Authoritative: `docs/amendments/FINDINGS_SUMMARY.md` (+ Addenda 1–5), `docs/SYNTHESIS.md`, `FRONTIER.md`,
memory `[[substrate-programme-state]]`.

- **Memory (ACTIVITY representation) — CLOSED NEGATIVE (≈70 NULLs, G83–G96).** The substrate has **no stable
  blank state**: any structured region latches self-activity, so there is never a written-vs-unwritten
  contrast. Slogans: *"write = broadcast = leak"* and *"maintenance = contamination."* Selective persistent
  content memory does **not** emerge in activity. Conclusively closed (even with stim/control physically
  disconnected, G86).
- **Memory (MATTER POSITION) — POSITIVE, scoped (G114–G125).** The escape: drive an *atom* to a location; it
  *holds* the position after release (matter doesn't spread/leak like activity). This is a **selective +
  persistent multi-bit content-addressable store** with wide spacing (G119, 1.000/bit). It is **MAINTAINED, not
  static** (G120): empty cells need active selective clearing or background repopulates them. The one real
  memory positive. Docs: `MATTER_MEMORY_SUMMARY.md`.
- **Communication — POSITIVE, scoped (G97–G105).** The *quiet* substrate is a usable real-time **co-located
  spatial codec** (linear MIMO readout, named as such): ~10 parallel channels × ≤4 bits/symbol × 1 tick/symbol,
  needs an **active reset between symbols**. CAPSTONE G104: a real ASCII string "EQMOD SUBSTRATE SPEAKS" was
  written and read back verbatim — but only at K=4 pitch. **NOT transport over distance** (G105: free
  vibrations decode at chance downstream; "transmission" wording was retracted). Docs: `COMMUNICATION_SUMMARY.md`.
- **Transport — free carriers closed; slow driven-MATTER transport works (G105–G112).** Continuously-driven
  atoms traverse >20 units alive carrying their symbol (G112), at ~3% nominal speed. Two comm modes: fast
  co-located codec + slow driven-matter line.
- **Proto-cell (G30–G49).** A spontaneously-assembled membrane that is **persistent, homeostatic, recovers to
  set-point, is a reaction chamber — but NOT self-renewing.** Self-repair fails (G46–G49): a wounded membrane
  does not heal. Cause, isolated by elimination (NOT valence commitment G48, NOT positional rigidity G49):
  **template-directed recruitment is absent** — the bond-saturated shell can't recruit new atoms at the wound.
  Docs: `PROTOCELL_SUMMARY.md`, `protocell_*` patterns. (Note: G47–G49 were *re-derived* by accident in the
  2026-06-05/06 session before realizing they were already done — see Lesson 11.1.)
- **Deep unification (`SYNTHESIS.md`):** there is no controllable middle regime — too sparse/active SPREADS (no
  selective memory); the medium is OVERDAMPED so nothing MOVES (no transport). You get **one of
  {localized, persistent, mobile} at a time**, never all together.

#### 5A-bis. Computation / optimization sub-thread (G135, G138–G153) — the last candidate for a real edge
- **EQMOD's own dynamics CANNOT optimize (G135):** atoms collapse; the bridge/binding graph is not a
  programmable problem Hamiltonian. So the "physical computing" question moved to an **adjacent, off-substrate**
  paradigm: **oscillator-Ising / Hopfield / RBM machines** (G138–G145), which ARE programmable (couplings =
  problem). Note this is *not EQMOD* — it's standard analog-Ising-machine hardware, tested in numpy.
- **G145 claimed the programme's ONE genuine advantage:** oscillator-Ising annealing beats greedy 8/8 on hard
  frustrated MAX-CUT. **This was rigorously REFUTED and re-characterized over G146→G153 (the 2026-06-05/06
  session):**
  - **G146** — G145's greedy baseline was **sign-bugged** (it minimized the cut; negative values). A *correct*
    greedy ties the oscillator on the (actually easy) n=30 instances. The "8/8" beat a backwards baseline.
  - **G147/G148** — at scale (n=200–360), classical **Simulated Annealing (SA)** genuinely beats correct greedy
    (~+2%), but the **naive oscillator only ties greedy and loses to SA 15/15**. The edge is the *algorithm's*.
  - **G149** — 10× compute doesn't help the naive oscillator → weakness is fundamental.
  - **G150** — steel-man: the textbook **amplitude-heterogeneity-corrected CIM (AHC; Leleu/Yamamoto 2019)**
    DOES beat correct greedy and comes within ~0.7% of SA.
  - **G151** — that holds on the ±1/SK family too (family-robust).
  - **G152** — and up to n=600 (scale-robust).
  - **G153 (decisive budget-match)** — give SA a fair/generous budget (a **numba-JIT SA**, ~100× faster, now a
    reusable asset): **SA beats AHC-CIM 8/8 (~+1.7%)**. The apparent near-tie was a budget artifact.
  - **Resolved ordering at matched budget: `SA > AHC-CIM > correct-greedy`.** A correct physical Ising annealer
    is real and beats local search, but **classical SA is the better & simpler solver, and EQMOD is neither.**
  - Corrections propagated to `g139/g140/g145`, `patterns/oscillator_ising_computing.md`, FINDINGS Addendum 5.

### 5B. EQMOD-2 cognition (BET/JEP-thread) — language/learning WITHOUT LLM/transformer
Authoritative: `COGNITION_PROGRAMME_SUMMARY.md`, memory `[[cognition-programme-state]]`,
`[[durable-substrate-reasoning-state]]`, patterns `substrate_reservoir_online`, `systematic_generalization`,
`recurrent_substrate_composition`, `compositional_cognition`.

- **Compose + read out (BET-110→132).** Stack = analog **VSA/HRR** (`world/vsa.py`: bind + analog bundle +
  CleanupMemory) → **reservoir** (`world/reservoir.py`: random tanh features + **RLS** online readout, no
  backprop). **The law (BET-129/130):** systematic generalization to novel symbol combinations scales with the
  **number of compositions experienced** (a curriculum law), not with dimension D. **Milestone BET-132 PASS:**
  generates the correct written next word for templated sentences never seen (100% held-out; no-rule control at
  chance). Honest boundary: only for linearly-separable regularities.
- **Recurrent composition (BET-136→140).** Substrate-native recurrence + nonlinear cell + sharp readout +
  in-loop cleanup = **drift-free unbounded recursive composition** (BET-140: parity at length 100, trained on 4
  single steps, local rule, **no BPTT**). Honest: RNN/reservoir+cleanup is textbook; value = the component map.
- **Temporal credit (BET-144→146, the 2026-06-06 session — newest).** Tested the stated frontier *"deep credit
  assignment without BPTT (e-prop/equilibrium-prop)."* Three arms on delayed selective recall (reservoir vs
  exact **RTRL** (Williams-Zipser 1989) vs **e-prop** (Bellec 2020, eligibility = BTSP-aligned)):
  - **BET-144 NULL** — D=8 within reservoir memory capacity (too easy); e-prop weak (below reservoir & RTRL).
  - **BET-145 NULL but SHARP** — delay sweep: reservoir horizon ~D≈14; at the break point **exact RTRL ALSO
    collapses** to chance, not just e-prop. → **The bottleneck is the ungated ARCHITECTURE (vanishing
    memory/gradient, Bengio 1994), NOT the credit-assignment rule.** No learning rule conjures a capability the
    architecture lacks. The lever is a **gated cell** (LSTM/GRU/JANET) — an established fix.
  - **BET-146 — PRE-REGISTERED but NOT RUN.** Tests whether a gated cell + exact RTRL (no BPTT) extends the
    horizon past the ungated wall (confirming the BET-145 diagnosis). Doc + tool ready
    (`bet_146_gated_memory.md`, `run_bet146_gated_memory.py`). **This is the cleanest place to resume.**
- **Affect / "energy cloud" (JEP-425→476).** Michael's hypothesis: bright/dark valence as a learning signal.
  Built a durable energy/affect model on the VSA store (`world/substrate_memory.py`, `world/energy.py`,
  `world/valence_reservoir.py`): taught/inherited(is-a)/signed-propagated(Heider)/generalized affect +
  ambivalence. Studied the **complexity ceiling**: it's order ~2 over VSA clouds, and the wall is
  **Statistical-Query hardness of parity** (Kearns 1998) — decisively shown vs a GF(2) algebraic module that
  cracks it (JEP-461). A bolt-on algebraic structure-discovery module escapes the SQ wall (HYB-*). Honest
  new-science verdict: **NO** new math, rigorously earned. Integration validated (JEP-476: 22/22, zero
  falsehoods). Summary: `ENERGY_FRONTIER_SUMMARY.md`.

### 5C. Other tracks (read their summaries before touching)
- **Perception + persistence (JEP-286→295):** senses + slow human-in-the-loop teaching, no transformer.
  `world/active_learner.py` (ask-when-unsure), `tools/teach_gui.py`, `world/audio_features.py` (stdlib FFT
  hearing). Memory `[[perception-thread-state]]`, `[[teaching-philosophy-rules]]` (open questions, connect to
  known facts, visual aids, "teach it like a child").
- **EQMOD-4 Understanding Engine (JEP-1→186):** Michael's MPC+EBM+joint-embedding directive culminated in
  `world/understanding.py` (NO transformer): LEARN from prose (5 relation types, 0.93 recall) → UNDERSTAND
  (multi-hop, grounding, developmental loop) → COMMUNICATE (Q&A/why/belief-revision). 62 tests. Frontier = real
  corpus, open generation, NL long-tail (the no-transformer wall). Docs `UNDERSTANDING_ENGINE.md`,
  `EQMOD4_FINAL_STATE.md`, memory `[[eqmod4-jepa-ebm-mpc-state]]`. **Talk to it:** `world/conversation.py`,
  `docs/HOW_TO_TALK.md`.
- **Durable substrate reasoning (JEP-294→341):** durable/growing VSA store + reasoning suite + rule-induction +
  generation + conversation (`talk.py`). Memory `[[durable-substrate-reasoning-state]]`.
- **GEOMETRIC track (EQMOD-3, GEO-1..22) — DIFFERENT CONSTRAINT (LLM ALLOWED):** substrate redefined as a
  geometric concept space over an LLM; working neuro-symbolic learn+understand on PC. Docs
  `GEOMETRIC_PROGRAMME.md`, `GEOMETRIC_ANSWER.md`, memory `[[geometric-programme-state]]`.

---

## 6. THE BIG HONEST CONCLUSION (state it without softening)
Across both major programmes:
- **The EQMOD substrate is computationally decorative.** Activity-memory impossible; matter-position memory and
  co-located communication are real but narrow; its own dynamics can't optimize (G135); its last adjacent
  candidate (oscillator-Ising) loses to classical SA at matched budget (G153).
- **The no-LLM cognition stack is bounded:** standard ML (VSA, reservoir, RLS) carries it; the substrate is
  decorative there too; long-term dependencies hit the ungated-architecture wall (BET-145); language hits the
  no-transformer / SQ-hardness walls.
- **Every "win" found this project belongs to an established method, named as such.** The deliverable is the
  **self-correcting process** — and this session's signature act was *retracting* an over-claim (G145) through
  four moves now distilled in `docs/patterns/auditing_a_headline_positive.md`: sanity-check the BASELINE,
  compare vs the PROPER peer, SEPARATE your method from the established one it rides on, kill the
  "under-resourced" objection with a matched control.

---

## 7. FILE MAP (where everything lives)
- **Orientation:** `FRONTIER.md` (one-screen current state), `README.md` (Michael's honest framing),
  `CLAUDE.md` (constraints, env, known bugs), **this file.**
- **Diary:** `LOGBOOK.md` (append-only, newest at bottom — current state is buried there, hence `FRONTIER.md`).
- **Per-experiment pre-registrations + results:** `docs/amendments/g*.md`, `bet_*.md`, `jep*.md`, `geo*.md`
  (803 files). **Top-level syntheses:** `FINDINGS_SUMMARY.md`, `SYNTHESIS.md`, `MEMORY_PROGRAMME_SUMMARY.md`,
  `MATTER_MEMORY_SUMMARY.md`, `COMMUNICATION_SUMMARY.md`, `PROTOCELL_SUMMARY.md`,
  `COGNITION_PROGRAMME_SUMMARY.md`, `ENERGY_FRONTIER_SUMMARY.md`, `GEOMETRIC_PROGRAMME_SUMMARY.md`,
  `UNDERSTANDING_ENGINE.md`.
- **Reusable mechanisms:** `docs/patterns/*.md` (40+; incl. `auditing_a_headline_positive.md`,
  `oscillator_ising_computing.md`, `recurrent_substrate_composition.md`, `calibration_lessons.md`).
- **Core code (`world/`):** `state.py` + `config.py` + `physics.py` (the substrate sim); `vsa.py` (HRR),
  `reservoir.py` + `valence_reservoir.py` (readouts), `substrate_memory.py` + `energy.py` (durable affect/VSA
  store), `understanding.py` (Understanding Engine), `conversation.py` + `brain_query.py` (talk/Q&A),
  `active_learner.py` + `audio_features.py` (perception), `dream.py` (consolidation), `induce_construction.py`
  (rule induction), `interactive.py` (GUI).
- **Experiment runners:** `tools/run_*.py` (785). Newest this session: `run_g146..g153_*`, `run_bet144..146_*`.
- **Results cache (not in git):** `~/.eqmod/bet/<NAME>/result.json`.

## 8. OPEN QUESTIONS / where to resume (in rough priority — but ask Michael for steer on big forks)
1. **BET-146 (ready to run):** does a gated cell + exact RTRL extend the working-memory horizon past D≈14?
   Confirms (or refutes) BET-145's architectural diagnosis. Established fix; honest either way.
2. **Cognition no-transformer wall:** open-ended NL generation, real corpora, non-separable structure remain the
   frontier for EQMOD-2/4. Likely needs a method honestly named (and may simply not be reachable without
   transformers — that itself is the finding).
3. **Substrate physics is essentially exhausted** — further G-experiments risk re-derivation or churn. Do NOT
   spin them up without a genuinely novel angle.
4. **GEO track** (LLM allowed) is the one place "real new mathematics could live" per Michael — but largely
   unexplored recently.

## 9. HOW MICHAEL WORKS WITH YOU (so you don't repeat mistakes)
- He runs this **autonomously** via a Stop-hook ("autonomy enforcement") that pushes you to chain experiments
  and never stop. **The ONLY clean stop is the kill-switch file `.eqmod_autonomy_off` at repo root** (currently
  PRESENT → autopilot is OFF as of 2026-06-06, on his explicit instruction "stop and reflect"). Delete it to
  resume autonomy.
- **His direct instruction overrides the hook.** On 2026-06-06 he said "Stop, write everything in one document,
  then stop." Respect that. When he says stop, stop — do not manufacture experiments against his wishes.
- He demands **brutal honesty** and hates dressing known methods as novel. He gives steer in German and English.
  Commit trailer he requires: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Always **commit AND push** after each experiment; pre-register bars BEFORE running.

## 10. LESSONS / GOTCHAS (hard-won — don't relearn the hard way)
1. **The re-derivation trap (2026-06-06):** a stale "frontier" view caused G47–G49 to be re-run though long
   superseded (and a duplicate `g49` doc created). FIX: read `FRONTIER.md` + `git log` + the highest
   `docs/amendments/` numbers BEFORE proposing any "new" experiment. 803 docs exist; most ideas are done.
2. **Calibration lesson #16:** conversational test runners MUST use a fresh `Conversation(brain_dir=tempfile.mkdtemp())`
   — never the shared persisted `~/.eqmod/brain/talk`, or results leak across runs. (See `calibration_lessons.md`.)
3. **Audit your own positives** before headlining them: sign-check baselines (G145 greedy bug), compare vs the
   proper peer (SA not greedy), separate your method from the algorithm it rides on, kill the budget objection.
4. **Verdict-of-record is the pre-registration DOC, not a possibly-buggy harness print** (a classification
   ordering bug bit G147 — report the doc's criterion, flag the code).
5. **Numba SA** (`run_g153_*`) is ~100× faster than the Python flip loop — reuse it for any large-n optimization.
6. **Known live bug:** F3b silent-pass (§3). And 2 `test_phase2_binding` freq-gating tests are `xfail` (obsolete
   by design: atom→molecule binding intentionally skips the freq check; selectivity is at electron binding).
7. **Don't trust the start-of-session git snapshot** for the frontier — it can be stale; trust `git log`.

---
*End of handoff. If you are the fresh AI reading this: start at §0 and §8, verify against `FRONTIER.md` and the
highest `docs/amendments/` numbers, and keep the honesty that is the whole point of this project.*
