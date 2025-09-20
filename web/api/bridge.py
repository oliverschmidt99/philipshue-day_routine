"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge (v2 API).
"""
from flask import Blueprint, jsonify, request, current_app
from src.hue_wrapper import HueBridge

bridge_api = Blueprint("bridge_api", __name__)

def get_bridge_instance() -> HueBridge | None:
    """Holt die globale, geteilte Bridge-Instanz aus dem App-Kontext."""
    bridge = current_app.bridge_instance
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
    
    bridge_data = bridge.get_full_api_data()
    all_devices = bridge_data.get("devices", [])
    
    # FINALE KORREKTUR: Wir nutzen jetzt die saubere Logik aus dem neuen Wrapper.
    rooms = []
    for r in bridge_data.get("rooms", []):
        # Hole die Lampen über die korrekte Wrapper-Funktion
        light_objects = bridge.get_lights_in_group(r['id'])
        # Extrahiere nur die IDs für das Frontend
        light_ids = [light['id'] for light in light_objects if light]
        rooms.append({
            "id": r['id'],
            "name": r['metadata']['name'],
            "lights": light_ids
        })
    
    zones = []
    for z in bridge_data.get("zones", []):
        # Nutze dieselbe Logik für Zonen
        light_objects = bridge.get_lights_in_group(z['id'])
        light_ids = [light['id'] for light in light_objects if light]
        zones.append({
            "id": z['id'],
            "name": z['metadata']['name'],
            "lights": light_ids
        })

    all_groups_for_routines = rooms + zones
    all_sensors_flat = []
    categorized_sensors = {}
    
    for device in all_devices:
        sensor_info = {"id": device['id'], "name": device['metadata']['name'], "productname": device['product_data']['product_name']}
        for service in device.get('services', []):
            if service.get('rtype') == 'motion':
                if "Bewegung" not in categorized_sensors: categorized_sensors["Bewegung"] = []
                categorized_sensors["Bewegung"].append(sensor_info)
                all_sensors_flat.append(sensor_info)
                break

    return jsonify({
        "rooms": rooms,
        "zones": zones,
        "groups": all_groups_for_routines,
        "sensors_categorized": categorized_sensors,
        "sensors": all_sensors_flat,
        "lights": bridge_data.get("lights", []),
        "scenes": bridge_data.get("scenes", [])
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

    bridge.recall_scene(scene_id)
    
    return jsonify({"message": f"Szene {scene_id} aktiviert."})