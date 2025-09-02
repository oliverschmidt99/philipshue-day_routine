"""
API-Endpunkte für das Management der Konfigurationsdatei (config.yaml),
inklusive Laden, Speichern, Sichern und Wiederherstellen.
"""

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

    # Stelle sicher, dass 'location' keine null-Werte enthält
    if "location" in data and isinstance(data["location"], dict):
        if data["location"].get("latitude") is None:
            data["location"]["latitude"] = ""
        if data["location"].get("longitude") is None:
            data["location"]["longitude"] = ""
    # Falls der location-Block ganz fehlt, füge einen leeren hinzu
    elif "location" not in data:
        data["location"] = {"latitude": "", "longitude": ""}

    if config_manager.safe_write(data):
        log.info("Konfiguration wurde über die API gespeichert.")
        return jsonify({"message": "Konfiguration erfolgreich gespeichert."})

    log.error("Fehler beim Speichern der Konfiguration über die API.")
    return jsonify({"error": "Speichern der Konfiguration fehlgeschlagen."}), 500


@config_api.route("/backup", methods=["POST"])
def backup_config():
    """Erstellt ein Backup der aktuellen Konfigurationsdatei."""
    log = current_app.logger_instance
    log.info("Backup der Konfiguration über API ausgelöst.")
    try:
        shutil.copy(CONFIG_FILE, CONFIG_BACKUP_FILE)
        backup_filename = os.path.basename(CONFIG_BACKUP_FILE)
        return jsonify(
            {"message": f"Konfiguration wurde als '{backup_filename}' gesichert."}
        )
    except (IOError, OSError) as e:
        log.error(f"Fehler beim Backup: {e}", exc_info=True)
        return jsonify({"error": f"Dateifehler beim Sichern: {e}"}), 500


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
    except (IOError, OSError) as e:
        log.error(f"Fehler bei Wiederherstellung: {e}", exc_info=True)
        return jsonify({"error": f"Dateifehler bei Wiederherstellung: {e}"}), 500
