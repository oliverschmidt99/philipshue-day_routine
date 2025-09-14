"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge (v2 API).
"""
from flask import Blueprint, jsonify, current_app
from src.hue_wrapper import HueBridge

bridge_api = Blueprint("bridge_api", __name__)

def get_bridge_instance() -> HueBridge | None:
    config = current_app.config_manager.get_full_config()
    bridge = HueBridge(ip=config.get("bridge_ip"), app_key=config.get("app_key"), logger=current_app.logger_instance)
    return bridge if bridge.is_connected() else None

@bridge_api.route("/all_items")
def get_all_bridge_items():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    bridge_data = bridge.get_api_data()
    
    # Gruppen (Räume und Zonen)
    rooms = [{"id": r['id'], "name": r['metadata']['name'], "lights": [s['rid'] for s in r.get('services', []) if s.get('rtype') == 'light']} for r in bridge_data.get("rooms", [])]
    zones = [{"id": z['id'], "name": z['metadata']['name'], "lights": [s['rid'] for s in z.get('services', []) if s.get('rtype') == 'light']} for z in bridge_data.get("zones", [])]
    all_groups_for_routines = rooms + zones

    # Gerätekategorisierung
    lights_and_plugs = []
    switches = []
    sensors = []

    for device in bridge_data.get("devices", []):
        device_info = {
            "id": device.get('id'),
            "name": device.get('metadata', {}).get('name'),
            "product_name": device.get('product_data', {}).get('product_name')
        }
        
        # Prüfe Services, um das Gerät zu kategorisieren
        is_light = any(s.get('rtype') == 'light' for s in device.get('services', []))
        is_plug = any(s.get('rtype') == 'smart_plug' for s in device.get('services', []))
        is_switch = any(s.get('rtype') in ['button', 'relative_rotary'] for s in device.get('services', []))
        is_sensor = any(s.get('rtype') in ['motion', 'light_level', 'temperature'] for s in device.get('services', []))

        if is_light or is_plug:
            lights_and_plugs.append(device_info)
        if is_switch:
            switches.append(device_info)
        if is_sensor:
            sensors.append(device_info)
            
    # Alte Sensor-Liste für Abwärtskompatibilität (z.B. Analyse-Tab)
    all_sensors_flat = sensors

    return jsonify({
        "rooms": rooms,
        "zones": zones,
        "groups": all_groups_for_routines,
        "devices": {
            "lights_and_plugs": lights_and_plugs,
            "switches": switches,
            "sensors": sensors
        },
        "sensors": all_sensors_flat 
    })