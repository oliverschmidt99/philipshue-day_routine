"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge.
Dient zum Abrufen von Informationen über Lichter, Gruppen und Sensoren.
"""

from flask import Blueprint, jsonify, current_app
from phue import Bridge, PhueException
from requests.exceptions import RequestException

bridge_api = Blueprint("bridge_api", __name__)


def get_bridge_instance():
    """Hilfsfunktion, um eine Bridge-Instanz aus der App-Konfiguration zu erstellen."""
    config = current_app.config_manager.get_full_config()
    ip = config.get("bridge_ip")
    key = config.get("app_key")
    if not ip or not key:
        return None
    try:
        bridge = Bridge(ip, username=key)
        bridge.get_api()
        return bridge
    except (PhueException, RequestException):
        return None


@bridge_api.route("/all_items")
def get_all_bridge_items():
    """Holt alle relevanten Geräte von der Bridge."""
    log = current_app.logger_instance
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    try:
        full_state = bridge.get_api()

        sensors = full_state.get("sensors", {})
        groups = full_state.get("groups", {})

        motion_sensors = [
            {"id": sid, "name": s["name"]}
            for sid, s in sensors.items()
            if s.get("type") == "ZLLPresence"
        ]

        bridge_groups = [{"id": gid, "name": g["name"]} for gid, g in groups.items()]

        return jsonify({"sensors": motion_sensors, "groups": bridge_groups})

    except PhueException as e:
        log.error(f"Fehler bei der Bridge-Kommunikation: {e}")
        return jsonify({"error": f"Bridge-Fehler: {e}"}), 500
