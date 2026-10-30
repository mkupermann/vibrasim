# G176 / L0 — Kontinuierliche Versuche und erfahrungsabhängiges Verhalten

Stand: 16.09.2026. Status: Forschungskandidat implementiert und technisch geprüft;
kein registrierter Forschungslauf und kein nachgewiesener Lernerfolg.
Der Folgeauftrag „Go“ umfasst Kern, Prüfer, technische Tests und Ressourcenmessung.
Dieses Dokument ersetzt den Drei-Ton-Ansatz des L0-Entwurfs vom 06.09.2026.
Es ist eine separate L0-Entwicklung, keine Fortsetzung oder Umdeutung von P0–P3.
Vor einem Forschungslauf müssen Implementierung und Messvertrag zusammen mit
ihren Hashes eingefroren werden; bis dahin ist dies kein abgeschlossener Run-Vertrag.

## 1. Entscheidung und Aussagegrenze

Ich untersuche zuerst, ob passend zugeordnete Rückmeldung eine dauerhafte,
übertragbare Verhaltensänderung bewirkt. Eine Oberfläche mit Kamera und Mikrofon
kommt erst nach diesem Nachweis. Das langfristige Ziel bleibt ein offenes,
nicht auf feste Antwortklassen beschränktes Erfahrungslernen ohne LLM.

Der erste Versuch prüft nur kontinuierliche, kontextabhängige Tonsteuerung.
Er belegt weder selbst gewählte Ziele noch Sprache, Verständnis, Bewusstsein,
multimodales Lernen oder eine neue mathematische Methode.

P0 NULL, P1 UNRESOLVED, P2 INCONCLUSIVE und der technische P3 PASS bleiben
unverändert. Die L0-Regel wird nicht als physikalisch emergenter Substratprozess
ausgegeben. Sie nutzt die Konzepte begrenzter Erfahrungsspeicherung und einer
zeitlich abklingenden Zuordnungsspur; eine Integration in historische STDP-,
BTSP- oder SubstrateLibrary-Implementierungen ist damit nicht behauptet.
Es werden keine neuronalen Zusatzschichten oder vortrainierten Modelle eingebaut.

## 2. Ein- und Ausgabe ohne vorgegebene Antworten

- Eingang des ersten Rechentests: ein dimensionsloser Messwert x in [0,1].
  Er ist ein vereinfachter Sensorkanal, kein Objektlabel oder vortrainiertes Merkmal.
- Handlung: eine frei gezogene reelle Zahl a in [0,1]. Die Aktuatorabbildung
  lautet f(a) = 200 * 8^a Hz. Jeder darstellbare Zwischenwert ist zulässig.
  Es gibt keine drei Klassen, Antwortliste oder Bedeutungszuordnung im Kern.
- Ein Versuch entspricht zunächst einem 0,2-s-Ton mit festem Ein-/Ausblenden.
  Die Beschränkung auf einen Stellwert erleichtert den ersten kausalen Nachweis;
  mehr Stellwerte und variable Wellenformen sind spätere eigene Fragen.
- Im Rechentest wird kein Lautsprecher geöffnet. Ein späterer Audioadapter
  startet nur ausdrücklich, begrenzt digitale Amplitude auf 0,05 und besitzt
  einen Stoppschalter. Dies ist keine Garantie für einen sicheren Schalldruck;
  die Hardwarelautstärke muss separat eingestellt werden.
- Rückmeldung ist ein explizites Ereignis (attempt_id, r, delay), r in [-1,1].
  Keine Rückmeldung ist kein Ereignis und insbesondere nicht r=0.
  r=0 bedeutet hier ausdrücklich neutrale Bewertung; ein früher besprochener
  Tastencode „0 = negativ“ würde vom UI als r=-1 umgesetzt. Keine stillschweigende
  Gleichsetzung von Tastencodes, Gefühlen und numerischem Feedback.
- Der Kern sieht ausschließlich x, seine eigene Handlung und zugehöriges Feedback.
  Zielhandlung, Bewertungsfunktion, Testlabels und Prüfsplit erhält er nicht.

## 3. Ein vollständig bestimmter Kandidat K1

