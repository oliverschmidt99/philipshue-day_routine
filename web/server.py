import os
import sys
import json
import sqlite3
import markdown
import yaml
import logging
import shutil
import time
import threading
import requests
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify, render_template, request
from src.logger import Logger
from phue import Bridge

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
CONFIG_LOCK_FILE = os.path.join(PROJECT_ROOT, "config.yaml.lock")
CONFIG_BACKUP_FILE = os.path.join(PROJECT_ROOT, "config.backup.yaml")
STATUS_FILE = os.path.join(PROJECT_ROOT, "status.json")
LOG_FILE = os.path.join(PROJECT_ROOT, "info.log")
DB_FILE = os.path.join(PROJECT_ROOT, "sensor_data.db")
HELP_FILE = os.path.join(BASE_DIR, "templates", "hilfe.html")

app = Flask(__name__)
log = Logger(LOG_FILE)

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)


def get_bridge():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        bridge_ip = config.get("bridge_ip")
        app_key = config.get("app_key")
        if not bridge_ip or not app_key:
            return None
        return Bridge(bridge_ip, username=app_key)
    except Exception as e:
        log.error(f"Fehler beim Verbinden mit der Bridge im Webserver: {e}")
        return None


# --- SETUP API ENDPOINTS ---
@app.route("/api/setup/status")
def get_setup_status():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if config and config.get("bridge_ip") and config.get("app_key"):
            return jsonify({"setup_needed": False})
        return jsonify({"setup_needed": True})
    except Exception:
        return jsonify({"setup_needed": True})


@app.route("/api/setup/discover")
def discover_bridges():
    try:
        response = requests.get("https://discovery.meethue.com/")
        response.raise_for_status()
        bridges = response.json()
        return jsonify([b["internalipaddress"] for b in bridges])
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/setup/connect", methods=["POST"])
def connect_to_bridge():
    data = request.get_json()
    ip_address = data.get("ip")
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400

    try:
        bridge = Bridge(ip_address)
        bridge.connect()
        app_key = bridge.username
        return jsonify({"app_key": app_key})
    except Exception as e:
        error_message = str(e)
        if "101" in error_message:
            error_message = "Der Link-Button auf der Bridge wurde nicht gedrückt."
        return jsonify({"error": error_message}), 500


