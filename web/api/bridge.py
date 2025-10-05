"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge (v2 API).
"""
import json
from flask import Blueprint, jsonify, request, current_app, Response
from src.hue_wrapper import HueBridge

BridgeAPI = Blueprint("bridge_api", __name__)

def get_bridge_instance() -> HueBridge | None:
    """
    Holt die Bridge-Instanz aus dem App-Kontext oder initialisiert sie,
    falls sie bei App-Start noch nicht konfiguriert war (Lazy Initialization).
    """
    bridge = getattr(current_app, 'bridge_instance', None)
    
    if not bridge:
        config = current_app.config_manager.get_full_config()
        bridge_ip = config.get("bridge_ip")
        app_key = config.get("app_key")
        
        if bridge_ip and app_key:
            bridge = HueBridge(
                ip=bridge_ip, app_key=app_key, logger=current_app.logger_instance
            )
            current_app.bridge_instance = bridge
        else:
            current_app.logger_instance.error("JIT-Initialisierung fehlgeschlagen: Bridge-IP/App-Key fehlen.")
            return None

    if not bridge.is_connected():
        bridge.connect()
    
    return bridge if bridge.is_connected() else None

@BridgeAPI.route("/all_grouped_lights")
def get_all_grouped_lights():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    try:
        grouped_lights = bridge.get_grouped_lights()
        return Response(json.dumps(grouped_lights), mimetype='application/json')
    except Exception as e:
        current_app.logger_instance.error(f"Fehler in get_all_grouped_lights: {e}", exc_info=True)
        return jsonify({"error": "Interner Serverfehler"}), 500

@BridgeAPI.route("/all_items")
def get_all_bridge_items():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    try:
        bridge_data = bridge.get_full_api_data()
        all_devices = bridge_data.get("devices", [])
        
        # --- Robuste Datenverarbeitung ---
        rooms = [
            {
                "id": r.get('id'),
                "name": r.get('metadata', {}).get('name', 'Unbenannter Raum'),
                "lights": [child.get('rid') for child in r.get('children', []) if child.get('rtype') == 'light']
            } for r in bridge_data.get("rooms", [])
        ]
        
        zones = [
            {
                "id": z.get('id'),
                "name": z.get('metadata', {}).get('name', 'Unbenannte Zone'),
                "lights": [child.get('rid') for child in z.get('children', []) if child.get('rtype') == 'light']
            } for z in bridge_data.get("zones", [])
        ]

        sensors = [
            {
                "id": dev.get('id'),
                "name": dev.get('metadata', {}).get('name', 'Unbenannter Sensor')
            } for dev in all_devices if any(s.get('rtype') == 'motion' for s in dev.get('services', []))
        ]

        # --- Stabile JSON-Antwort ---
        response_data = {
            "rooms": rooms,
            "zones": zones,
            "sensors": sensors,
            "lights": bridge_data.get("lights", []),
            "scenes": bridge_data.get("scenes", [])
        }
        return Response(json.dumps(response_data), mimetype='application/json')

    except Exception as e:
        current_app.logger_instance.error(f"Fehler beim Verarbeiten der Bridge-Daten in get_all_items: {e}", exc_info=True)
        return jsonify({"error": "Fehler beim Verarbeiten der Bridge-Daten."}), 500

# ... (Rest der Datei bleibt gleich)

@BridgeAPI.route("/grouped_light/<group_id>/state", methods=["POST"])
def set_group_light_state(group_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    state = request.get_json()
    if not state:
        return jsonify({"error": "Kein Zustand übergeben"}), 400
    bridge.set_group_state(group_id, state)
    return jsonify({"message": "Befehl für Gruppe gesendet"})

@BridgeAPI.route("/light/<light_id>/state", methods=["POST"])
def set_light_state(light_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    state = request.get_json()
    if not state:
        return jsonify({"error": "Kein Zustand übergeben"}), 400
    bridge.set_light_state(light_id, state)
    return jsonify({"message": "Befehl für Licht gesendet"})

@BridgeAPI.route("/group/<group_id>/scene", methods=["POST"])
def recall_scene_for_group(group_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    scene_id = request.json.get("scene_id")
    if not scene_id:
        return jsonify({"error": "Keine Szene-ID übergeben"}), 400
    bridge.recall_scene(scene_id)
    return jsonify({"message": f"Szene {scene_id} aktiviert."})

@BridgeAPI.route("/scenes", methods=["POST"])
def create_scene():
    bridge = get_bridge_instance()
    if not bridge: return jsonify({"error": "Bridge nicht erreichbar"}), 503
    data = request.get_json()
    group_type = 'room' if bridge.get_resource_by_id('room', data.get("group_id")) else 'zone'
    response = bridge.create_scene(
        name=data.get("name"), group_id=data.get("group_id"),
        group_type=group_type, actions=data.get("actions")
    )
    if response:
        return jsonify({"message": f"Szene '{data.get('name')}' erstellt.", "data": response}), 201
    return jsonify({"error": "Szene konnte nicht erstellt werden."}), 500

@BridgeAPI.route("/scenes/<scene_id>", methods=["DELETE"])
def delete_scene(scene_id):
    bridge = get_bridge_instance()
    if not bridge: return jsonify({"error": "Bridge nicht erreichbar"}), 503
    bridge.delete_scene(scene_id)
    return jsonify({"message": f"Szene {scene_id} wurde gelöscht."})