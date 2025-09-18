"""
API-Endpunkte für den Ersteinrichtungs-Assistenten (Setup Wizard).
"""
import os
import requests
from flask import Blueprint, jsonify, request, current_app
from src.hue_wrapper import HueBridge

setup_api = Blueprint("setup_api", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.yaml")
AUTOMATION_FILE = os.path.join(DATA_DIR, "automation.yaml")
HOME_FILE = os.path.join(DATA_DIR, "home.yaml")


@setup_api.route("/status")
def get_setup_status():
    config = current_app.config_manager.get_full_config()
    return jsonify({"setup_needed": not (config and config.get("bridge_ip") and config.get("app_key"))})

@setup_api.route("/discover")
def discover_bridges():
    try:
        response = requests.get("https://discovery.meethue.com/", timeout=10)
        response.raise_for_status()
        return jsonify([b["internalipaddress"] for b in response.json()])
    except requests.RequestException as e:
        current_app.logger_instance.error(f"Fehler bei der Bridge-Suche: {e}")
        if e.response is not None and e.response.status_code == 429:
            return jsonify({"error": "Zu viele Anfragen an den Hue-Server. Bitte warte einen Moment und versuche es erneut."}), 429
        return jsonify({"error": str(e)}), 500

@setup_api.route("/connect", methods=["POST"])
def connect_to_bridge():
    ip_address = request.json.get("ip")
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400
    
    new_app_key = HueBridge.create_app_key(ip=ip_address, logger=current_app.logger_instance)
    if new_app_key:
        return jsonify({"app_key": new_app_key})
    else:
        return jsonify({"error": "Der Link-Button auf der Bridge wurde nicht gedrückt oder ein Fehler ist aufgetreten."}), 500

@setup_api.route("/save", methods=["POST"])
def save_setup_config():
    config_manager = current_app.config_manager
    data = request.get_json()

    settings_data = {
        "bridge_ip": data.get("bridge_ip"), "app_key": data.get("app_key"),
        "location": {"latitude": data.get("latitude"), "longitude": data.get("longitude")},
        "global_settings": {"loop_interval_s": 1, "status_interval_s": 5},
    }
    automation_data = {"scenes": {}, "routines": []}
    home_data = {"rooms": []}

    if config_manager.safe_write(SETTINGS_FILE, settings_data) and \
       config_manager.safe_write(AUTOMATION_FILE, automation_data) and \
       config_manager.safe_write(HOME_FILE, home_data):
        return jsonify({"message": "Konfiguration gespeichert."})

    return jsonify({"error": "Speichern fehlgeschlagen."}), 500