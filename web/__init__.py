import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from src.hue_wrapper import HueBridge

from .api.bridge import BridgeAPI
from .api.config_api import ConfigAPI
from .api.data import DataAPI
from .api.floorplan_api import FloorplanAPI
from .api.setup import SetupAPI
from .api.system import SystemAPI

def create_app(config_manager=None, logger_instance=None, app_config=None):
    """
    Erstellt und konfiguriert die Flask-Anwendung (Application Factory).
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)

    # HIER DIE ÄNDERUNG: Erstelle eine prozess-lokale Bridge-Instanz für den Webserver.
    if app_config and app_config.get("bridge_ip"):
        bridge = HueBridge(
            ip=app_config.get("bridge_ip"),
            app_key=app_config.get("app_key"),
            logger=logger_instance
        )
        bridge.connect()
        app.bridge_instance = bridge
    else:
        app.bridge_instance = None
        logger_instance.warning("Keine Bridge-Konfiguration für den Webserver gefunden.")

    app.config_manager = config_manager
    app.logger_instance = logger_instance

    # API-Endpunkte (Blueprints) registrieren
    app.register_blueprint(BridgeAPI, url_prefix='/api/bridge')
    app.register_blueprint(ConfigAPI, url_prefix='/api/config')
    app.register_blueprint(DataAPI, url_prefix='/api/data')
    app.register_blueprint(FloorplanAPI, url_prefix='/api/floorplan')
    app.register_blueprint(SetupAPI, url_prefix='/api/setup')
    app.register_blueprint(SystemAPI, url_prefix='/api/system')

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/blueprint3d/<path:filename>')
    def blueprint3d_static(filename):
        directory = os.path.join(app.root_path, '..', 'blueprint3d')
        return send_from_directory(directory, filename)

    return app