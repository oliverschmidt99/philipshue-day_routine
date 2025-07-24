# Philips Hue Advanced Routine Controller

Ein fortschrittliches Steuerungssystem für Philips Hue, das komplexe, zeit- und sensorbasierte Routinen über eine intuitive Web-UI ermöglicht. Die Anwendung zeichnet sich durch eine modulare Architektur aus, die eine einfache Wartung und Erweiterung sicherstellt.

---

## ⭐ Kernfunktionen

- **Modulare Routine-Engine:** Jede Routine agiert autonom und kombiniert flexible Zeitpläne (Morgen, Tag, Abend, Nacht) mit Sensor-Auslösern wie Bewegung und Helligkeit.
- **Zustandsbasierte Logik:** Eine robuste State-Machine (z.B. Normalzustand, Bewegungs-Aktivität, Inaktiv) steuert alle Übergänge und sorgt für ein stabiles und vorhersehbares Systemverhalten.
- **Adaptive Helligkeitsregelung:** Eine intelligente, inverse Regelung mit einstellbarer Hysterese passt die Beleuchtung dynamisch an das Umgebungslicht an und verhindert unerwünschtes Flackern bei Grenzwerten.
- **Dynamische Zeitsteuerung:** Die Zeitabschnitte können wahlweise an feste Uhrzeiten oder dynamisch an den Sonnenauf- und -untergang gekoppelt werden, basierend auf dem Standort des Nutzers.
- **Datenpersistenz & Analyse:** Sensorwerte wie Helligkeit und Temperatur werden in einer SQLite-Datenbank protokolliert und über eine Flask-API zur Visualisierung mit Chart.js im Frontend bereitgestellt.
- **Modernes Web-Interface:** Eine auf Vanilla JS und Tailwind CSS basierende Single-Page-Application ermöglicht die vollständige Konfiguration von Routinen, Szenen und globalen Systemeinstellungen.

---

## 🏗️ Systemarchitektur

Das Projekt ist in logische Kernkomponenten unterteilt:

- **`main.py`**: Der Haupteinstiegspunkt der Anwendung. Er initialisiert die Bridge-Verbindung, startet den Webserver als separaten Prozess und führt die Hauptsteuerungslogik in einer stabilen Schleife aus.
- **`src/`**: Enthält die gesamte Kernlogik als Python-Paket.
  - `routine.py`: Implementiert die Logik für einzelne Routinen, inklusive Zustandsmanagement und Sensor-Interaktion.
  - `room.py`, `scene.py`, `sensor.py`: Abstraktionsklassen für die saubere Interaktion mit der Hue Bridge API.
  - `daily_time_span.py`: Kapselt die komplexe Zeitlogik zur Einteilung der Tagesperioden unter Berücksichtigung der Sonnenzeiten.
- **`web/`**: Beinhaltet die Flask-Webanwendung für die Benutzeroberfläche und API.
  - `server.py`: Stellt alle API-Endpunkte (`/api/*`) für die nahtlose Kommunikation zwischen Frontend und Backend bereit.
  - `templates/` & `static/`: Enthalten die HTML-Struktur sowie CSS- und JavaScript-Dateien für die interaktive UI.
- **`config.yaml`**: Die zentrale Konfigurationsdatei für alle Einstellungen, von der Bridge-IP über Routinen bis zu den Szenen.

---

## 🚀 Installation & Inbetriebnahme

Die Installation erfolgt komfortabel über das mitgelieferte Skript, welches alle notwendigen Schritte automatisiert.

**Voraussetzungen:**

- Ein Arch-basiertes Linux-System (z.B. Arch Linux, EndeavourOS). Da du, wie du mir gesagt hast, EndeavourOS nutzt, ist das perfekt.
- `git` zur Versionsverwaltung.

**Schritte:**

1.  **Repository klonen:**

    ```bash
    git clone [https://github.com/oliverschmidt99/philipshue-day_routine.git](https://github.com/oliverschmidt99/philipshue-day_routine.git)
    cd philipshue-day_routine
    ```

2.  **Installationsskript ausführen:**
    Das Skript macht sich selbst ausführbar und startet die Installation. Du wirst eventuell zur Eingabe deines `sudo`-Passworts aufgefordert.

    ```bash
    chmod +x install.sh
    ./install.sh
    ```

    Das Skript erledigt Folgendes:

    - Installiert Systemabhängigkeiten über `pacman`.
    - Richtet eine isolierte Python-Umgebung (`.venv`) ein.
    - Installiert Python-Pakete aus `requirements.txt`.
    - Erstellt, aktiviert und startet einen `systemd`-Service für den Autostart.

3.  **Anwendung konfigurieren:**
    Nach der Installation läuft die Anwendung als Hintergrunddienst. Öffne einen Webbrowser und navigiere zu `http://<IP-DEINES-SERVERS>:5000`. Ein Einrichtungsassistent führt dich durch die Verbindung mit deiner Hue Bridge.

---

## 🛠️ Service-Verwaltung (systemd)

- **Status prüfen:**
  Zeigt an, ob der Dienst aktiv ist und listet die letzten Logeinträge.
  ```bash
  systemctl status hue_controller.service
  ```
- **Dienst starten:**
  Startet den Hue Controller Service.
  ```bash
  systemctl start hue_controller.service
  ```
- **Dienst stoppen:**
  Stoppt den Hue Controller Service.
  ```bash
  systemctl stop hue_controller.service
  ```
- **Dienst neu starten:**
  Startet den Dienst neu, um Änderungen zu übernehmen.
  ```bash
  systemctl restart hue_controller.service
  ```
- **Logs anzeigen:**
  Zeigt die letzten Logeinträge des Dienstes an.
  ```bash
  journalctl -u hue_controller.service -f
  ```

**Contribution:**
Beiträge sind willkommen! Bitte erstellt Pull-Requests für neue Features oder Bugfixes. Für größere Änderungen erstelle bitte ein Issue, um die Änderungen zu diskutieren.

## 📄 Lizenz

Dieses Projekt ist Lizenzfrei und steht unter der MIT-Lizenz. Du kannst es frei verwenden, modifizieren und verteilen, solange du die ursprünglichen Urheberrechte anerkennst.  
