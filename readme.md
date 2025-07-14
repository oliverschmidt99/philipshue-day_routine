# Philips Hue Tageslicht- und Bewegungs-Routine

Dieses Projekt ermöglicht die Erstellung von dynamischen, automatisierten Licht-Routinen für Philips Hue, die über eine komfortable Weboberfläche verwaltet werden können.

---

## Features

- **Web-Interface:** Eine übersichtliche Weboberfläche zur Verwaltung aller Routinen und Lichtszenen.
- **Dynamische Tagesabläufe:** Passt sich an Sonnenauf- und -untergang an.
- **Flexible Szenen-Erstellung:** Visueller Editor für Farben, Farbtemperatur und Helligkeit.
- **Detaillierte Routine-Steuerung:** Mit Bewegungssteuerung, "Bitte nicht stören"-Funktion und Helligkeits-Check.
- **Live-Status-Monitor:** Echtzeit-Überwachung der Routinen und Logs.

---

## Setup & Installation

### 1. Voraussetzungen

- Python 3.x
- Eine Philips Hue Bridge im selben Netzwerk

### 2. Abhängigkeiten installieren

Die benötigten Python-Bibliotheken sind in der `requirements.txt` festgehalten.

**Installation im Terminal:**
```bash
pip install -r requirements.txt
```

### 3. Konfiguration

Passe die `config.yaml`-Datei an:
1.  **Bridge IP-Adresse:** Trage die IP deiner Hue Bridge ein.
2.  **Standort:** Gib deine Koordinaten für die Berechnung der Sonnenzeiten an.

### 4. Anwendung starten

Das gesamte Programm wird jetzt über die `main.py` gestartet.

1.  Öffne ein Terminal im Hauptverzeichnis des Projekts.
2.  Starte die Anwendung:
    ```bash
    python main.py
    ```
3.  **Beim allerersten Start:** Drücke den Link-Button auf deiner Hue Bridge, wenn du dazu aufgefordert wirst.

---

## Projektstruktur

- **`main.py`**: Der zentrale Startpunkt, der den Server und die Logik startet.
- **`web/`**: Enthält den Flask-Webserver (`server.py`) und die HTML-Templates.
- **`src/`**: Die gesamte Kernlogik des Projekts in einzelnen Modulen.
- **`config.yaml`**: Deine persönlichen Einstellungen.
- **`info.log`**: Die Log-Datei für alle Ereignisse.
- **`requirements.txt`**: Liste der Python-Abhängigkeiten.

---

> **Genutzte Bibliotheken**
> - [phue](https://github.com/studioimaginaire/phue) - Für die Kommunikation mit der Philips Hue Bridge.
> - [Flask](https://flask.palletsprojects.com/) - Für die Bereitstellung der Weboberfläche.
> - [PyYAML](https://pyyaml.org/) - Zum Lesen und Schreiben der `config.yaml`.
> - [astral](https://astral.readthedocs.io/) - Zur Berechnung der Sonnenzeiten.