K1 ist ein begrenztes episodisches Bewertungsmodell mit kontinuierlicher Suche.
Es ist ausdrücklich keine Neuheitsbehauptung. Die eigene Erfahrung darf gespeichert
werden; verboten sind eine vom Prüfer gelieferte Muster-Antwort-Tabelle und
verdeckter Zugriff auf die Sollhandlung.

### Zustand und Konstanten

Dauerhaft: geordneter Speicher M von höchstens 4096 Tupeln (x_i, a_i, q_i),
ID-Zähler und Trainings-Zufallszustand. Initial M leer und Zähler 0.
q_i liegt in [-1,1]. Ein Eintrag ist ein bewerteter eigener Versuch, keine Klasse.

Kurzlebig: höchstens 64 offene Versuche mit ID, x, a und Erzeugungszeit.
Im Prüfmodus gibt es keine offenen Lernversuche und keine Zustandsänderung.
Separate Zufallsströme für Handlungssuche, Trainingsdaten, Feedbackvertauschung
und Prüfung verhindern versehentliche Kopplung. PRNG: NumPy PCG64.

Konstanten: h_x=0,15; h_a=0,10; eta=0,5; tau=10 Sekunden;
alpha=1; epsilon=0,20; 64 neue Handlungsvorschläge pro Versuch.
Die Werte sind Designentscheidungen vor Daten, keine optimierten Werte.

### Handlung erzeugen

Für jeden Versuch werden 64 neue Vorschläge unabhängig gleichverteilt aus [0,1]
gezogen. Es ist kein dauerhaftes Menü: im nächsten Versuch werden neue Werte gezogen.
Für jeden Vorschlag a gilt:

    k_i(x,a) = exp(-0,5*((x-x_i)/h_x)^2 - 0,5*((a-a_i)/h_a)^2)
    Q(x,a) = sum_i(k_i*q_i) / (alpha + sum_i(k_i))

Mit Wahrscheinlichkeit epsilon wird der erste zufällige Vorschlag ausgegeben,
sonst der Vorschlag mit dem höchsten Q; bei Gleichstand gewinnt der zuerst
gezogene. Bei leerem Speicher sind alle Q=0, also ist die Ausgabe zufällig.
alpha hält nicht belegte Regionen nahe neutral; das ist eine eingebaute Annahme.
Für den Trainingsversuch werden x und die tatsächlich ausgegebene Handlung unter
einer neuen attempt_id zwischengespeichert. Keine Zielhandlung beeinflusst die Suche.

### Erfahrung speichern und verspätetes Feedback behandeln

Ein Feedbackereignis muss auf genau einen offenen Versuch zeigen. Delay wird aus
monotonen Zeitstempeln geprüft und muss in [0,30] Sekunden liegen. Zukünftige,
unbekannte, bereits bewertete oder abgelaufene IDs werden zurückgewiesen und geloggt.
Mehrere Bewertungen desselben Versuchs sind kein stärkeres oder mehrfaches Lernen.

Bei gültigem Ereignis:

    e = exp(-delay/tau)
    q_new = eta * e * r
    M := M angehängt um (x_attempt, a_attempt, q_new)

Der offene Versuch wird entfernt. Bei vollem M wird vor dem Anhängen genau der
älteste bewertete Eintrag entfernt (FIFO). Bei 64 offenen Versuchen blockiert eine
weitere Aktion mit explizitem Kapazitätsfehler; es gibt kein stilles Überschreiben.
Ohne Feedback läuft nur die kurzlebige Frist ab; M bleibt unverändert.

Widersprüchliche Bewertungen verschiedener Versuche werden beide gespeichert.
Bei identischem (x,a), unmittelbarem r=+1 und späterem r=-1 sind die Beiträge
+0,5 und -0,5: am identischen Prüfpunkt ist Q=(0,5-0,5)/(1+1+1)=0.
Die Regel erfindet keine Auflösung des Widerspruchs. Die Frequenz gleicher
Bewertungen beeinflusst Q; auch das ist eine zu prüfende Annahme.

### Handrechenbare Grenzen

Ein einziger Versuch am identischen späteren Prüfpunkt hat k=1:

