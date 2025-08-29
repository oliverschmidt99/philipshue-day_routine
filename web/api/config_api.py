# web/api/config_api.py
from flask import Blueprint, jsonify, request, current_app

config_api = Blueprint("config_api", __name__)


@config_api.route("/", methods=["GET"])
def get_config():
    """Gibt die gesamte Konfiguration zurück."""
    config_manager = current_app.config_manager
    config = config_manager.get_full_config()
    return jsonify(config)


@config_api.route("/", methods=["POST"])
def save_config():
    """Speichert die gesamte Konfiguration."""
    config_manager = current_app.config_manager
    log = current_app.logger_instance
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Ungültiges Format, JSON-Objekt erwartet."}), 400

    if config_manager.safe_write(data):
        log.info("Konfiguration wurde über die API gespeichert.")
        return jsonify({"message": "Konfiguration erfolgreich gespeichert."})
    else:
        log.error("Fehler beim Speichern der Konfiguration über die API.")
        return jsonify({"error": "Speichern der Konfiguration fehlgeschlagen."}), 500
