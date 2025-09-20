"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge (v2 API).
"""
from flask import Blueprint, jsonify, request, current_app
from src.hue_wrapper import HueBridge

bridge_api = Blueprint("bridge_api", __name__)

def get_bridge_instance() -> HueBridge | None:
    """Holt die globale, geteilte Bridge-Instanz aus dem App-Kontext."""
    bridge = current_app.bridge_instance
    # Prüfe bei jeder Anfrage, ob die Verbindung noch steht.
    # Das ist wichtig, falls die Konfiguration geändert wurde.
    if not bridge.is_connected():
        config = current_app.config_manager.get_full_config()
        bridge.ip = config.get("bridge_ip")
        bridge.app_key = config.get("app_key")
        bridge.connect()
    
    return bridge if bridge.is_connected() else None

@bridge_api.route("/all_grouped_lights")
def get_all_grouped_lights():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    grouped_lights = bridge.get_grouped_lights()
    return jsonify(grouped_lights)


@bridge_api.route("/all_items")
def get_all_bridge_items():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    bridge_data = bridge.get_api_data()
    
    rooms = [{"id": r['id'], "name": r['metadata']['name'], "lights": [s['rid'] for s in r.get('services', []) if s.get('rtype') == 'light']} for r in bridge_data.get("rooms", [])]
    zones = [{"id": z['id'], "name": z['metadata']['name'], "lights": [s['rid'] for s in z.get('services', []) if s.get('rtype') == 'light']} for z in bridge_data.get("zones", [])]
    all_groups_for_routines = rooms + zones

    all_sensors_flat = []
    categorized_sensors = {}
    
    for device in bridge_data.get("devices", []):
        is_sensor = False
        sensor_info = {"id": device['id'], "name": device['metadata']['name'], "productname": device['product_data']['product_name']}
        
        for service in device.get('services', []):
            rtype = service.get('rtype')
            if rtype == 'motion':
                if "Bewegung" not in categorized_sensors: categorized_sensors["Bewegung"] = []
                categorized_sensors["Bewegung"].append(sensor_info)
                is_sensor = True
        
        if is_sensor:
            all_sensors_flat.append(sensor_info)

    return jsonify({
        "rooms": rooms,
        "zones": zones,
        "groups": all_groups_for_routines,
        "sensors_categorized": categorized_sensors,
        "sensors": all_sensors_flat,
        "lights": bridge.get_lights(),
        "scenes": bridge.get_scenes()
    })

@bridge_api.route("/grouped_light/<group_id>/state", methods=["POST"])
def set_group_light_state(group_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    state = request.get_json()
    if not state:
        return jsonify({"error": "Kein Zustand übergeben"}), 400

    bridge.set_group_state(group_id, state)
    return jsonify({"message": "Befehl für Gruppe gesendet"})

@bridge_api.route("/light/<light_id>/state", methods=["POST"])
def set_light_state(light_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    state = request.get_json()
    if not state:
        return jsonify({"error": "Kein Zustand übergeben"}), 400

    bridge.set_light_state(light_id, state)
    return jsonify({"message": "Befehl für Licht gesendet"})


@bridge_api.route("/group/<group_id>/scene", methods=["POST"])
def recall_scene_for_group(group_id):
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503

    scene_id = request.json.get("scene_id")
    if not scene_id:
        return jsonify({"error": "Keine Szene-ID übergeben"}), 400

    # Die Hue v2 API erwartet die scene ID im "scene" Feld des Payloads
    state = {"scene": scene_id}
    bridge.set_group_state(group_id, state)
    
    return jsonify({"message": f"Szene {scene_id} für Gruppe {group_id} aktiviert."})