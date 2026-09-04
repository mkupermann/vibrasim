# Vibrasim II: Forschungs-Neustart, sicherer Laborbetrieb und beobachtende 3D-Ansicht

**Status:** freigegeben für die Implementierungsplanung am 2026-09-04
**Owner:** Michael Kupermann
**Datum:** 2026-09-03
**Arbeitsbranch:** `work/vibrasim2-research-reset`

**Freigabeumfang:** lokale Implementierungsplanung und anschließende lokale
Umsetzung. Die Freigabe autorisiert weder einen wissenschaftlichen P0-Lauf noch
Push, Veröffentlichung, Lizenzentscheidung oder Branch-Protection-Änderung.

**Planungsreview:** Die am 2026-09-04 ergänzten Klarstellungen operationalisieren
Konfigurationsnachweis, Budgetgrenze, Viewer-Abschluss und README-Reproduzierbarkeit.
Sie ändern weder P0-Modell, Fixture, Schwellen noch Verdict-Tabelle.

## 1. Entscheidung

Vibrasim II/P0 wird die einzige aktive Forschungsrichtung. Vibrasim I bleibt vollständig als historisches Labor erhalten, erhält aber keine weiteren Runs. Der Entwurf BP-C6c/G175 wird als nicht ausgeführter Designgedanke archiviert.

Diese Entscheidung wertet Vibrasim I nicht als gescheitert. Vibrasim I hat eine belastbare Grenze geliefert: Materiestruktur kann unter eng definierten Bedingungen Information tragen; freie Spezialisierung zu „Talent“ wurde nicht gezeigt. G175 würde nur mechanische Lesbarkeit prüfen und damit die geschlossene Talentfrage nicht beantworten. Außerdem ist der Entwurf vor einer Ausführung intern nicht eindeutig, weil er zunächst `k_h = 8` und anschließend `k_h = 40` festlegt.

Vibrasim II setzt tiefer an. P0 prüft genau eine Grundlage: ob ein energieerhaltender, wechselseitiger Feld-Materie-Kanal einen reproduzierbaren, topologieabhängigen Energietransfer erzeugt. Ein PASS erlaubt nur die Konzeption von P1. Es ist kein Nachweis für Persistenz, Individuation, Gedächtnis, Talent oder Leben.

## 2. Belegte Ausgangslage

Die folgenden Aussagen beruhen auf direkter Prüfung des Repository-Standes `20541df0`:

- `docs/vibrasim2/CHARTER.md` erklärt Vibrasim II zum aktiven Prototypen und ersetzt weitere Vibrasim-I-Experimente.
- `AGENTS.md`, `docs/BELIEF_PATH.md`, `FRONTIER.md` und der Anfang des `README.md` bezeichnen weiterhin den Vibrasim-I-Belief-Path als aktiv.
- `FRONTIER.md` ist älter als das letzte protokollierte G174-Ergebnis. Damit ist die eigene D10-Regel „LOGBOOK + FRONTIER in einem Commit“ nicht eingehalten.
- BP-C6c/G175 ist ein Draft, kein freigegebenes Experiment.
- `vibrasim2/wireframe.py` enthält bereits einen bewusst „dummen“ PyVista-Renderer, der nur gelieferte Punkte, Kanten und Feldpfade zeichnet.
- Die dokumentierte schnelle Testsuite ist nicht sicher abgegrenzt. Unmarkierte Tests enthalten unter anderem Vier- und Zwölf-Stunden-Läufe sowie einen Ein-Million-Neuronen-Versuch.
- Im Repository ist kein CI-Workflow vorhanden. GitHub meldet für `main` keine Branch Protection und keine Statuschecks.
- Das README behauptet eine nicht vorhandene Lizenzdatei und enthält mehrere nicht mehr vorhandene interne Ziele.

**Unsicherheit:** niedrig. Die Aussagen sind direkt im Checkout beziehungsweise über GitHub-Metadaten nachgewiesen.

## 3. Umfang und Reihenfolge

Das Vorhaben wird in vier voneinander prüfbare Lieferblöcke zerlegt. Kein Block darf stillschweigend den wissenschaftlichen Scope des folgenden Blocks erweitern.

