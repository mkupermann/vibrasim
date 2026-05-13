# EQMOD Autopilot — Setup für die Vacation-Phase

## Was steht hier?

Dieses Verzeichnis enthält alles, was der Autopilot braucht, um 14 Tage ohne dich an einer kleinen Queue pre-registrierter G-Amendments zu arbeiten. Plan-Dokument: `~/.claude/plans/ich-bin-jetzt-f-r-functional-crane.md`.

## Was du vor Abflug machen musst

### 1. Queue füllen (das ist die inhaltliche Arbeit)

Edit `.eqmod/autopilot/QUEUE.yaml`. Füge 3–5 Items in `items:` ein. Für jedes Item brauchst du:

- `id`: G24, G25, … — fortlaufend
- `title`: Ein-Satz-Hypothese
- `brief`: Pfad zu einer NEUEN Datei unter `docs/amendments/G<n>.md`, die du jetzt schreiben musst. Erbst dem G20-G23.md-Schema (Hypothese, Mechanik, Tests, Acceptance, Negative Control).
- `preregistered_acceptance`: liste binärer Aussagen. Mindestens eine `"... PASSES"` und eine `"... FAILS"` (negative control). Konvention: wenn ein Eintrag wie `"tests/test_g24_*.py::test_decay PASSES"` aussieht, wertet postflight ihn automatisch als pytest-Target aus.
- `time_budget_hours`: 24–48 typisch (bei 3 Items = ~96h pro Item Wallclock im 14-Tage-Fenster).
- `status: queued`

Beispiel siehe Schema-Kommentar am Ende von `QUEUE.yaml`.

**Wichtig:** Sobald ein Item `in_progress` ist, ist seine Acceptance gesperrt — pre-commit hook blockt jede Änderung. Lock-in passiert beim ersten Preflight-Pick. Also: Briefs UND Acceptances vor Abflug stabil.

### 2. Pre-Commit-Hook installieren

```
cd /Users/mkupermann/GitHub/EQMOD
ln -sf ../../.eqmod/autopilot/hooks/pre-commit .git/hooks/pre-commit
```

Der Hook ist no-op für deine eigenen Commits (er prüft `EQMOD_AUTOPILOT=1`). Du kannst weiterhin marker_protocol.md editieren. Nur der Autopilot wird geblockt.

Test:
```
EQMOD_AUTOPILOT=1 git commit --allow-empty -m "test"
# sollte fehlschlagen wenn auf branch != autopilot/*
```

### 3. launchd-Jobs installieren

```
cp .eqmod/autopilot/com.eqmod.autopilot.plist ~/Library/LaunchAgents/
cp .eqmod/autopilot/com.eqmod.watchdog.plist  ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.eqmod.autopilot.plist
launchctl load ~/Library/LaunchAgents/com.eqmod.watchdog.plist
launchctl list | grep eqmod
```

Erwartet: zwei Zeilen, Status `0`.

Autopilot tickt um 02:00, 08:00, 14:00, 20:00 Uhr. Watchdog jede Stunde, mailt täglich nach 08:00.

### 4. Mail-Versand verifizieren

```
echo "watchdog mail test" | /usr/bin/mail -s "[EQMOD] mail test" michael@kupermann.com
```

Wenn nichts ankommt: macOS lokales sendmail braucht u.U. Konfiguration (msmtp + ~/.msmtprc, oder /etc/postfix mit Gmail relay). Watchdog schreibt sonst nach `~/.eqmod/autopilot/watchdog_unsent_*.txt` — du würdest die nach Rückkehr sehen, aber während des Urlaubs keine Mail bekommen.

### 5. Dry-Run unter Beobachtung

```
bash .eqmod/autopilot/run_autopilot.sh
```

Beobachten in zweitem Terminal:
```
tail -f ~/.eqmod/autopilot/session.log
```

Prüfen nach dem Run:
- QUEUE.yaml: Status des ersten Items ist `passed` oder `null`, attempts=1
- LOGBOOK.md: ein neuer Eintrag mit Verdict
- `git log autopilot/G24 --oneline`: ein Autopilot-Commit
- `git branch -a`: Branch `autopilot/G24` existiert lokal (+ remote falls Push erfolgreich)
- `cat ~/.eqmod/autopilot/HUMAN_NEEDED.md`: idealerweise leer

