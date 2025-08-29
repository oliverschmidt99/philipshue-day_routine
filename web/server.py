"""
Flask-Webserver für die Philips Hue Routine-Steuerung.
Initialisiert die Flask-App und registriert alle API-Blueprints.
"""

import os
import sys
import logging
from flask import Flask, render_template

# Pfad zum Hauptverzeichnis hinzufügen, damit 'src' gefunden wird
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from src.logger import Logger

# Importiere die API-Blueprints
from api.setup import setup_api
from api.bridge import bridge_api
from api.system import system_api
from api.data import data_api

# --- Globale Pfade & Initialisierung ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")

app = Flask(__name__)
log = Logger(LOG_FILE)

# Deaktiviert das Standard-Flask-Logging
werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)

# Registriere alle API-Blueprints
app.register_blueprint(setup_api, url_prefix="/api/setup")
app.register_blueprint(bridge_api, url_prefix="/api/bridge")
app.register_blueprint(system_api, url_prefix="/api/system")
app.register_blueprint(data_api, url_prefix="/api/data")


# --- UI & Fehler-Routen ---
@app.route("/")
def index():
    """Zeigt die Hauptseite (index.html) an."""
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    """Verhindert 404-Fehler für das Browser-Icon."""
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
