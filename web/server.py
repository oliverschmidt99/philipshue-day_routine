"""
Flask-Webserver für die Philips Hue Routine-Steuerung.
Verwendet das Application Factory-Muster, um zirkuläre Importe zu vermeiden.
"""

import os
import sys
import logging
from flask import Flask, render_template, send_from_directory

# Fügt das Hauptverzeichnis (eine Ebene über 'web') zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.logger import Logger
from src.config_manager import ConfigManager

# --- Globale Pfade ---
BASE_DIR = project_root
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")


def create_app():
    """Erstellt und konfiguriert die Flask-App (Application Factory)."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.logger_instance = Logger(LOG_FILE)
    app.config_manager = ConfigManager(CONFIG_FILE, app.logger_instance)

    werkzeug_log = logging.getLogger("werkzeug")
    werkzeug_log.setLevel(logging.ERROR)

    with app.app_context():
        from web.api.setup import setup_api
        from web.api.bridge import bridge_api
        from web.api.system import system_api
        from web.api.data import data_api
        from web.api.config_api import config_api

        app.register_blueprint(setup_api, url_prefix="/api/setup")
        app.register_blueprint(bridge_api, url_prefix="/api/bridge")
        app.register_blueprint(system_api, url_prefix="/api/system")
        app.register_blueprint(data_api, url_prefix="/api/data")
        app.register_blueprint(config_api, url_prefix="/api/config")

    @app.route("/")
    def index():
        """Zeigt die Hauptseite (index.html) an."""
        return render_template("index.html")

    @app.route("/favicon.ico")
    def favicon():
        """Liefert das Favicon aus dem Static-Ordner aus."""
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    return app


if __name__ == "__main__":
    flask_app = create_app()
    log = flask_app.logger_instance
    log.info("Starte Flask-Server...")
    flask_app.run(host="0.0.0.0", port=5000, debug=False)
