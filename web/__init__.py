"""
Initialisiert das 'web' Flask-Paket und enthält die Application Factory.
"""
import logging
import os
import sys
from flask import Flask, render_template, send_from_directory, g

# Stellt sicher, dass das Projekt-Root im Python-Pfad ist
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.logger import Logger
from src.hue_wrapper import HueBridge

def create_app():
    """
    Erstellt, konfiguriert und gibt die Flask-App-Instanz zurück.
    Dieses Muster wird als "Application Factory" bezeichnet.
    """
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Pfaddefinitionen
    DATA_DIR = os.path.join(project_root, "data")
    SETTINGS_FILE = os.path.join(DATA_DIR, "settings.yaml")
    AUTOMATION_FILE = os.path.join(DATA_DIR, "automation.yaml")
    HOME_FILE = os.path.join(DATA_DIR, "home.yaml")
    LOG_FILE = os.path.join(DATA_DIR, "app.log")

    # Hänge Logger und Config Manager an die App an, damit sie global verfügbar sind
    app.logger_instance = Logger(LOG_FILE)
    app.config_manager = ConfigManager(SETTINGS_FILE, AUTOMATION_FILE, HOME_FILE, app.logger_instance)

    # Erstelle EINE zentrale Bridge-Instanz für die gesamte Web-Anwendung
    config = app.config_manager.get_full_config()
    app.bridge_instance = HueBridge(
        ip=config.get("bridge_ip"), 
        app_key=config.get("app_key"), 
        logger=app.logger_instance
    )

    # Benutze den App-Kontext, um die Blueprints sicher zu registrieren
    with app.app_context():
        # Importiere die Blueprints hier. Das verhindert zyklische Importe.
        from .api.bridge import bridge_api
        from .api.config_api import config_api
        from .api.data import data_api
        from .api.setup import setup_api
        from .api.system import system_api

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
        # Der Pfad muss relativ zum 'static' Ordner sein
        return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")

    # Route, um die Hilfe-Seite zu laden
    @app.route("/hilfe")
    def hilfe():
        return render_template("hilfe.html")

    return app