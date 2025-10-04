"""
API-Endpunkte für das Laden und Speichern von Grundrissdaten.
"""
import os
from flask import Blueprint, jsonify, request, current_app

# *** HIER IST DIE KORREKTUR: floorplan_api -> FloorplanAPI ***
FloorplanAPI = Blueprint("floorplan_api", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FLOORPLAN_FILE = os.path.join(BASE_DIR, "data", "floorplan.yaml")

@FloorplanAPI.route("/", methods=["GET"])
def get_floorplan():
    """Lädt die Grundrissdaten aus der YAML-Datei."""
    try:
        data = current_app.config_manager.load_yaml(FLOORPLAN_FILE)
        return jsonify(data if data else {})
    except FileNotFoundError:
        return jsonify({"error": "Grundriss-Datei nicht gefunden."}), 404
    except Exception as e:
        current_app.logger_instance.error(f"Fehler beim Laden des Grundrisses: {e}")
        return jsonify({"error": "Fehler beim Laden der Grundriss-Datei."}), 500

@FloorplanAPI.route("/", methods=["POST"])
def save_floorplan():
    """Speichert die Grundrissdaten in der YAML-Datei."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten empfangen."}), 400
    
    try:
        if current_app.config_manager.safe_write(FLOORPLAN_FILE, data):
            current_app.logger_instance.info("Grundriss wurde über die API gespeichert.")
            return jsonify({"message": "Grundriss erfolgreich gespeichert."})
        
        return jsonify({"error": "Speichern des Grundrisses fehlgeschlagen."}), 500
    except Exception as e:
        current_app.logger_instance.error(f"Fehler beim Speichern des Grundrisses: {e}")
        return jsonify({"error": "Fehler beim Speichern der Grundriss-Datei."}), 500