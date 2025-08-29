# web/api/setup.py
import requests
from flask import Blueprint, jsonify, request
from phue import Bridge, PhueException
from ..server import config_manager, CONFIG_FILE

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/status")
def get_setup_status():
    """Prüft, ob die Anwendung bereits eingerichtet wurde."""
    settings = config_manager.get_settings()
    if settings and settings.get("bridge_ip") and settings.get("app_key"):
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
    """Versucht, sich mit einer Bridge zu verbinden."""
    ip_address = request.json.get("ip")
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400
    try:
        bridge = Bridge(ip_address)
        bridge.connect()
        return jsonify({"app_key": bridge.username})
    except PhueException as e:
        return jsonify({"error": str(e)}), 500


@setup_api.route("/save", methods=["POST"])
def save_setup_config():
    """Speichert die initiale Konfiguration."""
    try:
        data = request.get_json()
        if config_manager.save_full_config(data):
            config_manager.safe_write(
                CONFIG_FILE, {"scenes": {}, "rooms": [], "routines": []}
            )
            return jsonify({"message": "Konfiguration gespeichert."})
        return jsonify({"error": "Speichern fehlgeschlagen."}), 500
    except (TypeError, KeyError) as e:
        return jsonify({"error": str(e)}), 500