| Feedback | Gespeichertes q | Q am selben Punkt |
|---|---:|---:|
| +1 sofort | +0,5 | +0,25 |
| -1 sofort | -0,5 | -0,25 |
| neutral 0 | 0 | 0, aber ein bewerteter Eintrag vorhanden |
| keines | kein Eintrag | 0 bei weiterhin leerem M |
| +1 nach 10 s | 0,5/e | 0,25/e, etwa 0,09197 |

Q ist eine durch Erfahrung geänderte Bewertungsfläche, kein Erfolgsnachweis.
Dass eine positive Bewertung die lokale Bewertung erhöht, reicht allein nicht
als Lernnachweis: Entscheidend ist das Verhalten bei zurückgehaltenen Eingaben.

Speichern/Neustart erhält M, IDs, Konstanten und Trainings-PRNG bitgetreu.
Offene Versuche werden beim Neustart verworfen und protokolliert, weil die
monotone Uhr nicht über Prozessgrenzen fortgeschrieben wird. Prüfung verwendet
eine Kopie von M und einen eigenen PRNG; Prüfen verändert den Trainingsstand nicht.

Arbeit pro Entscheidung O(64*|M|), Speicher O(|M|+64); kein unbeschränktes Wachstum.
Floating-point-Unterlauf des Kernels zählt als k=0; NaN/Inf sind Fehler.
Keine Laufzeit- oder Echtzeitgarantie ohne Messung. Zielbudget bleibt CPU, 2 GiB
Prozessspeicher und 100 MiB gespeicherter Zustand; Überschreitung wird ausgewiesen.

## 4. Messvertrag vor Implementierungsergebnissen

### Frage und getrennte Rollen

Hypothese: K1 erreicht bei neuen kontinuierlichen Eingaben bessere bewertete
Handlungen als derselbe Kern ohne Speicherung und mit falsch zugeordnetem Feedback.
Dieser Test misst Lernen einer extern bewerteten Beziehung, nicht eigene Zielbildung.

Nur der getrennte Prüfer kennt für Phase A a*(x)=0,2+0,6*x und für Phase B
a*(x)=0,8-0,6*x. Beide sind kontinuierliche Aufgaben, keine Tonklassen.
Bewertung: r = 1 - 2*min(abs(a-a*)/0,25, 1). Der Kern bekommt den Skalar erst
nach seinem Versuch und nie a*. Eine so einfache Funktion kann ein passender
bekannter Algorithmus ebenfalls lernen; K1 wird nicht deshalb als neu bezeichnet.

30 unabhängige Wiederholungen mit Master-Seeds 0 bis 29. Jeder Seed wird mit
SeedSequence in getrennte benannte Ströme aufgeteilt; die konkrete Zuordnung
wird im Implementierungsmanifest eingefroren. Pro Wiederholung identische
Kontextfolge für alle Arme, jeweils gleich viele Aktionen und Feedbackereignisse.

Phase A: 1200 Trainingsversuche mit x aus Uniform[0,1]. Prüfung: 200 andere,
vor Trainingsbeginn erzeugte x aus einem getrennten Strom; keine identischen
Trainingswerte und keine Updates. Delay wird je Versuch unabhängig aus
Uniform[0,10] gezogen. Training erfolgt in Blöcken von 20 Versuchen wie unten
definiert; jeder Block endet vollständig vor dem nächsten.
Für erste und letzte Prüfung dieselben reservierten Kontexte, getrennte festgelegte
Aktionsströme; keine Ergebnisrückgabe an den Lernkern.

Arme:

1. K1 vollständig.
2. Gleicher K1, Speicherung gesperrt; Feedback wird gezählt, aber nicht übernommen.
3. K1 mit vertauschtem Feedback: je 20 Versuche Bewertungen sammeln und mit einer
   zufälligen Derangement-Permutation den anderen Versuchen zuordnen. Dafür auch
   im Vollarm in 20er-Blöcken erst nach Aktionsausgabe speichern; identische
   Verzögerungswerte der ursprünglichen Versuche verwenden. Kein Datenzugriff
   zwischen Armen. Delay ist hier simulierte Zeit, nicht Block-Rechenzeit.
4. Uniforme Zufallshandlung als einfache Referenz.
5. Erfahrungsbasierte einfache Alternative: aus bisher positiv bewerteten
   eigenen Versuchen die Handlung mit nächstem x wiederverwenden; ohne positiven
   Eintrag uniform ziehen. Gleiche Feedbackblöcke, FIFO-Grenze und Datenbudgets.

