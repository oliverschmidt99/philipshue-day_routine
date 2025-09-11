"""
Flask-Webserver für die Philips Hue Routine-Steuerung.
"""
import logging
import os
import sys
from flask import Flask, render_template, send_from_directory

# Füge das Projekt-Root zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.logger import Logger

# Importiere die Blueprints aus dem api-Ordner
from web.api.bridge import bridge_api
from web.api.config_api import config_api
from web.api.data import data_api
from web.api.setup import setup_api
from web.api.system import system_api

# Pfaddefinitionen
DATA_DIR = os.path.join(project_root, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
LOG_FILE = os.path.join(DATA_DIR, "app.log")

def create_app():
    """Erstellt und konfiguriert die Flask-App (Application Factory)."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    # Logging und Config Manager der App hinzufügen
    app.logger_instance = Logger(LOG_FILE)
    app.config_manager = ConfigManager(CONFIG_FILE, app.logger_instance)

    # Werkzeug-Logger auf ERROR setzen, um die Konsole sauber zu halten
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    # Registriere alle API-Blueprints
    app.register_blueprint(bridge_api, url_prefix="/api/bridge")
    app.register_blueprint(config_api, url_prefix="/api/config")
    app.register_blueprint(data_api, url_prefix="/api/data")
    app.register_blueprint(setup_api, url_prefix="/api/setup")
    app.register_blueprint(system_api, url_prefix="/api/system")


    @app.route("/")
    def index():
        """Rendert die Hauptseite."""
        return render_template("index.html")

    @app.route("/favicon.ico")
    def favicon():
        """Liefert das Favicon aus."""
        return send_from_directory(
            os.path.join(app.static_folder, 'img'), "favicon.svg", mimetype="image/svg+xml"
        )

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.logger_instance.info("Starte Flask-Server...")
    # debug=False ist für den Produktivbetrieb wichtig
    flask_app.run(host="0.0.0.0", port=5001, debug=False)