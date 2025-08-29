# web/api/data.py
import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request
from ..server import DB_FILE, LOG_FILE, STATUS_FILE, log

data_api = Blueprint("data_api", __name__)


@data_api.route("/history")
def get_data_history():
    """Gibt historische Sensordaten aus der Datenbank zurück."""
    try:
        sensor_id = request.args.get("sensor_id", type=int)
        date_str = request.args.get("date")
        if not sensor_id or not date_str:
            return jsonify({"error": "Parameter fehlen"}), 400

        light_sensor_id, temp_sensor_id = sensor_id + 1, sensor_id + 2
        start_date = datetime.fromisoformat(date_str).replace(
            hour=0, minute=0, second=0
        )
        end_date = start_date + timedelta(days=1)

        query = "SELECT timestamp, measurement_type, value FROM measurements WHERE sensor_id IN (?,?) AND timestamp >= ? AND timestamp < ?"
        with sqlite3.connect(DB_FILE) as con:
            df = pd.read_sql_query(
                query,
                con,
                params=(
                    light_sensor_id,
                    temp_sensor_id,
                    start_date.isoformat(),
                    end_date.isoformat(),
                ),
            )

        if df.empty:
            return jsonify({"labels": [], "brightness_avg": [], "temperature_avg": []})

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df_pivot = df.pivot(
            index="timestamp", columns="measurement_type", values="value"
        )

        return jsonify(
            {
                "labels": df_pivot.index.strftime("%Y-%m-%dT%H:%M:%S").tolist(),
                "brightness_avg": df_pivot.get(
                    "brightness", pd.Series(dtype="float64")
                ).tolist(),
                "temperature_avg": df_pivot.get(
                    "temperature", pd.Series(dtype="float64")
                ).tolist(),
            }
        )
    except (sqlite3.Error, pd.errors.DatabaseError) as e:
        log.error(f"Fehler bei der Datenhistorie: {e}")
        return jsonify({"error": str(e)}), 500


@data_api.route("/log")
def get_log():
    """Gibt die letzten Log-Einträge zurück."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return "".join(f.readlines()[-500:])
    except IOError:
        return "Log-Datei nicht gefunden.", 404


@data_api.route("/status")
def get_status():
    """Gibt den aktuellen Status der Routinen zurück."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"routines": [], "sun_times": None})
