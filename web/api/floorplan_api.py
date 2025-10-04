"""
API-Endpunkte für den Blueprint3D-Grundriss-Editor.
"""
import os
import yaml
from flask import Blueprint, jsonify, request, current_app

floorplan_api = Blueprint("floorplan_api", __name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(project_root, "data")
FLOORPLAN_FILE = os.path.join(DATA_DIR, "floorplan.json") # Wir nutzen JSON für die Kompatibilität

@floorplan_api.route("/", methods=["GET"])
def get_floorplan_config():
    """Gibt die aktuelle Grundriss-Konfiguration als JSON zurück."""
    try:
        if os.path.exists(FLOORPLAN_FILE):
            with open(FLOORPLAN_FILE, "r", encoding="utf-8") as f:
                # Flask's jsonify wird das Dict korrekt als JSON senden
                return jsonify(yaml.safe_load(f) or {})
        return jsonify({})
    except (IOError, yaml.YAMLError) as e:
        current_app.logger_instance.error(f"Fehler beim Laden von {FLOORPLAN_FILE}: {e}")
        return jsonify({"error": "Konnte Grundriss-Konfiguration nicht laden."}), 500

@floorplan_api.route("/", methods=["POST"])
def save_floorplan_config():
    """Speichert die Grundriss-Konfiguration, die als JSON vom Editor kommt."""
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Ungültiges JSON-Format"}), 400

    try:
        temp_file = FLOORPLAN_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            # Wir speichern als YAML, um konsistent zu bleiben, aber JSON wäre auch ok
            yaml.dump(data, f, indent=2, allow_unicode=True, default_flow_style=False)
        os.replace(temp_file, FLOORPLAN_FILE)
        current_app.logger_instance.info("Grundriss-Konfiguration wurde gespeichert.")
        return jsonify({"message": "Grundriss erfolgreich gespeichert."})
    except (IOError, yaml.YAMLError) as e:
        current_app.logger_instance.error(f"Fehler beim Speichern von {FLOORPLAN_FILE}: {e}")
        return jsonify({"error": "Speichern des Grundrisses fehlgeschlagen."}), 500