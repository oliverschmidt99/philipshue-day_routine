"""
API-Endpunkte für Systemaktionen wie Neustart und Update.
"""
import os
import subprocess
from flask import Blueprint, jsonify, current_app

SystemAPI = Blueprint("system_api", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESTART_FLAG_FILE = os.path.join(BASE_DIR, "data", "restart.flag")

@SystemAPI.route("/restart", methods=["POST"])
def restart_app():
    """Löst einen Neustart der Anwendung aus."""
    try:
        with open(RESTART_FLAG_FILE, "w", encoding="utf-8") as f:
            pass # Leere Datei als Signal erstellen
        return jsonify({"message": "Neustart-Signal gesendet."})
    except IOError as e:
        return jsonify({"error": f"Neustart konnte nicht ausgelöst werden: {e}"}), 500

@SystemAPI.route("/update_app", methods=["POST"])
def update_app():
    """Führt 'git pull' aus, um die Anwendung zu aktualisieren."""
    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        return jsonify({"error": "Kein Git-Repository gefunden."}), 500
    try:
        subprocess.run(["git", "stash"], cwd=BASE_DIR, check=True, capture_output=True)
        result = subprocess.run(["git", "pull", "--rebase"], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        subprocess.run(["git", "stash", "pop"], cwd=BASE_DIR, check=True, capture_output=True)
        
        with open(RESTART_FLAG_FILE, "w", encoding="utf-8") as f:
            pass
        return jsonify({"message": f"Update erfolgreich!\n{result.stdout}\nAnwendung wird neu gestartet."})
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        return jsonify({"error": f"Fehler beim Update: {e.stderr if hasattr(e, 'stderr') else e}"}), 500

@SystemAPI.route("/scenes/add_defaults", methods=["POST"])
def add_default_scenes():
    """Fügt Standard-Lichtszenen zur Konfiguration hinzu."""
    try:
        config_manager = current_app.config_manager
        full_config = config_manager.get_full_config()
        
        automation_config = {
            "automations": full_config.get("automations", []),
            "scenes": full_config.get("scenes", {})
        }

        default_scenes = {
            "entspannen": {"status": True, "bri": 140, "ct": 366},
            "konzentrieren": {"status": True, "bri": 254, "ct": 233},
            "nachtlicht": {"status": True, "bri": 1, "ct": 447},
            "gedimmt": {"status": True, "bri": 77, "ct": 366},
            "aus": {"status": False, "bri": 0}
        }
        
        scenes_added_count = 0
        for name, data in default_scenes.items():
            if name not in automation_config["scenes"]:
                automation_config["scenes"][name] = data
                scenes_added_count += 1
        
        if scenes_added_count > 0:
            if config_manager.safe_write(config_manager.automation_file, automation_config):
                return jsonify({"message": f"{scenes_added_count} Standard-Szenen wurden hinzugefügt."})
            else:
                return jsonify({"error": "Speichern der neuen Szenen fehlgeschlagen."}), 500
        else:
            return jsonify({"message": "Alle Standard-Szenen sind bereits vorhanden."})
            
    except Exception as e:
        current_app.logger_instance.error(f"Fehler beim Hinzufügen der Standard-Szenen: {e}", exc_info=True)
        return jsonify({"error": "Ein interner Fehler ist aufgetreten."}), 500