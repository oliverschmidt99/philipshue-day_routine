import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from web.api.bridge import HueBridge
from web.api.config_api import ConfigAPI
from web.api.data import DataAPI
from web.api.floorplan_api import FloorplanAPI
from web.api.setup import SetupAPI
from web.api.system import SystemAPI

app = Flask(__name__, template_folder='templates', static_folder='static')

# API-Endpunkte registrieren
app.register_blueprint(HueBridge, url_prefix='/api/bridge')
app.register_blueprint(ConfigAPI, url_prefix='/api/config')
app.register_blueprint(DataAPI, url_prefix='/api/data')
app.register_blueprint(FloorplanAPI, url_prefix='/api/floorplan')
app.register_blueprint(SetupAPI, url_prefix='/api/setup')
app.register_blueprint(SystemAPI, url_prefix='/api/system')

# Standardrouten für die Webanwendung
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
def main_app():
    return render_template('main_app.html')

# *** NEUE ROUTE FÜR DEN GRUNDRISS-EDITOR ***
@app.route('/floorplan')
def floorplan_page():
    """ Rendert die Seite für den Grundriss-Editor. """
    return render_template('floorplan.html')

# *** NEUE ROUTE, UM BLUEPRINT3D-DATEIEN AUSZULIEFERN ***
@app.route('/blueprint3d/<path:filename>')
def blueprint3d_static(filename):
    """ Liefert statische Dateien aus dem blueprint3d-Verzeichnis aus. """
    directory = os.path.join(app.root_path, '..', 'blueprint3d')
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)