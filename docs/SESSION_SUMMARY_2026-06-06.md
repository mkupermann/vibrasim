# Session Summary — 2026-06-06 (alles an einem Ort, zum Nachdenken)

Michael: hier ist die **vollständige** Zusammenfassung dieser Session in einem Dokument. Danach stoppe ich.
Alles unten ist committet und gepusht; der Arbeitsbaum ist sauber, `main` synchron mit origin.

---

## 1. Worum es ging
Zwei Dinge sind diese Session passiert:
1. **Ich habe die einzige positive Behauptung des Substrat-Programms streng überprüft — und sie korrigiert.**
2. **Ich habe einen neuen Faden (kognitives Gedächtnis / zeitliche Kredit-Zuweisung) begonnen** und einen
   scharfen, ehrlichen Befund erzielt — bevor du mich gestoppt hast.

Wichtige ehrliche Selbstkritik vorab: **Der Anfang der Session war Verschwendung.** Ich habe G47–G49
(Proto-Zell-Selbstreparatur) noch einmal hergeleitet, obwohl sie längst durch G50–G145 erledigt waren — weil
mein „Frontier"-Bild veraltet war. Das habe ich erkannt, ehrlich protokolliert, ein Duplikat (`g49`) entfernt
und als Gegenmaßnahme **`FRONTIER.md`** angelegt (eine Ein-Seiten-Karte des aktuellen Stands), damit das einer
zukünftigen Session nicht wieder passiert.

---

## 2. Der Kern: die EINE positive Behauptung des Programms — widerlegt, dann präzisiert (G145 → G153)

**Ausgangslage (G145, frühere Session):** „Der oszillator-Ising-Rechner schlägt Greedy 8/8 auf harten
frustrierten MAX-CUT-Instanzen — das ist die *eine* Stelle, wo ‚Vibrations-Computing' einen echten Vorteil
hat." Das war die einzige positive Aussage des gesamten Substrat-Programms.

**Was ich Schritt für Schritt herausgefunden habe:**

| Exp | Befund |
|-----|--------|
| **G146** | G145s Greedy-Baseline war **vorzeichen-fehlerhaft** (sie *minimierte* den Cut, negative Werte −25…−67). Ein *korrekter* Greedy erreicht das Optimum auf allen n=30-Instanzen → die sind gar nicht hart, der Oszillator *gleichauf* mit korrektem Greedy. Das „8/8" war ein Sieg über eine rückwärts laufende Baseline. |
| **G147–G148** | Bei Skalierung (n=200–360) schlägt **klassisches Simulated Annealing (SA)** korrektes Greedy wirklich (~+2 %, 14/15). Aber: trennt man den *physischen Oszillator* von SA, so liegt der **naive Oszillator nur gleichauf mit Greedy und verliert 15/15 gegen SA**. Der Vorteil gehört dem *Algorithmus* (SA), nicht dem Substrat. |
| **G149** | Auch mit **10× Rechenleistung** holt der naive Oszillator nicht auf → die Schwäche ist **fundamental, kein Budget-Artefakt**. |
| **G150** | Steel-Man: Mit der etablierten **Amplituden-Korrektur (AHC-CIM, Leleu/Yamamoto 2019)** **schlägt** der Oszillator korrektes Greedy (5/5) und kommt bis auf ~0,7 % an SA heran. Die Schwäche war *teils* die naive Dynamik. |
| **G151** | Das gilt **robust** auch auf der zweiten kanonischen harten Familie (±1 / Sherrington-Kirkpatrick). |
| **G152** | Und **skaliert** bis n=600 (Beinahe-Gleichstand hält). |
| **G153** | **Budget-Match (entscheidend):** Gibt man SA ein faires/großzügiges Budget (numba-JIT-SA), schlägt **SA den AHC-CIM 8/8 (~+1,7 %)**. Der scheinbare „CIM ≥ SA"-Eindruck war ein Budget-Artefakt. |

**Ehrliches, vollständig aufgelöstes Ergebnis (Reihenfolge bei fairem Budget):**

> **SA  >  AHC-CIM  >  korrekter Greedy.**

- Das **EQMOD-Substrat selbst** ist **rechnerisch dekorativ** — seine eigene Dynamik kann nicht optimieren
  (G135). *Unverändert.*
- Ein **korrekt gebauter physischer Ising-Annealer (AHC-CIM)** ist real: er schlägt lokale Suche und spielt in
  SAs Liga — **aber das ist etablierte, *benachbarte* Hardware, NICHT EQMOD**, und **klassisches SA ist
  marginal das Beste und viel einfacher.**
- Einzeiler: *Ein korrekter physischer Ising-Annealer ist real und schlägt lokale Suche, aber klassisches SA
  ist der bessere und einfachere Löser — und EQMOD ist keiner von beiden.*

