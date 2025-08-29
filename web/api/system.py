# web/api/system.py
from flask import Blueprint, jsonify
from ..server import config_manager, log

system_api = Blueprint("system_api", __name__)


@system_api.route("/scenes/add_defaults", methods=["POST"])
def add_default_scenes():
    """Fügt Standard-Szenen hinzu oder aktualisiert sie, falls sie nicht existieren."""
    try:
        config = config_manager.get_full_config()
        default_scenes = {
            "entspannen": {"status": True, "bri": 144, "ct": 447},
            "lesen": {"status": True, "bri": 254, "ct": 343},
            "konzentrieren": {"status": True, "bri": 254, "ct": 233},
            "energie_tanken": {"status": True, "bri": 254, "ct": 156},
            "gedimmt": {"status": True, "bri": 77, "ct": 369},
            "nachtlicht": {"status": True, "bri": 1, "ct": 447},
            "aus": {"status": False, "bri": 0},
        }

        # Stelle sicher, dass der 'scenes'-Schlüssel existiert
        if "scenes" not in config:
            config["scenes"] = {}

        # Füge nur die Szenen hinzu, die noch nicht existieren
        new_scenes_added = False
        for name, params in default_scenes.items():
            if name not in config["scenes"]:
                config["scenes"][name] = params
                new_scenes_added = True

        if not new_scenes_added:
            return jsonify({"message": "Alle Standard-Szenen sind bereits vorhanden."})

        if config_manager.safe_write(config):
            return jsonify({"message": "Fehlende Standard-Szenen wurden hinzugefügt."})

        return jsonify({"error": "Speichern der Konfiguration fehlgeschlagen."}), 500
    except Exception as e:
        log.error(f"Fehler beim Hinzufügen der Standard-Szenen: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Hier können zukünftig weitere System-Routen wie /restart, /update etc. eingefügt werden.
