"""
API-Endpunkte für den Zugriff auf Laufzeit- und historische Daten.
Dazu gehören Logs, Statusinformationen und Sensordaten für die Analyse.
"""

import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request, Response, current_app
from web.server import DB_FILE, LOG_FILE, STATUS_FILE  # Absoluter Import

data_api = Blueprint("data_api", __name__)


@data_api.route("/history")
def get_data_history():
    """Gibt historische Sensordaten aus der Datenbank zurück."""
    log = current_app.logger_instance
    try:
        sensor_id_str = request.args.get("sensor_id")
        period = request.args.get("period", "day")
        date_str = request.args.get("date")
        avg_window_str = request.args.get("avg", "1")

        if not sensor_id_str or not date_str:
            return jsonify({"error": "Sensor-ID und Datum sind erforderlich."}), 400

        sensor_id = int(sensor_id_str)
        light_sensor_id, temp_sensor_id = sensor_id + 1, sensor_id + 2
        avg_window = int(avg_window_str) if avg_window_str.isdigit() else 1

        base_date = datetime.fromisoformat(date_str)
        if period == "week":
            start_date = base_date - timedelta(days=base_date.weekday())
            end_date = start_date + timedelta(days=7)
            resample_rule = "30min"
        else:  # 'day'
            start_date = base_date
            end_date = start_date + timedelta(days=1)
            resample_rule = "5min"

        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = end_date.replace(hour=0, minute=0, second=0)

        query = """
            SELECT timestamp, measurement_type, value
            FROM measurements
            WHERE sensor_id IN (?, ?) AND timestamp >= ? AND timestamp < ?
            ORDER BY timestamp
        """
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
                parse_dates=["timestamp"],
            )

        if df.empty:
            return jsonify({"labels": [], "brightness_avg": [], "temperature_avg": []})

        df_pivot = df.pivot_table(
            index="timestamp", columns="measurement_type", values="value"
        )
        df_resampled = df_pivot.resample(resample_rule).mean()

        if "brightness" in df_resampled.columns and avg_window > 1:
            df_resampled["brightness"] = (
                df_resampled["brightness"].rolling(window=avg_window).mean()
            )

        df_resampled = df_resampled.interpolate(method="time")

        return jsonify(
            {
                "labels": df_resampled.index.strftime("%Y-%m-%dT%H:%M:%S").tolist(),
                "brightness_avg": df_resampled.get("brightness")
                .where(pd.notna(df_resampled.get("brightness")), None)
                .tolist(),
                "temperature_avg": df_resampled.get("temperature")
                .where(pd.notna(df_resampled.get("temperature")), None)
                .tolist(),
            }
        )
    except (sqlite3.Error, ValueError, KeyError) as e:
        log.error(f"Fehler bei der Abfrage der Datenhistorie: {e}", exc_info=True)
        return jsonify({"error": "Datenbankfehler oder ungültige Daten."}), 500


@data_api.route("/log")
def get_log():
    """Gibt die letzten 500 Zeilen der Log-Datei zurück."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return Response("".join(lines[-500:]), mimetype="text/plain")
    except IOError:
        return "Log-Datei nicht gefunden.", 404


@data_api.route("/status")
def get_status():
    """Gibt den aktuellen Status der Routinen aus der status.json zurück."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="application/json")
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"routines": [], "sun_times": None})
