"""
API-Endpunkte für Systemaktionen wie das Hinzufügen von Standard-Szenen.
"""

from flask import Blueprint, jsonify, current_app

system_api = Blueprint("system_api", __name__)


@system_api.route("/scenes/add_defaults", methods=["POST"])
def add_default_scenes():
    """Fügt Standard-Szenen hinzu oder aktualisiert sie, falls sie nicht existieren."""
    config_manager = current_app.config_manager
    log = current_app.logger_instance
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

        if "scenes" not in config:
            config["scenes"] = {}

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
    except (IOError, TypeError, KeyError) as e:
        log.error(f"Fehler beim Hinzufügen der Standard-Szenen: {e}", exc_info=True)
        return jsonify({"error": f"Konfigurations- oder Dateifehler: {e}"}), 500