### Block A: Programm-Autorität und sichere Entwicklungsbasis

1. Den Wechsel zu Vibrasim II append-only im `LOGBOOK.md` dokumentieren.
2. `FRONTIER.md` auf P0 als einzige offene Frage aktualisieren.
3. `AGENTS.md` auf die neue Lesereihenfolge umstellen: Vibrasim-II-Charter, P0-Pre-Registration, Frontier, jüngster Logbook-Eintrag.
4. `BELIEF_PATH.md` und `DISCIPLINE_SHARP.md` nicht umschreiben, sondern am Anfang sichtbar als historisch/frozen kennzeichnen.
5. BP-C6c/G175 als „UNEXECUTED DRAFT — ARCHIVED“ kennzeichnen; Inhalt und Review-Historie bleiben erhalten.
6. Gefährliche oder externe Tests explizit markieren und aus dem Defaultlauf ausschließen.
7. Einen statischen Auditor ergänzen, der lange Laufzeiten, `Path.home()`-Ausgaben und große Ressourcenparameter in unmarkierten Tests beanstandet.
8. Einen minimalen, lockfile-basierten GitHub-Workflow für den sicheren Default-Testlauf, `git diff --check` und die Paketkonstruktion ergänzen. Er ist lokal reproduzierbar, aber wegen beweglicher Runner-Images und Action-Tags nicht vollständig hermetisch.

Block A erzeugt noch keine wissenschaftlichen Daten.

### Block B: P0 als isolierter, testbarer Kern

P0 wird als eigenes Unterpaket unter `vibrasim2/p0/` implementiert. Vibrasim-I-Code und `world/physics.py` werden nicht importiert oder verändert.

Vorgesehene Verantwortlichkeiten:

- `types.py`: unveränderliche Konfiguration, Zustände, Energie-Ledger und Resultattypen.
- `dynamics.py`: diskreter Integrator und Hamiltonian-Kopplung.
- `fixtures.py`: deterministische CYCLE-, BRANCH- und Kontrolltopologien.
- `verdict.py`: reine, geordnete PASS/NULL/INCONCLUSIVE/FAIL-Entscheidung.
- `runner.py`: Stage A, danach ausschließlich bei bestandenem Gate Stage B; persistiert Rohdaten und `result.json`.
- `cli.py`: bewusster Start, Ausgabepfad und optional `--observe`. P0 bietet
  keinen Seed-Parameter; die drei registrierten Quellzentren sind die
  deterministischen Replikate und werden immer vollständig ausgeführt.

Die Pre-Registration bleibt maßgeblich. Implementierungstests dürfen ihre Schwellen nicht ersetzen oder nach einem Run verändern.

### Block C: Beobachtende 3D-Ansicht

Die 3D-Ansicht ist ein Messfenster, kein Teil des Experiments und kein Verdict-Instrument.

Der Simulatorprozess bleibt autoritativ. Er persistiert wissenschaftliche
Snapshots unverändert alle zehn Simulationsticks, wie in P0 registriert. Erst
danach übergibt er eine Kopie des jeweiligen Snapshots an einen separaten
Viewerprozess. Der Darstellungsweg erzeugt keine zusätzlichen wissenschaftlichen
Messpunkte und ändert deren Takt nicht.

Der Viewerprozess wird über einen `multiprocessing`-Kontext mit der plattform-
sicheren Startmethode `spawn` und einer importierbaren Top-Level-Entry-Function
gestartet. Ein versioniertes `ObservationEnvelope` enthält ausschließlich
serialisierbare NumPy-Arrays und neutrale Laufmetadaten. Eine Queue mit
`maxsize=1` wird niemals blockierend beschrieben: `put_nowait`; bei `Full` wird
der vorhandene Darstellungsframe per `get_nowait` best-effort verworfen und der
neue Frame erneut per `put_nowait` angeboten. Schlägt auch das fehl, wird nur
der neue Darstellungsframe verworfen und der Drop-Zähler erhöht. Die Simulation
wartet niemals auf den Viewer.

Der Viewer darf:

- die in Abschnitt 6 definierte 3D-Beobachtungsprojektion der realen
  P0-Zustandswerte darstellen;
