# Projekt-Checkliste: HueFlow

Hier arbeiten wir Schritt für Schritt die offenen Punkte und neuen Features ab.

---

## Phase 1: Stabilität der Weboberfläche (UI)

- [ ] **Darkmode reparieren**: Der Umschaltknopf muss den Hintergrund und die Icons zuverlässig zwischen Hell und Dunkel wechseln.
- [ ] **Tab-Navigation reparieren**: Ein Klick auf "Szenen", "Status" oder "Einstellungen" muss den korrekten Inhalt anzeigen.
- [ ] **Fehler "Laden der Daten" beheben**: Die rote Fehlermeldung beim Start muss verschwinden.
- [ ] **Tab sind ohne Funktion**
- [ ] **Einstellung der Routinen** Die Routinen können nicht bearbeitet werden, da die UI nicht korrekt funktioniert.
- [ ] **Einstellung der Szenen** Die Szenen können nicht bearbeitet werden, da die UI nicht korrekt funktioniert.
- [ ] **Einstellung der IP-Adresse** Die IP-Adresse kann nicht gespeichert werden, da die UI nicht korrekt funktioniert.
- [ ] **Einstellung der Refreshrate** Die Refreshrate kann nicht gespeichert werden, da die UI nicht korrekt funktioniert.
- [ ] **Einstellung der Sprache** Die Sprache kann nicht gespeichert werden, da die UI nicht korrekt funktioniert.
- [ ] **Einstellung der Log-Level** Die Log-Level können nicht gespeichert

---

## Phase 2: Interaktivität der UI

- [ ] **Neue Routine erstellen**: Der "+ Neue Routine"-Knopf soll ein Modal öffnen, in dem man einen Namen und einen Raum/Zone auswählen kann.
- [ ] **Routine bearbeiten**: Der "Bearbeiten"-Knopf soll ein Modal mit allen Einstellungen der jeweiligen Routine öffnen.
- [ ] **Routine löschen**: Der "Löschen"-Knopf soll nach einer Bestätigung die Routine entfernen.
- [ ] **Neue Szene erstellen**: Der "+ Neue Szene"-Knopf soll den Szenen-Editor öffnen.
- [ ] **Szene bearbeiten**: Der "Bearbeiten"-Knopf soll den Szenen-Editor mit den Werten der jeweiligen Szene öffnen.
- [ ] **Szene löschen**: Der "Löschen"-Knopf soll nach einer Bestätigung die Szene entfernen.

---

## Phase 3: Backend & Speichern

- [ ] **Speichern & Neustart implementieren**: Der große "Speichern"-Button soll die `config.yaml` auf dem Server aktualisieren und die Logik-Engine sicher neustarten.
- [ ] **Spracheinstellungen speichern**: Die Auswahl im Einstellungs-Tab soll in der `config.yaml` gespeichert werden.
- [ ] **IP-Adresse & Refreshrate speichern**: Die Eingaben im Einstellungs-Tab sollen in der `config.yaml` gespeichert werden.

---

## Phase 4: Abschluss & Feinschliff

- [ ] **Live-Status-Updates**: Der "Status"-Tab soll sich automatisch aktualisieren und den Echtzeit-Zustand der Routinen und das Log anzeigen.
- [ ] **Visueller Feinschliff**: Überprüfung des Layouts, der Abstände und der Benutzerfreundlichkeit.
- [ ] **Code aufräumen**: Entfernen von nicht mehr benötigten Dateien und Code-Kommentaren.
