"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Initialisiert und startet den Webserver und die Kernlogik in einem Prozess.
"""

import os
import sys
import logging
import threading
import atexit
import socket
from flask import Flask, render_template, send_from_directory

# --- Pfad-Konfiguration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic

# --- Globale Pfade ---
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
# KORRIGIERT: Explizite Pfade zu den Web-Ordnern
WEB_DIR = os.path.join(BASE_DIR, "web")
TEMPLATE_DIR = os.path.join(WEB_DIR, "templates")
STATIC_DIR = os.path.join(WEB_DIR, "static")


def create_app():
    """Erstellt und konfiguriert die Flask-App (Application Factory)."""
    # KORRIGIERT: Nutzt die oben definierten, absoluten Pfade
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
        static_url_path="/static",
    )

    app.logger_instance = Logger(LOG_FILE, level=logging.INFO)
    app.config_manager = ConfigManager(CONFIG_FILE, app.logger_instance)

    werkzeug_log = logging.getLogger("werkzeug")
    werkzeug_log.setLevel(logging.ERROR)

    with app.app_context():
        from web.api.setup import setup_api
        from web.api.bridge import bridge_api
        from web.api.system import system_api
        from web.api.data import data_api
        from web.api.config_api import config_api
        from web.api.help import help_api

        app.register_blueprint(setup_api, url_prefix="/api/setup")
        app.register_blueprint(bridge_api, url_prefix="/api/bridge")
        app.register_blueprint(system_api, url_prefix="/api/system")
        app.register_blueprint(data_api, url_prefix="/api/data")
        app.register_blueprint(config_api, url_prefix="/api/config")
        app.register_blueprint(help_api, url_prefix="/api/help")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            app.static_folder,
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    return app


def get_local_ip():
    """Ermittelt die primäre lokale IP-Adresse des Systems."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


# --- Hauptlogik ---
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)

    flask_app = create_app()
    log = flask_app.logger_instance
    config_manager = flask_app.config_manager

    log.info("Starte die Hue Core-Logik in einem Hintergrund-Thread...")
    core_logic = CoreLogic(log, config_manager)
    logic_thread = threading.Thread(target=core_logic.run_main_loop, daemon=True)
    logic_thread.start()

    def cleanup():
        log.info("Anwendung wird beendet. Stoppe Hintergrund-Threads...")
        core_logic.stop_event.set()

    atexit.register(cleanup)

    local_ip = get_local_ip()
    port = 5001
    log.info("=====================================================")
    log.info(f"  Web-UI erreichbar unter: http://{local_ip}:{port}")
    log.info("=====================================================")

    flask_app.run(host="0.0.0.0", port=port, debug=False)