- tatsächlich gelieferte Kopplungskanten als Linien darstellen;
- neutrale Ausführungsdaten zeigen: Experiment-ID, Stage, Arm, registriertes
  Quellzentrum, Tick, Simulationszeit, Frame-Alter und RUNNING/COMPLETE;
- Kamera, Zoom und das Einfrieren der sichtbaren Ansicht erlauben.

Der Viewer darf nicht:

- Oberflächen, Organismen oder Bindungen aus räumlicher Nähe ableiten;
- Zwischenzustände interpolieren oder fehlende Geometrie ergänzen;
- Erfolg, „Fortschritt“ oder Emergenz durch Größe, Leuchten oder organische Formen suggerieren;
- die Simulation pausieren, schrittweise weiterschalten, Parameter ändern oder einen Lauf neu starten;
- Livebilder als Acceptance-Metrik verwenden;
- vor Abschluss der registrierten Entscheidung ein PASS/NULL-Signal anzeigen.

Die sichtbare Pause friert nur die Ansicht ein. Die Simulation läuft weiter.
Nach Abschluss liest ein Replay ausschließlich das append-only persistierte
Snapshot-Journal; die verlustbehaftete Live-Queue ist niemals Replay-Quelle.
Während des Laufs trägt jede Live-Ansicht sichtbar den Hinweis
`RAW SIMULATION STATE — OBSERVATION ONLY — VERDICT PENDING`. Ein letzter
Live-Frame mit `VERDICT RECORDED IN result.json` bleibt wegen des bewusst
verlustbehafteten Kanals best effort und ist keine Abschlussgarantie. Der Replay-
Pfad liest `result.json` selbst und zeigt den Abschlussstatus nach erfolgreicher
Validierung zuverlässig; ohne gültige Ergebnisdatei behauptet er keinen Abschluss.

### Block D: README und öffentliche Repository-Oberfläche

Das README wird auf eine einzige gegenwärtige Geschichte reduziert. Ziel ist kein Marketingtext, sondern eine belastbare Einladung, das Denken und die Evidenz nachzuvollziehen.

Das Repository ist weder Kundenreferenz noch fertiges Produkt. Es ist ein
öffentliches Forschungslabor und soll sichtbar machen, wie Michael arbeitet:
Behauptungen präzisieren, Gegenbeweise vorab definieren, Ergebnisse festhalten
und Sackgassen nicht aus der Geschichte entfernen. Die Oberfläche wird deshalb
nicht auf Hochglanz bereinigt. Sie muss lediglich zuverlässig zwischen aktiver
Frage, belegtem Ergebnis, historischem Pfad und persönlicher Hoffnung
unterscheiden.

Die Hoffnung, dass aus der Arbeit etwas Eigenständiges entsteht, darf im README
ausgesprochen werden, aber nur als Hoffnung. Sie begründet weder eine
Erfolgsprognose noch einen größeren wissenschaftlichen Claim. Die passende
Haltung lautet sinngemäß: Ich weiß nicht, ob Vibrasim irgendwohin führt. Die
Frage ist mir wichtig genug, sie so präzise zu bearbeiten, dass sie auch
scheitern kann.

Vorgesehene Struktur:

1. Ein Satz: was Vibrasim II ist.
2. „Why I am doing this“ in Michaels Ich-Perspektive.
3. Die eine aktuelle Frage P0 und ihr enger Claim.
4. „What this is / is not“ mit klaren Grenzen.
5. Was das Vibrasim-I-Labor tatsächlich belegt hat, einschließlich NULLs und Retraktionen.
6. Ein funktionierender Minimalstart für den sicheren Testlauf und ein sichtbar
   als wissenschaftlich daten-erzeugend gekennzeichneter P0-Lauf nach dem
   Pre-Run-Gate.
7. Optionaler Start der 3D-Beobachtung, ebenfalls als daten-erzeugender P0-Lauf.
8. Links zu Charter, P0-Pre-Registration, Frontier, Logbook und historischem
   Vibrasim-I-Material. `BELIEF_PATH.md` und `DISCIPLINE_SHARP.md` werden an
   jeder öffentlichen Verlinkung sichtbar als historisch/frozen bezeichnet.

