# Mathematische Grundlagen — EQMOD brain-faithful Substrat

Konsolidierte Übersicht aller mathematischen Strukturen, die im Phase-A/B
Verlauf zum Einsatz kommen. Alle Gleichungen stehen explizit im Code, keine
black-box Komponenten.

---

## 1. Neuron-Dynamik: Conductance-based LIF

Pro Neuron (Excitatory oder Inhibitory):

$$
\tau_m \frac{dv}{dt} = -(v - v_{\text{rest}}) + g_e (E_e - v) + g_i (E_i - v)
$$

mit synaptischen Konduktanzen die exponentiell zerfallen:

$$
\tau_e \frac{dg_e}{dt} = -g_e, \qquad \tau_i \frac{dg_i}{dt} = -g_i
$$

Spike bei $v > v_{\text{thresh}}$, dann Reset $v \leftarrow v_{\text{reset}}$,
Refraktärzeit $\tau_{\text{ref}}$.

**Parameter (alle Phase B BETs):**

| Symbol | Wert |
|---|---|
| $\tau_m$ | 20 ms |
| $\tau_e$ | 5 ms |
| $\tau_i$ | 10 ms |
| $v_{\text{rest}}$ | -70 mV |
| $v_{\text{thresh,init}}$ | -54 mV |
| $v_{\text{reset}}$ | -75 mV |
| $E_e, E_i$ | 0 mV, -80 mV |
| $\tau_{\text{ref}}$ | 5 ms |

---

## 2. STDP-Plastizität (Bi-Poo 1998)

Pre-spike bei $t_{\text{pre}}$, post-spike bei $t_{\text{post}}$. Zeitfenster
$\Delta t = t_{\text{post}} - t_{\text{pre}}$.

$$
\Delta w =
\begin{cases}
A_+ \, e^{-\Delta t / \tau_+} & \text{wenn } \Delta t > 0 \\
-A_- \, e^{\Delta t / \tau_-} & \text{wenn } \Delta t < 0
\end{cases}
$$

Implementiert als event-driven Eligibility-Trace-Pair:

$$
\frac{dA_{\text{pre}}}{dt} = -\frac{A_{\text{pre}}}{\tau_+},
\qquad
\frac{dA_{\text{post}}}{dt} = -\frac{A_{\text{post}}}{\tau_-}
$$

- bei Pre-spike: $A_{\text{pre}} \mathrel{+}= dA_{\text{pre}}^{(0)}$, $w \leftarrow \text{clip}(w + A_{\text{post}}, 0, w_{\max})$
- bei Post-spike: $A_{\text{post}} \mathrel{+}= dA_{\text{post}}^{(0)}$, $w \leftarrow \text{clip}(w + A_{\text{pre}}, 0, w_{\max})$

**Parameter:**

| Verwendung | $\tau_{\pm}$ | $dA_{\text{pre}}^{(0)}$ | $dA_{\text{post}}^{(0)}$ | $w_{\max}$ |
|---|---|---|---|---|
| Input + Feedforward + Feedback | 20 ms | 0.01 | -0.012 | 2.0 |
| Recurrent E→E (BET-077c) | 20 ms | 0.005 | -0.006 | 0.3 |

Die getrennte $w_{\max}$ für recurrent E→E (0.3 vs 2.0) verhindert
runaway-firing im rekurrenten Layer.

---

## 3. R-STDP mit Eligibility-Trace (Frémaux-Gerstner 2016)

Zusätzlich zum STDP-Trace-Paar wird pro Synapse eine **Eligibility-Variable**
$e_{ij}$ geführt, die durch STDP-Kernel inkrementiert wird und exponentiell zerfällt:

$$
\frac{de_{ij}}{dt} = -\frac{e_{ij}}{\tau_e}
$$

- bei Pre-spike: $e_{ij} \mathrel{+}= A_{\text{post}}$
- bei Post-spike: $e_{ij} \mathrel{+}= A_{\text{pre}}$

Reward-modulierte Gewichts-Aktualisierung (am Ende des Trials):

$$
\Delta w_{ij} = \eta \cdot \delta \cdot e_{ij}
$$

mit TD-Error (Critic-Actor-Architektur):

$$
\delta = r - V(s), \qquad V(s) = \frac{1}{N_{\text{critic}}}\sum_k \text{firing}_k
$$

