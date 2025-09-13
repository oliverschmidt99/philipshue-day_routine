"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge.
"""
from flask import Blueprint, jsonify, current_app

# KEIN Import aus 'src' hier auf oberster Ebene

bridge_api = Blueprint("bridge_api", __name__)

def get_bridge_instance():
    """Hilfsfunktion, um eine Bridge-Instanz aus der App-Konfiguration zu erstellen."""
    # Importiere den Wrapper hier, innerhalb der Funktion
    from src.hue_wrapper import HueBridge

    config = current_app.config_manager.get_full_config()
    ip = config.get("bridge_ip")
    key = config.get("app_key")
    if not ip or not key:
        return None

    bridge = HueBridge(ip=ip, username=key, logger=current_app.logger_instance)
    if bridge.is_connected():
        return bridge
    return None

@bridge_api.route("/all_items")
def get_all_bridge_items():
    """Holt alle relevanten Geräte (Gruppen, Sensoren) von der Bridge."""
    log = current_app.logger_instance
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503

    full_state = bridge.get_full_api_state()
    if not full_state:
        log.error("Fehler bei der Bridge-Kommunikation: Konnte API-Status nicht abrufen.")
        return jsonify({"error": "Bridge-Fehler: Konnte API-Status nicht abrufen."}), 500

    sensors = full_state.get("sensors", {})
    groups = full_state.get("groups", {})

    motion_sensors = [
        {"id": sid, "name": s["name"]}
        for sid, s in sensors.items()
        if s.get("type") == "ZLLPresence"
    ]
    bridge_groups = [{"id": gid, "name": g["name"]} for gid, g in groups.items()]
    return jsonify({"sensors": motion_sensors, "groups": bridge_groups})