Experimentchronik, Bibliografie, Dashboard-Anleitung und historische Runbooks werden in passende Dokumente verschoben oder über bestehende Dokumente verlinkt. Git-Historie und Logbook bleiben die vollständige Provenienz.

Der Zieltext bleibt in Englisch, weil Repository und externes Publikum englischsprachig sind. Die Stimme folgt diesen Regeln:

- erste Person statt institutioneller Sprache;
- konkrete Eingeständnisse statt Disclaimer-Floskeln;
- klare Grenzen vor Erfolgsbehauptungen;
- NULL, FAIL und Retraktion als Ergebnisse, nicht als peinliche Fußnoten;
- keine Superlative, Erfolgswahrscheinlichkeiten oder erfundenen Zukunftsbilder;
- keine Nennung von ChatGPT, Codex, OpenAI oder „AI“ als Autor oder Bearbeiter;
- keine persönlichen Erfahrungen oder Entscheidungen behaupten, die Michael nicht selbst getroffen hat.

Ich-Aussagen sind auf Entscheidungen, Beobachtungen und Retraktionen begrenzt,
die durch Michaels Logbook-Einträge oder Commits belegt sind. Implementierungs-
und Run-Behauptungen bleiben neutral (`the repository implements`, `the run
recorded`), solange keine persönliche Prüfung durch Michael dokumentiert ist.

Die README-Eröffnung enthält vier konkrete Anker: das Problem, durch das Michael
sich nicht bluffen kann; Nomenklatur statt Ontologie; Deadlocks als Material;
und genau ein letztes aufgezeichnetes, nachprüfbares PASS-, NULL- oder FAIL-
Ergebnis. Solange P0 noch kein Resultat besitzt, ist dies G174 und wird ausdrücklich
als historisches Vibrasim-I-Ergebnis bezeichnet. Dadurch bleibt die Stimme
spezifisch und fällt nicht in allgemeine Manifest-Sprache zurück.

Der Kern der Stimme bleibt: Ich habe ein Problem gewählt, durch das ich mich nicht bluffen kann; die Namen im Modell sind Nomenklatur, keine Ontologie; die Deadlocks sind das Material.

## 4. P0-Scope-Korrektur vor Daten

Der Vibrasim-II-Charter verlangt endliche Bindungslebensdauer und lokalen Energieverbrauch bei Bindungsbildung. P0 verwendet dagegen feste, vorgegebene Kanten. Das ist für einen Kopplungs-Verifikator sinnvoll, muss aber ausdrücklich begrenzt werden.

Die als `FROZEN ON COMMIT` markierte P0-Pre-Registration wird nicht still
umgeschrieben. Vor Implementierung und erstem Run wird ein versioniertes,
ebenfalls vor Daten eingefrorenes Protokoll-Addendum
`docs/amendments/v2_p0_scope_addendum.md` erstellt. Es verweist auf das Original,
belässt sämtliche Modelle, Fixtures, Schwellen und Verdict-Prädikate unverändert
und präzisiert ausschließlich den Geltungsbereich:

- P0-Kanten heißen `supplied coupling edges`, nicht entstandene oder persistente Bindungen.
- Sie sind ein deterministischer Prüfkörper für Energieerhaltung, Kausalrichtung und Topologieempfindlichkeit.
- Sie sind ausschließlich in P0 von Bildungskosten und endlicher Lebensdauer ausgenommen.
- Ein P0-PASS sagt nichts über die P1-Anforderungen Bindungsbildung, Turnover und Persistenz aus.
- Ab P1 gelten die Charter-Regeln ohne diese Ausnahme.

Diese Präzisierung erfolgt vor Daten und ändert keine registrierte Schwelle. Eine Integration von Bindungsbildung und Lebensdauer bereits in P0 wird verworfen, weil sie mehrere Mechanismen gleichzeitig öffnen und die Aussage des Verifikators verwischen würde.

## 5. Datenfluss und Isolation

```text
P0 config + registered source centres
        |
        v
authoritative simulator  ---> raw observations ---> pure verdict ---> atomic result.json
        |
        +--- copied snapshots ---> best-effort latest queue ---> PyVista viewer process
                                     (drop stale)              (read-only)
```

