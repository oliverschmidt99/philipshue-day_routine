"""
Flask-Webserver für die Philips Hue Routine-Steuerung.
"""

import logging
import mimetypes
import os
import sys
from flask import Flask, render_template, send_from_directory

# KORREKTUR: MIME-Typ für JavaScript-Module explizit setzen
mimetypes.add_type("application/javascript", ".js")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.logger import Logger
from web.api import api as api_blueprint

DATA_DIR = os.path.join(project_root, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
LOG_FILE = os.path.join(DATA_DIR, "app.log")


def create_app():
    """Erstellt und konfiguriert die Flask-App (Application Factory)."""
    app = Flask(
        __name__,
        static_folder=os.path.join(project_root, "web", "static"),
        template_folder=os.path.join(project_root, "web", "templates"),
    )

    app.logger_instance = Logger(LOG_FILE)
    app.config_manager = ConfigManager(CONFIG_FILE, app.logger_instance)

    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app.register_blueprint(api_blueprint, url_prefix="/api")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon"
        )

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.logger_instance.info("Starte Flask-Server...")
    flask_app.run(host="0.0.0.0", port=5001, debug=False)
