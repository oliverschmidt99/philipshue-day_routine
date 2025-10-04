"""
API-Endpunkte für die direkte Kommunikation mit der Philips Hue Bridge (v2 API).
"""
from flask import Blueprint, jsonify, request, current_app
from src.hue_wrapper import HueBridge

BridgeAPI = Blueprint("bridge_api", __name__)

def get_bridge_instance() -> HueBridge | None:
    """Holt die prozess-lokale Bridge-Instanz aus dem App-Kontext."""
    bridge = getattr(current_app, 'bridge_instance', None)
    
    if not bridge:
        current_app.logger_instance.error("Bridge-Instanz wurde nie im App-Kontext erstellt.")
        return None
        
    if not bridge.is_connected():
        current_app.logger_instance.warning("Bridge nicht verbunden. Versuche Wiederverbindung...")
        bridge.connect() # Versuch, die Verbindung wiederherzustellen
        if not bridge.is_connected():
            current_app.logger_instance.error("Wiederverbindung zur Bridge fehlgeschlagen.")
            return None
            
    return bridge

@BridgeAPI.route("/all_grouped_lights")
def get_all_grouped_lights():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    try:
        grouped_lights = bridge.get_grouped_lights()
        return jsonify(grouped_lights)
    except Exception as e:
        current_app.logger_instance.error(f"Unerwarteter Fehler in get_all_grouped_lights: {e}", exc_info=True)
        return jsonify({"error": "Interner Serverfehler beim Abrufen der Gruppenlichter."}), 500


@BridgeAPI.route("/all_items")
def get_all_bridge_items():
    bridge = get_bridge_instance()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar oder konfiguriert"}), 503
    
    try:
        bridge_data = bridge.get_full_api_data()
        return jsonify(bridge_data)
    except Exception as e:
        current_app.logger_instance.error(f"Unerwarteter Fehler in get_all_bridge_items: {e}", exc_info=True)
        return jsonify({"error": "Interner Serverfehler beim Abrufen der Bridge-Daten."}), 500