Wissenschaftliche Resultate entstehen ausschließlich aus den persistierten
Rohbeobachtungen. Die reine Verdict-Funktion konsumiert diese Records; erst
danach wird ein `result.json` mit Verdict atomar geschrieben und unabhängig
wieder eingelesen. Der Viewer konsumiert Kopien und hat keinen Rückkanal. Ein
Viewer-Absturz darf den Run nicht abbrechen. Ein voller oder geschlossener
Viewerkanal wird als Darstellungsereignis protokolliert, nicht als
wissenschaftlicher Fehler.

## 6. Terminologie und visuelle Ehrlichkeit

P0 ist ein zweidimensionales Gitter mit skalaren Feldverschiebungen `u_x` und
sechs skalaren Materieoszillatoren `q_i`; es enthält weder bewegte 3D-Partikel
noch berechnete Feldstromlinien. Die Ansicht heißt deshalb ausdrücklich
`3D observation embedding`, nicht 3D-Welt.

Die producer-seitige, deterministische Projektion ist vollständig deklariert:

- Feldgitterpunkt `x=(x_1,x_2)` wird als `(x_1, x_2, S·u_x)` dargestellt.
- Materieoszillator `i` wird am registrierten Kopplungsort als
  `(s_i.x, s_i.y, S·q_i)` dargestellt.
- Dünne Feldgitter-Polylinien verbinden ausschließlich registrierte periodische
  Nachbarn; Materiekanten verbinden ausschließlich die im Arm gelieferte Edge-Liste.
- Eine vertikale Kopplungslinie verbindet `S·u_{s_i}` mit `S·q_i` am selben
  Kopplungsort und zeigt damit nur die tatsächlich im Hamiltonian enthaltene
  Differenz.
- `S` ist ein fester, im Screenshot sichtbarer Displaymaßstab. Er geht weder in
  Messung noch Verdict ein. Achsen werden als Gitterkoordinate, Gitterkoordinate
  und Modellverschiebung × Displaymaßstab beschriftet.

Der Adapter erzeugt diese Polylinien aus den vom Simulator gelieferten
Zustandsarrays und der registrierten Gitteradjazenz. Der PyVista-Renderer zeichnet
nur die gelieferten Polylinien und leitet selbst keine Geometrie ab.

Der bestehende Typ `WireframeFrame` verwendet `bonds`, obwohl P0 nur gelieferte
Kopplungskanten besitzt. Vor dem ersten P0-Frame wird die frühe Schnittstelle auf
neutrale `edges`/`edge_states` umgestellt. Ein neutraler Zustand `SUPPLIED`
kennzeichnet die P0-Fixture mit genau einer festen, wertungsfreien Farbe.
`FORMING`, `STABLE` und `BREAKING` sowie ihre Lifecycle-Farben bleiben für spätere
Mechanismen reserviert, die diese Zustände tatsächlich berechnen. Der
Visualisierungsvertrag im Charter und seine Tests werden im selben Commit
entsprechend präzisiert.

Das vorhandene morphodynamische Konzeptbild bleibt als klar gekennzeichnete Designvision erhalten. Es darf nicht im Ergebnisbereich oder als Illustration eines realen Runs erscheinen. Reale Screenshots nennen Experiment, Stage, Arm, registriertes Quellzentrum und Simulationszeit.

## 7. Teststrategie

### Sicherer Default

Der normale lokale und CI-Testlauf schließt mindestens diese Marker aus:

- `experiment`: führt einen wissenschaftlichen Run aus oder erzeugt persistente Forschungsdaten;
- `slow`: für den schnellen Feedbackzyklus ungeeignet;
- `external`: benötigt Netzwerk, Hardware, Datenbestand oder Benachrichtigungssystem;
- `resource_intensive`: hoher Speicher-, CPU- oder Laufzeitbedarf.

Explizite Experimentläufe benötigen einen bewusst gewählten Marker oder ein dafür vorgesehenes Runner-Kommando. Ein nacktes `pytest` darf keinen stundenlangen Run und keinen Schreibzugriff auf `~/.eqmod` auslösen.

### P0-Kern