**Befund** (BET-067, 071, 072): Eligibility-Decay $\tau_e = 500\text{–}1000\,\text{ms}$
und einzelne TD-Updates pro Chunk reichen NICHT für Klassen-selektive Actor-
Verdrahtung. Drei sequenzielle NULLs auf demselben Mechanismus.

---

## 4. Homeostatische Threshold-Plastizität (Turrigiano 2008)

Pro E-Neuron eigene Variable $v_{\text{thresh}}^{(i)}$. Nach jedem Audio-Chunk:

$$
v_{\text{thresh}}^{(i)} \leftarrow \text{clip}\!\left(
v_{\text{thresh}}^{(i)} + \eta_h \cdot \left(s^{(i)} - s^*\right),
\ v_{\min},\ v_{\max}
\right)
$$

- $s^{(i)}$ = Spike-Zahl von Neuron $i$ im letzten Chunk
- $s^* = r^* \cdot \Delta t$ = Ziel-Spikes (z.B. $r^*=5\,\text{Hz} \cdot 100\,\text{ms} = 0.5$)
- $\eta_h$ = Drift-Rate in mV pro Spike-Excess (BET-077b: 0.05, BET-077c: 1.0)
- $v_{\min} = -60\,\text{mV}$, $v_{\max} = -48\,\text{mV}$

Bei BET-077c reichte $\eta_h = 1.0\,\text{mV}$ nicht, um Sättigung zu
verhindern — Recurrent E→E erzeugt mehr Aktivität als der homöostatische
Threshold-Drift abschwächen kann (Threshold sättigt am Cap $-48\,\text{mV}$).

---

## 5. KL-Divergenz für Klassen-Diskrimination

Symmetrisierte KL zwischen Spike-Pattern-Histogrammen zweier Klassen:

$$
\text{KL}_{\text{sym}}(P, Q) = \frac{1}{2}\bigl(D_{KL}(P \,\|\, Q) + D_{KL}(Q \,\|\, P)\bigr)
$$

wobei $P, Q$ über Bin-normalisierte Spike-Counts pro Neuron im Test-Set
geschätzt werden.

**Hierarchische Verstärkung** definiert als:

$$
A_{\text{KL}} = \frac{\max(\text{KL}_{L2/3}, \text{KL}_{L5}, \text{KL}_{L6})}{\text{KL}_{L4}}
$$

BET-077c: $A_{\text{KL}} = 11.80\times$ — tiefere Layer sind 12× klassen-selektiver
als das Input-Layer.

---

## 6. Prototype-Classification-Accuracy

Klassen-Mittelwert-Pattern:

$$
\vec{\mu}_c = \frac{1}{|S_c|}\sum_{\vec{x} \in S_c} \vec{x}
$$

Klassifikation eines neuen Patterns $\vec{x}$:

$$
\hat{c}(\vec{x}) = \arg\min_c \|\vec{x} - \vec{\mu}_c\|_2
$$

Accuracy: Anteil korrekter $\hat{c}(\vec{x})$ auf Test-Set.

Phase-A Brian2 hierarchisch L2: 0.83 (BET-068)
Phase-B cortical L5: 0.84 (BET-077c, vergleichbar trotz 125× mehr Neuronen)
Phase-B cortical L23: 1.00 (BET-077b mit Homeostase, perfekt)

---

## 7. Memory-Skalierungs-Bilanz

Pro Synapse mit STDP: ~80 Bytes (drei Plastizitätsvariablen `w, Apre, Apost`
+ Source/Target-Indices + Delay-Buffer + Overhead).

Pro Neuron LIF: ~200 Bytes (vier Differenzialgleichungs-Variablen
`v, ge, gi, v_thresh` + Refraktärstatus + Spike-Buffer).

Total Memory:

$$
M \approx N_{\text{syn}} \cdot 80\,\text{B} + N_{\text{neuron}} \cdot 200\,\text{B}
$$

**Mac Phase-B Realität (16 GB nutzbar ≈ 14 GB):**

$$
N_{\text{syn,max}} \approx \frac{14 \cdot 10^9}{80} \approx 1.75 \cdot 10^8
$$

Bei cortical-density 5000 Synapsen pro Neuron:

$$
N_{\text{neuron,cortical}} \leq \frac{N_{\text{syn,max}}}{5000} \approx 35\,000
$$

