"""
API-Endpunkte für den Ersteinrichtungs-Assistenten (Setup Wizard).
Umfasst die Bridge-Suche, das Koppeln und das Speichern der initialen Konfiguration.
"""

import requests
from flask import Blueprint, jsonify, request, current_app
from phue import Bridge, PhueException

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/status")
def get_setup_status():
    """Prüft, ob die Anwendung bereits eingerichtet wurde."""
    config_manager = current_app.config_manager
    settings = config_manager.get_full_config()
    if settings and settings.get("bridge_ip") and settings.get("app_key"):
        return jsonify({"setup_needed": False})
    return jsonify({"setup_needed": True})


@setup_api.route("/discover")
def discover_bridges():
    """Sucht nach Hue Bridges im Netzwerk."""
    log = current_app.logger_instance
    try:
        response = requests.get("https://discovery.meethue.com/", timeout=10)
        response.raise_for_status()
        return jsonify([b["internalipaddress"] for b in response.json()])
    except requests.RequestException as e:
        log.error(f"Fehler bei der Bridge-Suche: {e}")
        return jsonify({"error": str(e)}), 500


@setup_api.route("/connect", methods=["POST"])
def connect_to_bridge():
    """Versucht, sich mit einer Bridge zu verbinden."""
    log = current_app.logger_instance
    ip_address = request.json.get("ip")
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400
    try:
        bridge = Bridge(ip_address)
        bridge.connect()
        log.info(f"Erfolgreich mit Bridge {ip_address} verbunden und App-Key erhalten.")
        return jsonify({"app_key": bridge.username})
    except PhueException as e:
        log.error(f"Fehler beim Verbinden mit Bridge {ip_address}: {e}")
        error_message = str(e)
        if "101" in error_message:
            error_message = "Der Link-Button auf der Bridge wurde nicht gedrückt."
        return jsonify({"error": error_message}), 500


@setup_api.route("/save", methods=["POST"])
def save_setup_config():
    """Speichert die initiale Konfiguration."""
    config_manager = current_app.config_manager
    log = current_app.logger_instance
    try:
        data = request.get_json()
        initial_config = {
            "bridge_ip": data.get("bridge_ip"),
            "app_key": data.get("app_key"),
            "location": data.get("location", {}),
            "global_settings": {
                "loop_interval_s": 1,
                "status_interval_s": 5,
            },
            "scenes": {},
            "rooms": [],
            "routines": [],
        }
        if config_manager.safe_write(initial_config):
            log.info("Ersteinrichtung abgeschlossen und Konfiguration gespeichert.")
            return jsonify({"message": "Konfiguration gespeichert."})
        return jsonify({"error": "Speichern fehlgeschlagen."}), 500
    except (TypeError, KeyError) as e:
        log.error(f"Fehler beim Speichern der Setup-Konfiguration: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
