"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge.
Dient zum Abrufen von Informationen über Lichter, Gruppen und Sensoren.
"""

from flask import Blueprint, jsonify, current_app, request
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


@bridge_api.route("/<item_type>/<int:item_id>/rename", methods=["POST"])
def rename_item(item_type, item_id):
    """Benennt ein Gerät auf der Bridge um."""
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar"}), 503

    data = request.get_json()
    new_name = data.get("name")

    if not new_name:
        return jsonify({"error": "Fehlende Parameter"}), 400

    try:
        if item_type == "light":
            bridge.set_light(item_id, "name", new_name)
        elif item_type == "group":
            bridge.set_group(item_id, "name", new_name)
        elif item_type == "sensor":
            bridge.set_sensor_config(item_id, {"name": new_name})
        else:
            return jsonify({"error": "Ungültiger Gerätetyp"}), 400
        return jsonify({"message": f"{item_type} erfolgreich umbenannt."})
    except (PhueException, RequestException) as e:
        return jsonify({"error": f"Fehler beim Umbenennen: {e}"}), 500


@bridge_api.route("/<item_type>/<int:item_id>/delete", methods=["DELETE"])
def delete_item(item_type, item_id):
    """Löscht ein Gerät von der Bridge."""
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar"}), 503

    try:
        # pylint: disable=no-member
        if item_type == "light":
            bridge.delete_light(item_id)
        elif item_type == "group":
            bridge.delete_group(item_id)
        elif item_type == "sensor":
            bridge.delete_sensor(item_id)
        else:
            return jsonify({"error": "Ungültiger Gerätetyp"}), 400
        return jsonify({"message": f"{item_type} erfolgreich gelöscht."})
    except (PhueException, RequestException) as e:
        return jsonify({"error": f"Fehler beim Löschen: {e}"}), 500