Bei degenerate-density 40 Synapsen pro Neuron (BET-076):

$$
N_{\text{neuron,degenerate}} \leq \frac{N_{\text{syn,max}}}{40} \approx 4.4 \cdot 10^6
$$

Trade-off: **brain-faithful Dichte** oder **viele Neuronen**, nicht beides.

---

## 8. Empirische Real-Time-Skalierung

Wall-Clock-Zeit-Faktor $F$ über sim-Zeit:

| Neuronen | Synapsen | $F$ (slower than real-time) |
|---|---|---|
| 200 (BET-068) | ~50K | $\sim 0.3\times$ (schneller als RT) |
| 1K (BET-073) | ~10K | $\sim 0.2\times$ |
| 10K (BET-074) | 5M | $30\times$ |
| 100K (BET-075) | 50M | $500\times$ |
| 1M (BET-076) | 40M | $487\times$ |
| 25K cortical (BET-077c) | 26.8M | $\sim 100\times$ |

Wachstum nicht linear in $N$ — dominiert von Synapsen-Updates und L1/L2-Cache-
Druck. cython-Speedup über numpy spürbar erst ab $N_{\text{syn}} \gtrsim 5 \cdot 10^6$.

---

## 9. Audio-Feature-Encoding

Pro Audio-Chunk (16 Samples bei 16 kHz = 1 ms wallzeit):

$$
\vec{f} = (\text{RMS},\ \text{ZCR},\ b_1, b_2, \ldots, b_8)
$$

mit RMS-Energie, Zero-Crossing-Rate, und 8 log-spaced FFT-Magnitude-Bändern.
Skaliert auf $[0, 1]$ → Poisson-Rate $r_k = f_k \cdot 100\,\text{Hz}$ für
Input-Neuron $k$.

---

## 10. Pre-Registrations-Mathematik

Für jedes BET $i$ gilt:

$$
\text{Verdict}_i = 
\begin{cases}
\text{PASS} & \text{wenn } \forall j:\ T_{ij}^{\text{measured}} \in \text{Bar}_{ij}^{\text{LOCKED}} \\
\text{NULL} & \text{wenn } \exists j:\ T_{ij}^{\text{measured}} \notin \text{Bar}_{ij}^{\text{LOCKED}}
\end{cases}
$$

Bars sind LOCKED **vor** Datenerhebung. Post-hoc Anpassung von $\text{Bar}_{ij}$
nach Sicht von $T_{ij}^{\text{measured}}$ ist Protokoll-Verletzung.

Drei NULLs auf demselben Mechanismus (BET-067/071/072 credit-assignment)
sind kein "Re-Versuch bis PASS", sondern ein scharfer Befund über die
Schwierigkeit unsupervised reward-modulated learning in single-iteration-
Budgets.

---

## 11. Phase-A Empirische Bilanz

| BET | Stufe | Verdict | Kernzahl |
|---|---|---|---|
| 065 | 1 Binär | PASS | acc 0.98 |
| 066 | 2 Multi-Klasse | hard-cap | audio infra |
| 067 | 5 R-STDP | NULL | acc 0.43 |
| 068 | 7 Hierarchie | PASS | L2 acc 0.83, KL ampl 10× |
| 069 | 4 Generation | PASS | cos 0.91, KL 0.24 |
| 070 | 3 Temporal | PASS | acc 0.70 |
| 071 | 6 Closed-Loop | NULL | motor selectivity 1.29 |
| 072 | 5 R-STDP+critic | NULL | acc 0.52 |

4 PASS, 2 NULL (credit-assignment), 1 hard-cap, 1 NULL (071 dito).

## 12. Phase-B (laufend)

| BET | Was | Verdict | Kernzahl |
|---|---|---|---|
| 073 | cython@1K | NULL | speedup 0.91× |
| 074 | 10K sparse | PASS | speedup 2.12× |
| 075 | 100K sparse | PASS | 5.4 GB peak |
| 076 | 1M sparse | PASS | 4.3 GB peak |
| 077 | cortical 25K | NULL | L23 0.94, L5/L6 collapse |
| 077b | + homeostase | NULL | L23 1.00, L5/L6 collapse |
| 077c | + bounded rec | NULL by sat | L5 0.84, KL ampl 12× |
| 078 | checkpoint | PASS | 0.0 diff bit-perfect |