Der Blockmodus aus Punkt 3 gilt verbindlich für alle lernenden Arme und geht der
sequenziellen Sofortverarbeitung im allgemeinen Kernelbetrieb vor. Im Test sind
20 offene Versuche erlaubt. Alle Aktionen eines Blocks haben denselben virtuellen
Erzeugungszeitpunkt; nach Festlegung aller Aktionen werden die Feedbackereignisse
nach virtueller Empfangszeit sortiert zugestellt (bei Gleichstand nach attempt_id).
Damit wird die Verzögerungsprüfung unverändert angewendet. Der nächste Block
startet eine virtuelle Sekunde nach dem letzten Ereignis. Rechenzeit und reale
Audiolatenz werden daraus nicht abgeleitet.

Jede Wiederholung liefert den mittleren Prüfreward J je Arm. Bericht enthält
alle 30 Werte, Mittelwert und Standardabweichung sowie gepaarte Differenzen.
Für den Mittelwert der gepaarten Differenzen: zweiseitiges 95%-t-Intervall
mit 29 Freiheitsgraden, kritischer Wert 2,045229642. Dies setzt unabhängige
Wiederholungen voraus und ist keine allgemeine Garantie außerhalb der Aufgabe.

### Kriterien und Reihenfolge

- FAIL: Zugriff des Kerns auf Sollhandlungen/Testfeedback; ungültige IDs;
  Änderungen im Prüfmodus; fehlende Daten; NaN/Inf; nicht registrierte Konfiguration;
  Verletzung des Ressourcen- oder Zeitlimits. Fehler nicht als wissenschaftliches NULL ausgeben.
- INCONCLUSIVE: weniger als 30 vollständig gültige Wiederholungen durch einen
  externen Abbruch oder eine nicht auswertbare Unsicherheitsrechnung. Keine
  selektive Auswertung nur erfolgreicher Seeds.
- PASS-LERNEN nur gemeinsam: mittleres J von K1 mindestens 0,50; mittlere
  Differenz gegen den gesperrten und den vertauschten Arm jeweils mindestens
  0,10; beide unteren Intervallgrenzen größer als 0; gesperrter und vertauschter
  Arm erreichen nicht die absolute 0,50-Schwelle.
- Sonst NULL für diesen Kandidaten unter diesem Vertrag. Ein Kontrollarm über
  der Schwelle wird als fehlende kausale Trennbarkeit berichtet, nicht verschwiegen.
- VORTEIL gegenüber der einfachen Erfahrungsreferenz nur separat, wenn ihre
  gepaarte mittlere Differenz mindestens 0,05 und untere Intervallgrenze größer
  als 0 ist. Ihr Erfolg ist legitim; ein fehlender K1-Vorteil widerlegt nicht Lernen.

Schwellen sind vor Daten gewählte Mindestanforderungen, keine Naturkonstanten.
Es gibt keine nachträgliche Anpassung, keine Suche auf den Prüfdaten und keine
Best-of-Seed-Auswahl. Ein NULL erlaubt keine automatische weitere Variante.

### Behalten und Umlernen separat

Nach Phase A: Zustand speichern und neu laden. Bei identischem Prüf-PRNG müssen
Handlungen und Bewertungen exakt übereinstimmen; Speichergleichheit allein reicht
nicht. Dann 1200 Versuche Phase B mit identischen Budgets, neue Trainingsdaten.
Erneut A und B ohne Updates prüfen. UMLERNEN nur bei J_B mindestens 0,50 und
Verbesserung gegenüber dem A-Zustand auf B mindestens 0,10. BEHALTEN nach B nur,
wenn J_A höchstens 0,10 unter seinem Wert vor B liegt. Beide Werte berichten.
Da sich A und B für dasselbe x widersprechen und kein Aufgabenindikator gegeben
wird, ist ein gleichzeitiger Erfolg nicht vorausgesetzt. Ein Scheitern des
Behalten-Kriteriums bezeichnet Interferenz, nicht einen Protokollfehler und
nicht automatisch Widerlegung des zuvor separat gemessenen Lernens.