Wenn etwas schiefläuft: Notbremse `touch ~/.eqmod/autopilot/STOP`, dann debuggen, dann `rm` und neuen Dry-Run.

### 6. Soft-Launch (48h vor Abflug)

Lass die launchd-Jobs laufen während du noch da bist. Beobachte zwei Tickets, prüfe:
- Watchdog-Mail kommt morgens
- Branches landen sauber auf GitHub
- Keine `HUMAN_NEEDED`-Einträge aus Trivia
- Sub-Window-Auslastung im Claude-Status

Falls Charter härter werden muss: editiere `.eqmod/autopilot/CHARTER.md` jetzt. Während der Vacation ist Charter eingefroren (Hook blockt Änderungen).

### 7. Abflug

`git status` sollte clean sein. launchd-Jobs laufen. Du gehst.

## Während du weg bist

- Watchdog mailt täglich. Wenn 12h+ ohne Tick: Alert-Mail.
- Notbremse: einmal von unterwegs `touch ~/.eqmod/autopilot/STOP` ssh'en — alle Sessions exit sofort.
- Branch-Inspektion: `git fetch && git log autopilot/<id>` zeigt was passiert.

## Bei Rückkehr

```
bash tools/autopilot_postmortem.sh
```

Listet Queue-Verdict, HUMAN_NEEDED-Einträge, alle Autopilot-Commits, LOGBOOK-Tail. Eine Seite, alles drauf.

Dann manuell:
- Jedes PASS-Item nochmal mental durchspielen: war die Acceptance fair? Hat der negative control wirklich diskriminiert?
- Jedes NULL/FAIL-Item: ist die Opus-Postmortem-Notiz in LOGBOOK brauchbar?
- Branches mergen die du behalten willst, andere löschen.
- launchd-Jobs stoppen: `launchctl unload ~/Library/LaunchAgents/com.eqmod.*.plist`.

## Layout-Übersicht

```
.eqmod/autopilot/                          ← versioniert im Repo
  CHARTER.md                               ← Constitutional contract (frozen during vacation)
  QUEUE.yaml                               ← Work queue (preregistered_acceptance frozen during in_progress)
  SETUP.md                                 ← dieses Dokument
  run_autopilot.sh                         ← Entry-Point für launchd
  com.eqmod.autopilot.plist                ← launchd config (copy nach ~/Library/LaunchAgents)
  com.eqmod.watchdog.plist                 ← launchd config (copy nach ~/Library/LaunchAgents)
  hooks/pre-commit                         ← Bot-Edit-Gate (symlink nach .git/hooks/pre-commit)

tools/                                     ← versionierte Skripte
  autopilot_preflight.py                   ← Pre-session checks, picks item, branches
  autopilot_postflight.py                  ← Post-session: runs tests, sets verdict, commits, pushes
  autopilot_watchdog.py                    ← Hourly health check, daily mail
  autopilot_opus_postmortem.py             ← Single-shot Opus call after NULL/FAIL
  autopilot_postmortem.sh                  ← Post-vacation review skript

~/.eqmod/autopilot/                        ← Runtime-State, NICHT versioniert
  STOP                                     ← touch to disable (Notbremse)
  current_item.txt                         ← Preflight schreibt, Postflight liest
  current_brief.txt                        ← Pfad zum aktuellen Brief
  last_tick.txt                            ← ISO-Timestamp für Watchdog
  HUMAN_NEEDED.md                          ← Session schreibt bei Uncertainty
  session.log                              ← run_autopilot.sh appendet jeden Run
  launchd.{out,err}                        ← launchd stdout/stderr
  watchdog.{out,err}                       ← launchd stdout/stderr
  watchdog_last_daily.txt                  ← Dedup für Daily-Mail
  watchdog_alert_seen.txt                  ← Dedup für HUMAN_NEEDED-Alerts
```
