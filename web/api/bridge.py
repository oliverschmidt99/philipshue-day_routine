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
    
    def get_light_ids_for_devices(device_ids):
        """Hilfsfunktion: Sucht alle Lampen-IDs (services), die zu einer Liste von Geräte-IDs gehören."""
        light_ids = []
        for device in all_devices:
            if device['id'] in device_ids:
                for service in device.get('services', []):
                    if service.get('rtype') == 'light':
                        light_ids.append(service['rid'])
        return light_ids

    rooms = []
    for r in bridge_data.get("rooms", []):
        device_ids = [child['rid'] for child in r.get('children', [])]
        rooms.append({
            "id": r['id'],
            "name": r['metadata']['name'],
            "lights": get_light_ids_for_devices(device_ids)
        })
    
    zones = []
    for z in bridge_data.get("zones", []):
        zones.append({
            "id": z['id'],
            "name": z['metadata']['name'],
            "lights": [s['rid'] for s in z.get('services', []) if s.get('rtype') == 'light']
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

# /// NEUE API-ENDPUNKTE FÜR SZENEN-MANAGEMENT ///

@bridge_api.route("/scenes", methods=["POST"])
def create_scene():
    """Erstellt eine neue Szene auf der Hue Bridge."""
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar"}), 503
        
    data = request.get_json()
    # Logik, um zu bestimmen, ob es ein Raum oder eine Zone ist
    group_type = 'room' if bridge.get_resource_by_id('room', data.get("group_id")) else 'zone'

    response = bridge.create_scene(
        name=data.get("name"),
        group_id=data.get("group_id"),
        group_type=group_type,
        actions=data.get("actions")
    )
    if response:
        return jsonify({"message": f"Szene '{data.get('name')}' erstellt.", "data": response}), 201
    return jsonify({"error": "Szene konnte nicht erstellt werden."}), 500

@bridge_api.route("/scenes/<scene_id>", methods=["DELETE"])
def delete_scene(scene_id):
    """Löscht eine Szene von der Hue Bridge."""
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar"}), 503
        
    bridge.delete_scene(scene_id)
    return jsonify({"message": f"Szene {scene_id} wurde gelöscht."})