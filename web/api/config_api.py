# web/api/config_api.py
import os
import shutil
from flask import Blueprint, jsonify, request, current_app

config_api = Blueprint("config_api", __name__)
# Definiere die Pfade relativ zur aktuellen Datei
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
CONFIG_BACKUP_FILE = os.path.join(DATA_DIR, "config.backup.yaml")


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


# =======================================================================
# HIER SIND DIE FEHLENDEN FUNKTIONEN
# =======================================================================
@config_api.route("/backup", methods=["POST"])
def backup_config():
    """Erstellt ein Backup der aktuellen Konfigurationsdatei."""
    log = current_app.logger_instance
    log.info("Backup der Konfiguration über API ausgelöst.")
    try:
        shutil.copy(CONFIG_FILE, CONFIG_BACKUP_FILE)
        return jsonify(
            {
                "message": f"Konfiguration wurde als '{os.path.basename(CONFIG_BACKUP_FILE)}' gesichert."
            }
        )
    except Exception as e:
        log.error(f"Fehler beim Backup: {e}")
        return jsonify({"error": str(e)}), 500


@config_api.route("/restore", methods=["POST"])
def restore_config():
    """Stellt die Konfiguration aus einem Backup wieder her."""
    log = current_app.logger_instance
    log.info("Wiederherstellung der Konfiguration über API ausgelöst.")
    try:
        if not os.path.exists(CONFIG_BACKUP_FILE):
            return jsonify({"error": "Keine Backup-Datei gefunden."}), 404
        shutil.copy(CONFIG_BACKUP_FILE, CONFIG_FILE)
        return jsonify({"message": "Konfiguration aus Backup wiederhergestellt."})
    except Exception as e:
        log.error(f"Fehler bei Wiederherstellung: {e}")
        return jsonify({"error": str(e)}), 500


# =======================================================================
