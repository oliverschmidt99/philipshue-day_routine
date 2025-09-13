"""
Ein einfaches Skript, um NUR den Flask-Webserver im Debug-Modus
für Entwicklungszwecke zu starten.

Die core_logic wird hierbei nicht ausgeführt.
"""
import os
import sys

# Füge das Projekt-Root zum Python-Pfad hinzu, damit die Imports funktionieren
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Importiere die Funktion, die deine Flask-App erstellt
from web import create_app

# Erstelle die App-Instanz
app = create_app()

if __name__ == '__main__':
    # Starte die App im Debug-Modus auf einem anderen Port (z.B. 5050)
    # use_reloader=True sorgt für den automatischen Neustart bei Änderungen.
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=True)