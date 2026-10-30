# L0 — Grundlage eines erfahrungslernenden Systems

> Historischer Entwurf, am 16.09.2026 ersetzt durch
> [G176 / L0 — kontinuierliches Erfahrungslernen](../../amendments/G176_l0_continuous_experience_learning.md).
> Die unten erhaltene Drei-Ton-Aufgabe entspricht nicht dem korrigierten Auftrag
> und darf nicht als aktuelle Implementierungsvorgabe verwendet werden.

Status: Entwurf zur Prüfung, keine implementierte Lernmaschine und keine
Präregistrierung eines bereits festgelegten Algorithmus.

## Ziel und Programmgrenze

Ich will ein lokal laufendes System entwickeln, das durch Wahrnehmung,
eigene Antwortversuche und meine Rückmeldung lernt. Langfristig gehören
Webcam, Videos, Texte und Sound dazu. Ein LLM, vortrainierte Wahrnehmung,
Spracherkennung oder fertiges semantisches Wissen sind nicht der Kern.
Normale CPU/GPU-Hardware ist eine feste Randbedingung, keine spätere Optimierung.

Der Forschungsanspruch ist eine eigenständige mathematische Lernregel.
Ihre Neuheit, Brauchbarkeit und Skalierbarkeit sind getrennt nachzuweisen.
Eine neue Bezeichnung oder Implementierung bekannter Regeln erfüllt diesen
Anspruch nicht. Eine wissensfreie Herleitung kann nicht garantiert werden.

L0 ist kein P4 und kein Nachweis physikalischer Materie. P0–P3 sowie die
Vibrasim-I-Experimente bleiben geschlossen und unverändert. Die bisherige
Vibrasim-II-Charta verbietet Rückmeldesignale; sie ist deshalb keine passende
Autorität für diesen neuen Ansatz. Dieser Entwurf schlägt einen getrennten
Lernauftrag vor, keine rückwirkende Änderung ihrer Kriterien.

## Architekturentscheidung

Ein isolierter Kern mit dokumentierten Zustandsübergängen ist der bevorzugte
Weg. Die Übernahme des historischen Lernkerns würde dessen Annahmen übernehmen.
Eine vollständige multimodale Oberfläche vor dem mathematischen Kern würde
Bedienbarkeit erzeugen, aber noch keinen Nachweis von Lernen.

Der erste Arbeitsschritt ist daher die mathematische Spezifikation mit
handrechenbaren Gegenbeispielen. Die nachfolgende Implementierung wird erst
aus dieser Spezifikation abgeleitet. Sensoradapter und 3D-Anzeige bleiben
austauschbar und können weder Bewertungen noch Sollantworten erfinden.

## Erster Lernkreislauf

1. Ein ausdrücklich gestarteter Aufnahmeabschnitt liefert Bild und Ton.
2. Ein zunächst kleines System erzeugt einen kurzen Ton als Antwortversuch.
3. Zwei Tasten bewerten genau diesen Versuch als gut oder falsch.
4. Ohne Rückmeldung findet keine erfundene Bewertung statt.
5. Eine spätere Prüfung verwendet neue Aufnahmen ohne Lernupdates.

Die Tasten sind ein anfänglicher Kommunikationskanal. Das System versteht
damit noch nicht die gesprochenen Wörter gut und falsch. Ebenso ist ein
erzeugter Ton noch keine Sprache. Text, Videodateien, freie Sprache und
unbeaufsichtigtes Dauerlernen gehören nicht in den ersten Funktionsnachweis.

Die erste Aufgabe verwendet drei unterscheidbare visuelle Reize und drei
fest begrenzte mögliche Antworttöne. Die Zuordnung ist nur der bewertenden
Person beziehungsweise dem getrennten Testsystem bekannt, niemals dem Kern.
Tonfrequenzen sind Aktionsmöglichkeiten, keine vorgegebenen Bedeutungen.
Gleichzeitige Sprache darf aufgenommen werden; ein visueller Erfolg belegt
noch nicht, dass beide Eingangskanäle gemeinsam gelernt wurden.

## Mathematisches Lastenheft

Die Schreibweise S(t+1)=F(S(t), X(t), U(t), R(t)) benennt lediglich die
Schnittstelle, nicht die gesuchte Lernregel. S bezeichnet den vollständigen
inneren Zustand, X die Eingangswerte, U den eigenen Antwortversuch und R eine
zugeordnete Rückmeldung oder deren Abwesenheit.

Die mathematische Entwicklungsphase muss genau einen Kandidaten liefern mit:

- vollständig angegebenen Zustandsgrößen, Einheiten, Wertebereichen,
  Anfangsbedingungen und Übergangsregeln;
- einer expliziten Unterscheidung zwischen kurzlebiger Aktivität und
  erfahrungsabhängigen, speicherbaren Veränderungen;
- einer kausalen Regel für die Wirkung verzögerter Rückmeldung;
- einer begründeten Rolle von Schwingungen, falls sie verwendet werden:
  Frequenzbezeichnungen allein sind keine Erklärung;