## 5. Was dieser Entwurf nicht vorgibt

Sensorstruktur, Handlungssicherheit, Suchverteilung, Ähnlichkeitsmaß und
Bewertungsfenster sind konstruiert. Das System entdeckt weder seine Physik noch
die Bedeutung menschlicher Rückmeldung aus dem Nichts. Es erhält aber keine
richtige Antwort und keine endliche Liste vorab definierter Antworttöne.

K1 enthält bekannte Formen: Nachbarschaftsgewichtung, Exploration, episodische
Erfahrung und zeitliche Zuordnung. Die Literatur beschreibt bereits
verstärkungsmodulierte Plastizität mit abklingenden Spuren, z.B.
[Florian 2007](https://pubmed.ncbi.nlm.nih.gov/17444757/) und
[Legenstein et al. 2008](https://doi.org/10.1371/journal.pcbi.1000180).
Diese Quellen validieren weder K1 noch seinen Nutzen. K1 wird nicht als STDP-
Implementierung oder neue Mathematik ausgegeben. Der Neuheitsnachweis bleibt
offen; bekannte Bausteine unter einem neuen Namen erfüllen ihn nicht.

## 6. Nächste Lieferung und Stop

Als Nächstes: kleiner isolierter Kern und Prüfer gemäß diesem Dokument,
Grenz-/Leakage-/Persistenztests, dann Ressourcenmessung ohne Nutzung der
Prüfziele. Implementierungsbudget als Planungsgrenze: 60 Minuten, harte Grenze
120 Minuten ab Implementierungsbeginn; keine Zusage eines wissenschaftlichen
Erfolgs in dieser Zeit. Vor einem Forschungslauf eine feste Laufzeitgrenze aus
dem gemessenen Durchsatz ableiten und zusammen mit Code/Protokoll einfrieren.

Ohne bestandene technischen Prüfungen oder bei überschrittenem Budget stoppen
und den Befund dokumentieren. Keine Kamera, keine Live-Audioausgabe, kein
Forschungslauf und keine P0–P3-Wiederholung sind für diese Spezifikation erfolgt.
Eine Implementierung ersetzt keine mathematische Neuheitsprüfung.

## 7. Technischer Lieferstand am 16.09.2026

Implementierung: `vibrasim2/l0/core.py`, `evaluation.py`, `benchmark.py`.
Bedienung und Prüfgrenzen stehen in [L0 / README](../../vibrasim2/l0/README.md),
Messwerte und Nachweise im [technischen Prüfbericht](../validation/l0-20260916.md).

45 neue technische L0-Tests und sechs bestehende P3-Tests bestanden gemeinsam.
Die verkürzte Ablaufprüfung nutzt Seed 1001, nur 20 Versuche je Phase und vier
Prüfkontexte. Sie prüft Ablauf und Dateien; sie bewertet keinen wissenschaftlichen
Erfolg. Die Forschungs-Seeds 0–29 wurden nicht auf Lernerfolg ausgewertet.

Die benannten Zufallsströme sind in `evaluation.STREAMS` eindeutig nummeriert
(0–13); jeder entsteht aus `SeedSequence(master_seed, spawn_key=(index,))` und
PCG64. Für alle Arme gilt dieselbe Zuordnung. Die operative Unterscheidung bei
fehlenden Wiederholungen ist ausdrücklich: dokumentierter externer Abbruch →
INCONCLUSIVE; unerklärte fehlende Daten oder Ressourcenüberschreitung → FAIL.

Die Ressourcenmessung ohne Prüfziele blieb bei vollem Speicher innerhalb der
Grenzen. Für diese Maschine ergibt sich eine konservative Planung von rund
59 Minuten und eine vorgeschlagene harte Grenze von 7140 Sekunden (119 Minuten).
Das ist noch kein eingefrorener Run-Vertrag. Vor dem Forschungslauf müssen
Code-/Protokoll-/Umgebungshashes, Ressourcenwächter und Artefaktprüfung gemeinsam
festgelegt werden. Die Funktion `summarize` prüft Zahlen; sie bestätigt allein
keine Artefaktherkunft. Ein Ergebnisbericht darf diese Prüfung nicht ersetzen.
