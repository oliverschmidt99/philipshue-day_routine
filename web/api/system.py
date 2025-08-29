# web/api/system.py
from flask import Blueprint, jsonify
from ..server import config_manager, log

system_api = Blueprint("system_api", __name__)


@system_api.route("/scenes/add_defaults", methods=["POST"])
def add_default_scenes():
    """Fügt Standard-Szenen hinzu oder aktualisiert sie."""
    try:
        config = config_manager.get_full_config()
        default_scenes = {
            "entspannen": {"status": True, "bri": 144, "ct": 447},
            "lesen": {"status": True, "bri": 254, "ct": 343},
            "konzentrieren": {"status": True, "bri": 254, "ct": 233},
        }
        config.setdefault("scenes", {}).update(default_scenes)

        if config_manager.save_full_config(config):
            return jsonify({"message": "Standard-Szenen wurden hinzugefügt."})
        return jsonify({"error": "Speichern der Konfiguration fehlgeschlagen."}), 500
    except (IOError, TypeError) as e:
        log.error(f"Fehler beim Hinzufügen der Standard-Szenen: {e}")
        return jsonify({"error": str(e)}), 500


# Hier können zukünftig weitere System-Routen wie /restart, /update etc. eingefügt werden.
