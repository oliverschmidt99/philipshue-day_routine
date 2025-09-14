"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge.
"""
from flask import Blueprint, jsonify, current_app
from src.hue_wrapper import HueBridge

bridge_api = Blueprint("bridge_api", __name__)

def get_bridge_instance():
    config = current_app.config_manager.get_full_config()
    bridge = HueBridge(ip=config.get("bridge_ip"), username=config.get("app_key"), logger=current_app.logger_instance)
    return bridge if bridge.is_connected() else None

@bridge_api.route("/all_items")
def get_all_bridge_items():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    full_state = bridge.get_api()
    if not full_state:
        return jsonify({"error": "Bridge-Fehler: Konnte API-Status nicht abrufen."}), 500

    sensors = full_state.get("sensors", {})
    groups = full_state.get("groups", {})

    # Filtert nur die Bewegungssensoren heraus
    motion_sensors = [{"id": sid, "name": s["name"]} for sid, s in sensors.items() if s.get("type") == "ZLLPresence"]
    
    # Holt jetzt ALLE Gruppen (Räume, Zonen und Bewegungszonen)
    bridge_groups = [{"id": gid, "name": g["name"]} for gid, g in groups.items()]
    
    return jsonify({"sensors": motion_sensors, "groups": bridge_groups})