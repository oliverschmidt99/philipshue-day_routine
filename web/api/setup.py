# web/api/setup.py
import requests
from flask import Blueprint, jsonify, request
from phue import Bridge, PhueException
from ..server import config_manager, log

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/status")
def get_setup_status():
    """Prüft, ob die Anwendung bereits eingerichtet wurde."""
    settings = config_manager.get_full_config()
    # Setup ist nötig, wenn IP oder Key fehlen
    if settings and settings.get("bridge_ip") and settings.get("app_key"):
        return jsonify({"setup_needed": False})
    return jsonify({"setup_needed": True})


@setup_api.route("/discover")
def discover_bridges():
    """Sucht nach Hue Bridges im Netzwerk über den Discovery-Service."""
    try:
        response = requests.get("https://discovery.meethue.com/", timeout=10)
        response.raise_for_status()
        # Gebe nur die IPs als Liste von Strings zurück
        return jsonify([b["internalipaddress"] for b in response.json()])
    except requests.RequestException as e:
        log.error(f"Fehler bei der Bridge-Suche: {e}")
        return jsonify({"error": f"Netzwerkfehler bei der Bridge-Suche: {e}"}), 500


@setup_api.route("/connect", methods=["POST"])
def connect_to_bridge():
    """Versucht, sich mit einer Bridge zu verbinden und einen App-Key zu erstellen."""
    ip_address = request.json.get("ip")
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400
    try:
        # Konfigurationsdatei wird nicht übergeben, da wir hier nur einen Key generieren wollen
        bridge = Bridge(ip_address)
        # Dieser Aufruf blockiert, bis der Button gedrückt wird oder ein Timeout auftritt
        bridge.connect()
        log.info(f"Erfolgreich mit Bridge {ip_address} verbunden und App-Key erhalten.")
        return jsonify({"app_key": bridge.username})
    except PhueException as e:
        log.error(f"Fehler beim Verbinden mit der Bridge {ip_address}: {e}")
        # Mache die Fehlermeldung benutzerfreundlicher
        error_message = str(e)
        if "101" in error_message:
            error_message = (
                "Der Link-Button wurde nicht gedrückt. Bitte versuche es erneut."
            )
        return jsonify({"error": error_message}), 500
    except Exception as e:
        log.error(f"Allgemeiner Fehler beim Verbinden mit der Bridge {ip_address}: {e}")
        return jsonify({"error": "Ein unerwarteter Fehler ist aufgetreten."}), 500


@setup_api.route("/save", methods=["POST"])
def save_setup_config():
    """Speichert die initiale Konfiguration nach dem Setup-Wizard."""
    try:
        data = request.get_json()
        if not all(k in data for k in ["bridge_ip", "app_key", "location"]):
            return (
                jsonify({"error": "Unvollständige Daten für die Ersteinrichtung."}),
                400,
            )

        # Erstelle eine saubere, leere Konfiguration mit den neuen Zugangsdaten
        initial_config = {
            "bridge_ip": data["bridge_ip"],
            "app_key": data["app_key"],
            "location": data["location"],
            "global_settings": {
                "hysteresis_percent": 25,
                "datalogger_interval_minutes": 15,
                "loop_interval_s": 1,
                "status_interval_s": 5,
                "log_level": "INFO",
            },
            "scenes": {},
            "rooms": [],
            "routines": [],
        }

        if config_manager.safe_write(initial_config):
            log.info("Ersteinrichtung abgeschlossen und Konfiguration gespeichert.")
            return jsonify({"message": "Konfiguration gespeichert."})

        return jsonify({"error": "Speichern fehlgeschlagen."}), 500
    except Exception as e:
        log.error(f"Fehler beim Speichern der Setup-Konfiguration: {e}", exc_info=True)
        return jsonify({"error": f"Ein interner Fehler ist aufgetreten: {e}"}), 500