Das **kehrt G145s Schlagzeile um**, und zwar ehrlich verdient: Jede Übertreibung wurde unterwegs gefangen (der
Vorzeichen-Bug, die `max(OSC,SA)`-Vermischung, der „zu wenig Rechenzeit"-Einwand, das Budget-Artefakt).

---

## 3. Neuer Faden: tiefe ZEITLICHE Kredit-Zuweisung ohne BPTT (BET-144 → 145; 146 nur vorregistriert)

Nachdem der Optimierungs-Faden erschöpft war, bin ich zur **offenen Grenze des Kognitions-Programms**
gewechselt (laut Memo: „deep credit assignment without BPTT = e-prop / equilibrium-prop frontier"). e-prop
(Bellec 2020) nutzt **Eligibility-Traces** — was ein **Kern-Primitiv des Substrats (BTSP)** ist.

**Aufgabe:** verzögerter *selektiver* Abruf mit Ablenkern (Cue speichern, D Ablenker ignorieren, am Ende
abrufen). Drei Arme: **Reservoir** (nur Readout), **RTRL** (exakter Online-Gradient, Williams-Zipser 1989),
**e-prop** (Eligibility, substrat-nah). Alles **ohne** BPTT/Transformer, leaky-tanh-RNN.

| Exp | Befund |
|-----|--------|
| **BET-144** | **NULL.** Sanity ok (RTRL & e-prop 1.0 bei D=1 → Trainer funktionieren). Aber bei D=8 löst schon das **Reservoir** die Aufgabe (0.815) → zu leicht, kein Tiefen-Kredit-Bedarf. Nebenbefund: e-prop (0.613) **schlechter** als Reservoir und RTRL. |
| **BET-145** | **NULL — aber scharf diagnostisch.** Delay-Sweep: Reservoir-Horizont ~D≈14. Am Bruchpunkt (D=16) **bricht auch der EXAKTE RTRL zusammen** (0.290 ≈ Zufall), nicht nur e-prop. → **Der Engpass ist die ARCHITEKTUR (ungated leaky-tanh, verschwindendes Gedächtnis/Gradient, Bengio 1994), NICHT die Lernregel.** Keine Kredit-Zuweisungsmethode kann etwas erzeugen, das die Architektur nicht halten kann. |
| **BET-146** | **Nur vorregistriert, NICHT ausgeführt** (du hast hier gestoppt). Geplant: Test, ob ein **gated** Zell-Typ (JANET/LSTM/GRU-artige Vergiss-Gate) den Horizont über die ungated Wand hinaus verlängert, trainiert mit demselben exakten RTRL ohne BPTT. Code + Bars liegen bereit (`docs/amendments/bet_146_gated_memory.md`, `tools/run_bet146_gated_memory.py`), falls du es später laufen lassen willst. |

**Ehrliche Schlussfolgerung dieses Fadens (Stand 145):** Die *tiefe zeitliche Kredit-Zuweisung* ist nicht der
Engpass — auch der exakte Gradient (RTRL) scheitert an derselben Wand wie e-prop und das Reservoir (~D14). Der
echte Hebel für Langzeit-Arbeitsgedächtnis ist eine **gated Speicherzelle** (etablierte Lösung, kein neues
Mathe). Ob ein *substrat-naher* multiplikativer Gate-Pfad das löst, ist die offene Frage (BET-146, ungelaufen).

---

## 4. Prozess-Arbeit (das „bessere Deliverable" laut README)
- **`FRONTIER.md`** — Ein-Seiten-Karte des aktuellen Stands aller Fäden, damit nicht wieder Erledigtes
  hergeleitet wird (die Verschwendung am Sessionanfang war der Auslöser).
- **`docs/patterns/auditing_a_headline_positive.md`** — die Methode destilliert, mit der G145 gekippt wurde
  (Baseline prüfen, gegen den *richtigen* Gegner messen, deine Methode vom etablierten Verfahren trennen, den
  „zu wenig Budget"-Einwand mit einer fairen Kontrolle töten).
- **Konsistenz-Audit**: alle Stellen, die den alten G145-Vorteil behaupteten, korrigiert
  (`g139`, `g140`, `g145`, das Oszillator-Pattern-Doc, FINDINGS_SUMMARY Addendum 5); doppeltes `g49` entfernt;
  2 veraltete Physik-Tests sauber als `xfail` markiert (Suite grün: 198 passed, 2 xfailed).
- **Wiederverwendbares Asset**: numba-JIT-SA (~100× schneller) für künftige große-n-Optimierung.

---

## 5. Wo das Programm jetzt steht (ehrlich, alle Fäden)
| Faden | Status |
|-------|--------|
| Gedächtnis (Aktivität) | **NEGATIV geschlossen** — kein stabiler Blank-Zustand (G83–G96). |
| Gedächtnis (Materie-Position) | **POSITIV, eng** — getriebene Materie als selektiver, persistenter Multi-Bit-Speicher (G114–G119). |
| Kommunikation | **POSITIV, eng** — ko-lokierter Echtzeit-Codec; kein Transport über Distanz (G97–G105). |
| Berechnung/Optimierung | **EQMOD negativ; benachbarte CIM-Hardware konkurrenzfähig, aber SA ist am besten** (G145→G153). |
| Kognition: zeitlicher Kredit | **Engpass = Architektur (ungated), nicht die Lernregel** (BET-144/145); gated-Zelle ungetestet (BET-146). |

**Programm-weites, ehrliches Fazit:** Die Physik ist **überall, wo getestet, dekorativ**; klassische
Standard-Methoden tragen jeden Gewinn. Das Deliverable war — wie die README sagt — nie der Erfolg der
Simulation, sondern der **strenge, selbst-korrigierende Prozess**: diese Session hat ihn benutzt, um eine
*Über*-Behauptung zurückzunehmen (eine vorzeichen-fehlerhafte Baseline), statt eine zu machen.

---

## 6. Offene Punkte (für deine Überlegung — ich entscheide nichts davon allein)
- **BET-146 (gated cell):** vorregistriert, Code bereit, **ungelaufen**. Klärt, ob eine gated Zelle den
  Gedächtnis-Horizont verlängert (bestätigt die BET-145-Diagnose). Etablierte Lösung, kein neues Mathe.
- Die Substrat-Physik-Fäden sind erschöpft; weitere Experimente dort wären Wiederholung oder Budget-Fischen.

Das ist alles. Ich höre hier auf, wie du gesagt hast.