- Energieidentitäten und diskrete Konvergenz werden mit kleinen deterministischen Fixtures getestet.
- Jede Pre-Registration-Armkonfiguration erhält mindestens einen Konstruktionstest.
- Die Verdict-Funktion wird tabellengetrieben über jede geordnete Entscheidungskante getestet.
- Stage B darf technisch nicht starten, wenn Stage A nicht bestanden ist.
- Rohdaten und `result.json` werden unabhängig erneut gelesen und bewertet.

### Observer-Isolation

- Headless und `--observe` müssen für dieselbe registrierte Konfiguration
  denselben kanonischen Digest der geordneten wissenschaftlichen Records und
  dasselbe Verdict erzeugen. Wallclock-, GUI- und Frame-Drop-Metadaten sind
  ausdrücklich nicht Teil dieses Digests.
- Ein voller Framekanal darf den Simulator nicht blockieren.
- Ein beendeter Viewerprozess darf den Simulator nicht abbrechen.
- Ungültige Viewer-Payloads werden nur im Darstellungsweg verworfen und
  protokolliert. Sie filtern, reparieren oder klassifizieren niemals persistierte
  wissenschaftliche Records; deren Validitätsgates liegen ausschließlich im
  P0-Runner und in der Pre-Registration.
- Pause und Replay dürfen keine Simulationsfunktion aufrufen.
- Projektion, Payload-Validierung, Queue-Eviction, Cadence und Controller werden
  display-unabhängig in CI getestet. Reale PyVista/OpenGL-Smokes sind opt-in und
  werden praktisch auf macOS und Windows geprüft.
- Shutdown wird explizit getestet: Der Simulator schließt nach dem letzten
  persistierten Record den Kanal, wartet begrenzt auf den Viewer und beendet bei
  Bedarf ausschließlich den Viewerprozess.

Vollständige wissenschaftliche P0-Runs gehören nicht in CI. CI prüft Mechanik, Invarianten, Entscheidungscode und Isolation.

## 8. Fehlerbehandlung

- Numerische Nicht-Endlichkeit, gebrochene Energieidentität oder ungültige Fixture-Geometrie stoppt den betroffenen Stage gemäß Pre-Registration.
- Viewerfehler werden separat protokolliert; der Run bleibt gültig, sofern Rohdatenpfad und Simulation unbeeinflusst sind.
- Fehlt eine erforderliche Rohbeobachtung oder kann `result.json` nicht atomar
  geschrieben und erneut gelesen werden, liegt kein abgeschlossener
  Experiment-Record vor. Das ist ein operativer Abbruch außerhalb der
  PASS/NULL/INCONCLUSIVE/FAIL-Tabelle, nicht ein zusätzliches Verdict. Vor einem
  erneuten Run wird die Ursache dokumentiert; Daten werden nicht rekonstruiert.
- Ein README-Beispiel wird nur aufgenommen, wenn der genaue Befehl auf einem sauberen Checkout verifiziert wurde.

## 9. Repository-Hygiene innerhalb dieses Vorhabens

Enthalten:

- kaputte README-Links entfernen oder auf existierende Ziele korrigieren;
- Legacy-Reproduktionsbefehle mit dem korrekten Substrat versehen oder in das historische Runbook verschieben;
- harte lokale Datenbankexposition mindestens auf Loopback beschränken;
- Projektstatus, Testzahlen und CI-Aussagen nur dann nennen, wenn sie beim Abschluss erneut gemessen wurden;
- veraltetes Windows-Setup nicht mehr als aktuellen Forschungsweg darstellen.

Nicht enthalten:

- keine Löschung historischer Daten, Runs, Modelle oder Branches;
- keine Umbenennung des gesamten Python-Distributionspakets;
- keine Wiederaufnahme von VSA, Reservoir, Brian2, LLM oder anderen Archivpfaden;
- keine Branch Protection oder Veröffentlichung auf GitHub ohne abschließende Bestätigung;
- keine rechtlich bindende Lizenzentscheidung. Die vorhandene widersprüchliche Lizenzbehauptung wird vor einer öffentlichen Änderung Michael zur konkreten Entscheidung vorgelegt.

## 10. Abnahmekriterien

Das Vorhaben ist abgeschlossen, wenn:

