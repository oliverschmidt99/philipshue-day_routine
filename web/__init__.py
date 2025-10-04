import os
from flask import Flask, render_template, send_from_directory

from .api.bridge import BridgeAPI
from .api.config_api import ConfigAPI
from .api.data import DataAPI
from .api.floorplan_api import FloorplanAPI
from .api.setup import SetupAPI
from .api.system import SystemAPI

def create_app(config_manager=None, bridge_instance=None, logger_instance=None):
    """
    Erstellt und konfiguriert die Flask-Anwendung (Application Factory).
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Hänge die geteilten Instanzen an das App-Objekt an.
    # So sind sie über `current_app` in den Blueprints verfügbar.
    app.config_manager = config_manager
    app.bridge_instance = bridge_instance
    app.logger_instance = logger_instance

    # API-Endpunkte (Blueprints) registrieren
    app.register_blueprint(BridgeAPI, url_prefix='/api/bridge')
    app.register_blueprint(ConfigAPI, url_prefix='/api/config')
    app.register_blueprint(DataAPI, url_prefix='/api/data')
    app.register_blueprint(FloorplanAPI, url_prefix='/api/floorplan')
    app.register_blueprint(SetupAPI, url_prefix='/api/setup')
    app.register_blueprint(SystemAPI, url_prefix='/api/system')

    # Standardrouten für die Webanwendung
    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/app')
    def main_app_route():
        return render_template("main_app.html")

    # Route für die blueprint3d-Dateien
    @app.route('/blueprint3d/<path:filename>')
    def blueprint3d_static(filename):
        directory = os.path.join(app.root_path, '..', 'blueprint3d')
        return send_from_directory(directory, filename)

    return app