@app.route("/api/setup/save", methods=["POST"])
def save_setup_config():
    try:
        data = request.get_json()
        new_config = {
            "bridge_ip": data.get("bridge_ip"),
            "app_key": data.get("app_key"),
            "location": {
                "latitude": float(data.get("latitude")),
                "longitude": float(data.get("longitude")),
            },
            "global_settings": {
                "datalogger_interval_minutes": 1,
                "hysteresis_percent": 25,
                "log_level": "INFO",
                "times": {
                    "morning": "06:30",
                    "day": "",
                    "evening": "",
                    "night": "23:00",
                },
            },
            "rooms": [],
            "routines": [],
            "scenes": {
                "off": {"status": False, "bri": 0},
                "on": {"status": True, "bri": 254},
            },
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
        return jsonify(
            {
                "message": "Konfiguration erfolgreich gespeichert. Die Anwendung lädt im Hintergrund neu."
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- REGULAR API ENDPOINTS ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/bridge/groups")
def get_bridge_groups():
    b = get_bridge()
    if not b:
        return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        groups = b.get_group()
        return jsonify(
            [{"id": key, "name": value["name"]} for key, value in groups.items()]
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bridge/sensors")
def get_bridge_sensors():
    b = get_bridge()
    if not b:
        return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        sensors = b.get_sensor()
        return jsonify(
            [
                {"id": key, "name": value["name"]}
                for key, value in sensors.items()
                if value.get("type") == "ZLLPresence"
            ]
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["GET", "POST"])
def handle_config():
    if request.method == "POST":
        try:
            new_config = request.get_json()
            with open(CONFIG_LOCK_FILE, "w") as f:
                pass
            log.debug("Config-Lock erstellt.")
            temp_file = CONFIG_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
            os.replace(temp_file, CONFIG_FILE)
            log.info("Konfiguration wurde erfolgreich über die API aktualisiert.")
            return jsonify({"message": "Konfiguration erfolgreich gespeichert."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(CONFIG_LOCK_FILE):
                os.remove(CONFIG_LOCK_FILE)
                log.debug("Config-Lock entfernt.")
    else:
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return jsonify(yaml.safe_load(f))
        except FileNotFoundError:
            return jsonify({"error": "Konfigurationsdatei nicht gefunden."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/status")
def get_status():
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify(
                {
                    "routines": data.get("routines", []),
                    "sun_times": data.get("sun_times", None),
                }
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"routines": [], "sun_times": None}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/log")
def get_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return "".join(f.readlines()[-500:])
    except FileNotFoundError:
        return "Log-Datei nicht gefunden.", 404
    except Exception as e:
        return f"Fehler beim Lesen der Log-Datei: {e}", 500


@app.route("/api/data/history")
def get_data_history():
    try:
        sensor_id = request.args.get("sensor_id", type=int)
        period = request.args.get("period", "day")
        date_str = request.args.get("date")
        range_hours = request.args.get("range", default=24, type=int)
        avg_window = request.args.get("avg", default=0, type=int)

        if not sensor_id:
            return jsonify({"error": "sensor_id ist erforderlich"}), 400

        light_sensor_id = sensor_id + 1
        temp_sensor_id = sensor_id + 2
        con = sqlite3.connect(DB_FILE)

        if period == "week":
            start_date = datetime.fromisoformat(date_str)
            start_of_week = start_date - timedelta(days=start_date.weekday())
            end_of_week = start_of_week + timedelta(days=7)
            start_iso = start_of_week.isoformat()
            end_iso = end_of_week.isoformat()
        else:  # day or custom range
            now = datetime.now()
            start_date = now - timedelta(hours=range_hours)
            start_iso = start_date.isoformat()
            end_iso = now.isoformat()

        query = """
            SELECT timestamp, value, measurement_type FROM measurements 
            WHERE sensor_id IN (?, ?) AND timestamp >= ? AND timestamp <= ? 
            ORDER BY timestamp
        """
        df = pd.read_sql_query(
            query, con, params=(light_sensor_id, temp_sensor_id, start_iso, end_iso)
        )
        con.close()

        if df.empty:
            return jsonify(
                {
                    "labels": [],
                    "brightness": [],
                    "temperature": [],
                    "brightness_avg": [],
                    "temperature_avg": [],
                }
            )

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.pivot(index="timestamp", columns="measurement_type", values="value")
        df.rename(
            columns={"brightness": "brightness", "temperature": "temperature"},
            inplace=True,
        )

        if avg_window > 0:
            df["brightness_avg"] = (
                df["brightness"].rolling(window=avg_window, min_periods=1).mean()
            )
            df["temperature_avg"] = (
                df["temperature"].rolling(window=avg_window, min_periods=1).mean()
            )
        else:
            df["brightness_avg"] = None
            df["temperature_avg"] = None

        df = df.where(pd.notnull(df), None)

        return jsonify(
            {
                "labels": df.index.strftime("%Y-%m-%dT%H:%M:%S").tolist(),
                "brightness": df["brightness"].tolist(),
                "temperature": df["temperature"].tolist(),
                "brightness_avg": df["brightness_avg"].tolist(),
                "temperature_avg": df["temperature_avg"].tolist(),
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if "con" in locals() and con:
            con.close()


@app.route("/api/help")
def get_help():
    try:
        with open(HELP_FILE, "r", encoding="utf-8") as f:
            return jsonify(content=f.read())
    except FileNotFoundError:
        log.error(f"Hilfedatei nicht gefunden unter: {HELP_FILE}")
        return jsonify(error="hilfe.html nicht gefunden"), 404
    except Exception as e:
        log.error(f"Fehler beim Lesen der Hilfedatei: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/system/restart", methods=["POST"])
def restart_app():
    log.info("Neustart der Anwendung über API ausgelöst.")

    def restart_later():
        time.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    threading.Thread(target=restart_later).start()
    return jsonify({"message": "Anwendung wird neu gestartet..."})


@app.route("/api/config/backup", methods=["POST"])
def backup_config():
    log.info("Backup der Konfiguration über API ausgelöst.")
    try:
        shutil.copy(CONFIG_FILE, CONFIG_BACKUP_FILE)
        return jsonify(
            {
                "message": f"Konfiguration wurde als '{os.path.basename(CONFIG_BACKUP_FILE)}' gesichert."
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config/restore", methods=["POST"])
def restore_config():
    log.info("Wiederherstellung der Konfiguration über API ausgelöst.")
    try:
        if not os.path.exists(CONFIG_BACKUP_FILE):
            return jsonify({"error": "Keine Backup-Datei gefunden."}), 404
        shutil.copy(CONFIG_BACKUP_FILE, CONFIG_FILE)
        return jsonify(
            {
                "message": "Konfiguration aus Backup wiederhergestellt. Bitte die Anwendung neu starten."
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
