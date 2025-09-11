"""
API-Endpunkte für den Ersteinrichtungs-Assistenten.
"""
import requests
from flask import Blueprint, jsonify, request, current_app
from phue import Bridge, PhueException

setup_api = Blueprint("setup_api", __name__)

@setup_api.route("/status")
def get_setup_status():
    """Prüft, ob die Anwendung bereits eingerichtet ist."""
    config = current_app.config_manager.get_full_config()
    if config and config.get("bridge_ip") and config.get("app_key"):
        return jsonify({"setup_needed": False})
    return jsonify({"setup_needed": True})

@setup_api.route("/discover")
def discover_bridges():
    """Sucht nach Hue Bridges im Netzwerk."""
    try:
        response = requests.get("https://discovery.meethue.com/", timeout=10)
        response.raise_for_status()
        return jsonify([b["internalipaddress"] for b in response.json()])
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@setup_api.route("/connect", methods=["POST"])
def connect_to_bridge():
    """Versucht, sich mit einer Bridge zu verbinden und einen App-Key zu erhalten."""
    ip = request.json.get("ip")
    if not ip:
        return jsonify({"error": "IP-Adresse fehlt."}), 400
    try:
        bridge = Bridge(ip)
        bridge.connect()
        return jsonify({"app_key": bridge.username})
    except PhueException as e:
        return jsonify({"error": str(e)}), 500

@setup_api.route("/save", methods=["POST"])
def save_setup_config():
    """Speichert die initiale Konfiguration."""
    data = request.get_json()
    initial_config = {
        "bridge_ip": data.get("bridge_ip"),
        "app_key": data.get("app_key"),
        "location": {
            "latitude": data.get("latitude", ""),
            "longitude": data.get("longitude", "")
        },
        "global_settings": {"loop_interval_s": 1, "status_interval_s": 5},
        "scenes": {}, "rooms": [], "routines": []
    }
    if current_app.config_manager.safe_write(initial_config):
        return jsonify({"message": "Konfiguration gespeichert."})
    return jsonify({"error": "Speichern fehlgeschlagen."}), 500