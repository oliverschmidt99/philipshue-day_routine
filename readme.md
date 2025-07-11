# Philips Hue Tageslicht- und Bewegungs-Routine

Dieses Projekt ermöglicht die Erstellung von dynamischen, automatisierten Licht-Routinen für Philips Hue, die über eine komfortable Weboberfläche verwaltet werden können. Die Steuerung kombiniert feste Tagesabläufe mit den realen Zeiten für Sonnenauf- und -untergang und reagiert auf Bewegungsmelder.

![Web Interface Screenshot](https://placehold.co/800x400/2d3748/ffffff?text=Web+Interface+Screenshot)

---

## Features

- **Web-Interface:** Eine übersichtliche Weboberfläche zur Verwaltung aller Routinen und Lichtszenen.
- **Dynamische Tagesabläufe:** Die vier festen Tagesphasen (`Morning`, `Day`, `Evening`, `Night`) werden automatisch an den täglichen Sonnenauf- und -untergang angepasst.
- **Flexible Szenen-Erstellung:** Erstelle und bearbeite Lichtszenen mit einem visuellen Editor, inklusive:
  - Farbwähler für beliebige Farben (`hue`/`sat`).
  - Farbtemperatur-Regler für Weißtöne (`ct`).
  - Helligkeitssteuerung (`bri`).
- **Detaillierte Routine-Steuerung:**
  - **Bewegungssteuerung:** Aktiviere oder deaktiviere die Reaktion auf Bewegung für jeden Tagesabschnitt einzeln.
  - **Ausschaltverzögerung:** Lege sekundengenau fest, wie lange das Licht nach der letzten Bewegung anbleiben soll.
  - **"Bitte nicht stören"-Funktion:** Verhindert, dass eine Automatisierung eine manuell eingestellte Lichtstimmung überschreibt.
  - **Helligkeits-Check:** Die Bewegungssteuerung kann optional nur dann auslösen, wenn die Umgebungshelligkeit unter einem bestimmten Wert liegt.
- **Live-Status-Monitor:** Ein eigener Reiter in der Weboberfläche zeigt den Echtzeit-Zustand aller Routinen und die `info.log`-Datei an, um die Abläufe nachzuvollziehen.

---

## Setup & Installation

Folge diesen Schritten, um das Projekt einzurichten und zu starten.

### 1. Voraussetzungen

- Python 3.x
- Eine Philips Hue Bridge im selben Netzwerk

### 2. Abhängigkeiten installieren

Öffne ein Terminal und installiere die benötigten Python-Bibliotheken mit `pip`:

```bash
pip install phue Flask PyYAML requests astral
```

### 3. Konfiguration

Bevor du das Skript startest, musst du die `config.yaml`-Datei anpassen:

1.  **Bridge IP-Adresse:** Trage die lokale IP-Adresse deiner Hue Bridge ein.
    ```yaml
    bridge_ip: "192.168.178.XX"
    ```
2.  **Standort:** Gib deine geografischen Koordinaten für die Berechnung von Sonnenauf- und -untergang an. Diese kannst du z.B. über Google Maps ermitteln.
    ```yaml
    location:
      latitude: 52.2059
      longitude: 8.0755
    ```

### 4. Anwendung starten

Das System besteht aus zwei Teilen: dem Webserver (`app.py`) und dem Logik-Skript (`main.py`). Der Webserver startet und verwaltet das Logik-Skript automatisch.

1.  Öffne ein Terminal im Hauptverzeichnis des Projekts.
2.  Starte den Webserver:
    ```bash
    python app.py
    ```
3.  **Beim allerersten Start:** Das Terminal wird dich auffordern, den großen, runden **Link-Button auf deiner Hue Bridge** zu drücken. Dies ist nur einmalig notwendig, um die Anwendung mit deiner Bridge zu koppeln.

---

## Benutzung

1.  **Weboberfläche aufrufen:** Öffne einen Webbrowser und gehe zur Adresse, die im Terminal angezeigt wird (z.B. `http://127.0.0.1:5000`).
2.  **Routinen-Tab:**
    - Erstelle neue Routinen mit dem `+ Neue Routine`-Button.
    - Bearbeite bestehende Routinen, um die Szenen, die Bewegungssteuerung und die Helligkeits-Checks für die vier Tagesphasen anzupassen.
3.  **Szenen-Tab:**
    - Erstelle neue Lichtszenen mit dem `+ Neue Szene`-Button.
    - Bearbeite bestehende Szenen über den visuellen Editor für Farbe oder Weißtöne.
4.  **Status-Tab:**
    - Überwache in Echtzeit, welche Routine gerade in welchem Zustand ist.
    - Verfolge die Aktionen des Systems über die Live-Anzeige der Log-Datei.
5.  **Speichern:** Nachdem du Änderungen vorgenommen hast, klicke auf **"Speichern und Alle Routinen neu starten"**, damit das System die neue Konfiguration lädt und anwendet.

---

## Projektstruktur

- **`app.py`**: Der Flask-Webserver. Dient als Haupt-Startpunkt und stellt die Weboberfläche sowie die API bereit.
- **`main.py`**: Das Herzstück der Logik. Läuft als Hintergrundprozess, berechnet die Zeiten und führt die Routinen aus.
- **`config.yaml`**: Die zentrale Konfigurationsdatei für alle deine persönlichen Einstellungen.
- **`control/`**: Enthält die Python-Klassen, welche die Logik kapseln (`Routine.py`, `Scene.py`, `Room.py`, etc.).
- **`templates/`**: Enthält die `hue.html`-Datei, welche die komplette Weboberfläche darstellt.
- **`info.log`**: Die Log-Datei, in die alle wichtigen Ereignisse geschrieben werden.
- **`status.json`**: Eine temporäre Datei, die den Live-Zustand der Routinen für die Status-Seite speichert.
