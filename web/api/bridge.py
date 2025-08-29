# web/api/bridge.py
from flask import Blueprint, jsonify
from phue import Bridge, PhueException
from ..server import config_manager, log

bridge_api = Blueprint("bridge_api", __name__)


def get_bridge_instance():
    """Hilfsfunktion, um eine Bridge-Instanz zu erstellen."""
    config = config_manager.get_full_config()
    ip = config.get("bridge_ip")
    key = config.get("app_key")
    if not ip or not key:
        return None
    try:
        bridge = Bridge(ip, username=key)
        # Ein kurzer Testaufruf, um die Verbindung zu verifizieren
        bridge.get_api()
        return bridge
    except Exception:
        return None


@bridge_api.route("/all_items")
def get_all_bridge_items():
    """Holt alle relevanten Geräte von der Bridge."""
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    try:
        # Hole alle Daten mit einem einzigen API-Aufruf für Effizienz
        full_state = bridge.get_api()

        lights = full_state.get("lights", {})
        sensors = full_state.get("sensors", {})
        groups = full_state.get("groups", {})

        light_ids_in_groups = {
            lid for g in groups.values() for lid in g.get("lights", [])
        }

        # ZLLPresence ist der Typ für Hue Bewegungsmelder
        motion_sensors = [
            {"id": sid, "name": s["name"]}
            for sid, s in sensors.items()
            if s.get("type") == "ZLLPresence"
        ]

        # Gruppen (Räume/Zonen)
        bridge_groups = [{"id": gid, "name": g["name"]} for gid, g in groups.items()]

        return jsonify({"sensors": motion_sensors, "groups": bridge_groups})

    except PhueException as e:
        log.error(f"Fehler bei der Bridge-Kommunikation: {e}")
        return jsonify({"error": f"Bridge-Fehler: {e}"}), 500