- einem vollständig durchgerechneten kleinen Beispiel mit positiver,
  negativer, fehlender und widersprüchlicher Rückmeldung;
- einer Obergrenze für Speicher und Arbeit je Schritt sowie einem definierten
  Verhalten an der Kapazitätsgrenze;
- einer Liste sämtlicher eingebauter Hilfen und nicht bewiesener Annahmen.

Ein Kandidat darf nicht heimlich auf eine Muster-Antwort-Tabelle, semantische
Merkmale aus einem vortrainierten Modell oder Sollantworten zugreifen.
Wird eine bekannte Regel wiedererkannt, wird dies offengelegt. Der Kandidat
wird dann nicht als neue Mathematik bezeichnet. Ohne ausformulierte Regel
wird keine lernende 3D-Demonstration als Ersatz gebaut.

## Messvertrag für die anschließende Präregistrierung

Vor Experimentdaten werden der Kandidat, seine Konstanten, die Eingaben,
Lern- und Prüfaufteilung, Initialisierungen, Versuchszahl und numerischen
Akzeptanzgrenzen in einem eigenen ausführbaren L0-Protokoll eingefroren.
Dieses Dokument legt die dafür zwingenden Nachweise fest, nicht einen
vermeintlich schon messbaren Lernerfolg:

- neue Aufnahmen statt identischer Trainingsdateien bei der Prüfung;
- Vergleich mit demselben Kern bei gesperrter dauerhafter Veränderung;
- Vergleich mit derselben Anzahl, aber falsch zugeordneten Bewertungen;
- zufällige Antwortwahl als zusätzliche Referenz;
- Behalten nach Speichern und Neustart;
- erneute Prüfung der ersten Zuordnung nach einer zweiten Lernphase;
- getrennte Prüfung von Bild allein, Ton allein und beiden zusammen, bevor
  eine Behauptung über multimodales Lernen zulässig ist.

Ein Lernnachweis und ein Neuheitsnachweis sind separate Urteile. Auch ein
bestandener Test würde weder Baby-ähnliches Allgemeinlernen noch Verständnis
oder Bewusstsein belegen. Wachstum ist ebenfalls separat zu prüfen: Mehr
belegte Speicherplätze allein gelten nicht als neu entstandene Fähigkeit.

## Ressourcen, Datenschutz und Beobachtung

Vorgeschlagenes erstes Budget: CPU-Betrieb ohne erforderliche GPU,
höchstens 2 GiB Prozessspeicher einschließlich Ein-/Ausgabe und Beobachter,
höchstens 100 MiB persistierter Kernzustand. Dies sind Entwurfsgrenzen,
keine bereits gemessenen Leistungswerte. Eine spätere GPU-Nutzung darf die
mathematische Bedeutung der Regeln nicht ändern.

Eingänge werden auf maximal fünf Bildabnahmen pro Sekunde und 16-kHz-Monoaudio
begrenzt. Zulässig sind Größenanpassung, Normierung und dokumentierte
Signalumrechnung, nicht eine versteckte Objekterkennung oder Transkription.
Zeitstempel, fehlende Daten und verworfene Frames bleiben sichtbar. Bei
Überlast wird sie gemeldet; sie darf nicht als Simulation in Echtzeit gelten.

Webcam und Mikrofon starten nur nach einer ausdrücklichen Bedienaktion.
Kein Cloudtransfer und keine automatische dauerhafte Rohaufnahme. Aufnahme
für reproduzierbare Tests erfolgt separat und sichtbar mit Einwilligung.
Lernen, Aufnahme und Tonausgabe sind jeweils stoppbar. Töne werden in Dauer
und Amplitude begrenzt; fehlende Geräte erzeugen einen Fehler, keine Demodaten.

Die 3D-Ansicht zeigt ausschließlich veröffentlichte Kernzustände. Sie trägt
L0, Session-ID, Lern-/Prüfmodus, Zeit und Datenalter. LIVE, REPLAY, PAUSE und
STOP sind eindeutig unterscheidbar. Wachstum darf nur bei tatsächlich
veränderten internen Strukturen sichtbar werden. Die Ansicht ist kein Gehirn-
oder Intelligenznachweis.

## Nächste verbindliche Lieferung

Nach Prüfung dieses Entwurfs folgt eine begrenzte mathematische
Entwicklungsphase: ein Kandidat nach obigem Lastenheft oder ein dokumentierter
Befund, welche Anforderung nicht erfüllt werden konnte. Zeitbudget dafür:
60 Minuten, harte Grenze 120 Minuten ab Beginn dieser Phase. Ein Scheitern
wird nicht durch einen anderen Algorithmus unter demselben Namen verdeckt.

Erst ein prüfbarer Kandidat rechtfertigt Implementierungsplan, Kerntests,
Sensoranbindung und den registrierten Lernversuch. Unbeaufsichtigte Aufnahme,
Veröffentlichung, zusätzliche Hardwarekäufe oder automatische Fortsetzung
beliebig vieler Experimente sind nicht Bestandteil dieser Freigabe.
