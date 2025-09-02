"""
API-Endpunkte für Systemaktionen wie Neustart, Update und das Hinzufügen von Szenen.
"""

import os
import subprocess
from flask import Blueprint, jsonify, current_app, render_template
from jinja2 import TemplateNotFound

system_api = Blueprint("system_api", __name__)

# Finde das Hauptverzeichnis und das Datenverzeichnis
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESTART_FLAG_FILE = os.path.join(DATA_DIR, "restart.flag")


@system_api.route("/help")
def get_help_content():
    """Liest und retourniert den HTML-Inhalt der Hilfeseite."""
    log = current_app.logger_instance
    try:
        # render_template sucht automatisch im 'templates'-Ordner
        return render_template("hilfe.html")
    except TemplateNotFound:
        log.error(
            "Fehler beim Laden der Hilfeseite: Vorlage 'hilfe.html' nicht gefunden."
        )
        return "<p>Fehler: Die Hilfedatei konnte nicht gefunden werden.</p>", 404


@system_api.route("/restart", methods=["POST"])
def restart_app():
    """Löst einen Neustart aus, indem eine Flag-Datei für den Hauptprozess erstellt wird."""
    log = current_app.logger_instance
    log.info("Neustart-Anforderung über API erhalten. Setze Neustart-Flag.")
    try:
        # Erstelle die leere Flag-Datei
        with open(RESTART_FLAG_FILE, "w", encoding="utf-8") as _:
            pass
        message = "Neustart-Signal gesendet. Die Anwendung wird in Kürze neu starten."
        return jsonify({"message": message})
    except IOError as e:
        log.error(f"Konnte Neustart-Flag-Datei nicht erstellen: {e}")
        return jsonify({"error": "Neustart konnte nicht ausgelöst werden."}), 500


@system_api.route("/update_app", methods=["POST"])
def update_app():
    """
    Führt 'git pull' aus, um die Anwendung zu aktualisieren.
    Lokale Änderungen werden mit 'git stash' zwischengespeichert.
    """
    log = current_app.logger_instance
    log.info("Update über die API ausgelöst.")

    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        return (
            jsonify({"error": "Kein Git-Repository gefunden. Update nicht möglich."}),
            500,
        )

    try:
        subprocess.run(["git", "stash"], cwd=BASE_DIR, check=True)
        log.info("Lokale Änderungen wurden mit 'git stash' gesichert.")

        result = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        log.info(f"Git Pull erfolgreich: {result.stdout}")

        subprocess.run(["git", "stash", "pop"], cwd=BASE_DIR, check=True)
        log.info("Gesicherte Änderungen wurden wieder angewendet.")

        with open(RESTART_FLAG_FILE, "w", encoding="utf-8") as _:
            pass
        message = f"Update erfolgreich!\n{result.stdout}\nAnwendung wird neu gestartet."
        return jsonify({"message": message})

    except FileNotFoundError:
        log.error("Git ist nicht installiert oder nicht im PATH.")
        return (
            jsonify({"error": "'git' Kommando nicht gefunden. Ist Git installiert?"}),
            500,
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Fehler bei Git-Operation: {e.stderr}")
        return jsonify({"error": f"Fehler beim Update: {e.stderr}"}), 500


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
