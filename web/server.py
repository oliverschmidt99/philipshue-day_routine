"""
Flask-Webserver für die Philips Hue Routine-Steuerung.
Verwendet das Application Factory-Muster.
"""
import os
import sys

# Fügt das Projekt-Root-Verzeichnis zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from web import create_app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.logger_instance.info("Starte Flask-Server...")
    flask_app.run(host="0.0.0.0", port=9090, debug=True)