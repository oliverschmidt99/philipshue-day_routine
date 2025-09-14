"""
API-Endpunkte für Systemaktionen wie Neustart und Update.
"""
import os
import subprocess
import threading
import time
from flask import Blueprint, jsonify, current_app

system_api = Blueprint("system_api", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESTART_FLAG_FILE = os.path.join(BASE_DIR, "data", "restart.flag")

def trigger_restart():
    """Erstellt die Neustart-Datei nach einer kurzen Verzögerung."""
    time.sleep(1)
    with open(RESTART_FLAG_FILE, "w", encoding="utf-8") as f:
        pass # Leere Datei als Signal erstellen

@system_api.route("/restart", methods=["POST"])
def restart_app():
    """Löst einen Neustart der Anwendung aus, nachdem die Antwort gesendet wurde."""
    try:
        # Starte den Neustart in einem Hintergrund-Thread
        threading.Thread(target=trigger_restart).start()
        # Sende sofort eine Erfolgsmeldung zurück
        return jsonify({"message": "Neustart-Signal gesendet."})
    except IOError as e:
        return jsonify({"error": f"Neustart konnte nicht ausgelöst werden: {e}"}), 500

@system_api.route("/update_app", methods=["POST"])
def update_app():
    """Führt 'git pull' aus, um die Anwendung zu aktualisieren."""
    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        return jsonify({"error": "Kein Git-Repository gefunden."}), 500
    try:
        subprocess.run(["git", "stash"], cwd=BASE_DIR, check=True, capture_output=True)
        result = subprocess.run(["git", "pull", "--rebase"], cwd=BASE_DIR, check=True, capture_output=True, text=True)
        subprocess.run(["git", "stash", "pop"], cwd=BASE_DIR, check=True, capture_output=True)
        
        threading.Thread(target=trigger_restart).start()
        return jsonify({"message": f"Update erfolgreich!\n{result.stdout}\nAnwendung wird neu gestartet."})
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        return jsonify({"error": f"Fehler beim Update: {e.stderr if hasattr(e, 'stderr') else e}"}), 500