1. genau eine aktive Frage in AGENTS, Frontier, README und Logbook identisch benannt ist;
2. P0s Fixture-Ausnahme vor Daten eindeutig dokumentiert ist;
3. der Default-Testlauf nachweislich keine Experiment-, External- oder Resource-Intensive-Tests ausführt;
4. die Befehle des sicheren CI-Workflows lokal erfolgreich sind; die GitHub-Ausführung bleibt bis zu einem autorisierten Push extern unbestätigt;
5. P0-Kern und reine Verdict-Funktion die registrierten Mechaniktests bestehen;
6. `--observe` reale Snapshots zeigt, ohne Rohdaten oder Verdict gegenüber Headless zu verändern;
7. Viewer-Abbruch und Frame-Überlast den wissenschaftlichen Run nicht stoppen;
8. das README das Repository als öffentliches Forschungslabor statt als Produkt
   oder Kundenreferenz einordnet, seine Befehle auf einem sauberen Checkout
   geprüft sind und keine nicht belegten Claims enthält;
9. der Git-Diff keine unbeabsichtigten Änderungen historischer Daten enthält;
10. vor Push, Lizenzänderung und Branch-Protection jeweils eine konkrete Freigabe vorliegt.

## 11. Wesentliche Risiken

- **Scope creep:** Eine schöne Darstellung kann leichter wachsen als der P0-Kern. Gegenmaßnahme: Renderer konsumiert nur die minimale Snapshot-Schnittstelle.
- **Observer effect:** Serialisierung und GUI dürfen den Lauf nicht beeinflussen. Gegenmaßnahme: separater Prozess, latest-only Queue und Headless/Observe-Gleichheitstest.
- **Visuelle Überinterpretation:** Menschen lesen Formen schneller als Tabellen. Gegenmaßnahme: rohe Geometrie, neutrale Terminologie und sichtbarer Observation-only-Hinweis.
- **Historische Umschreibung:** Eine neue Richtung darf alte NULLs nicht nachträglich heilen. Gegenmaßnahme: append-only Transition und Frozen-Hinweise statt Textbereinigung vergangener Verdicts.
- **Überpolitur:** Ein zu glattes README würde genau die Arbeitsweise verdecken,
  die das Repository nach außen zeigen soll. Gegenmaßnahme: Widersprüche,
  unsichere Anweisungen und unklare Statussignale korrigieren, aber NULLs,
  Sackgassen und die Entwicklung des Denkens sichtbar lassen.
- **Plattformverhalten:** PyVista und Prozess-Start unterscheiden sich zwischen macOS und Windows. Die Architektur ist plausibel, aber die vollständige GUI-Funktion muss auf beiden Zielsystemen praktisch geprüft werden. **Unsicherheit:** mittel, bis beide Plattformen gelaufen sind.

## 12. Budgetgrenze

Die Blöcke A, C und D sind nicht-experimentelle Infrastruktur und zählen nicht
in das eingefrorene P0-Laufbudget. Sie erzeugen keine P0-Daten und dürfen weder
Modell, Schwellen noch Verdict-Tabelle verändern. Block B ist die in P0
registrierte Implementierung. Überschreitet Block B den vorhandenen Hard Cap,
wird vor Daten abgebrochen und eine versionierte Nachfolge-Registration mit
realistisch neu begründetem Budget eingefroren; es gibt keine stille Verlängerung.
Beginn, Ende und kumulierte Dauer von Block B werden in einem versionierten,
maschinenlesbaren Ledger festgehalten. Der produktive P0-Start und das Pre-Run-
Gate lehnen einen offenen oder überschrittenen Ledger-Status ab.

## 13. Auslieferung

Die Implementierung erfolgt in kleinen lokalen Commits auf dem Arbeitsbranch. Wissenschaftliche Runs starten erst nach abgeschlossener P0-Implementierung, bestandener Testisolation und erneuter Prüfung der Pre-Registration. Es erfolgt kein automatischer Push und keine Änderung öffentlicher GitHub-Einstellungen. Vor diesen extern sichtbaren Schritten wird der konkrete Diff, der Testnachweis und die verbleibende Unsicherheit vorgelegt.
