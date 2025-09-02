"""
API-Endpunkte für den Zugriff auf Laufzeit- und historische Daten.
Dazu gehören Logs, Statusinformationen und Sensordaten für die Analyse.
"""

import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request, Response, current_app
from web.server import DB_FILE, LOG_FILE, STATUS_FILE

data_api = Blueprint("data_api", __name__)


@data_api.route("/history")
def get_data_history():
    """Gibt historische Sensordaten aus der Datenbank zurück."""
    log = current_app.logger_instance
    try:
        sensor_id_str = request.args.get("sensor_id")
        date_str = request.args.get("date")
        period = request.args.get("period", "day")
        avg_window_str = request.args.get("avg", "1")

        if not sensor_id_str or not date_str:
            return (
                jsonify(
                    {"error": "Parameter 'sensor_id' und 'date' sind erforderlich."}
                ),
                400,
            )

        sensor_id = int(sensor_id_str)
        avg_window = (
            int(avg_window_str)
            if avg_window_str.isdigit() and int(avg_window_str) > 0
            else 1
        )

        start_date = datetime.fromisoformat(date_str).replace(
            hour=0, minute=0, second=0
        )
        end_date = start_date + (
            timedelta(days=7) if period == "week" else timedelta(days=1)
        )

        light_sensor_id, temp_sensor_id = sensor_id + 1, sensor_id + 2

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
            )

        if df.empty:
            return jsonify({"labels": [], "brightness_avg": [], "temperature_avg": []})

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df_pivot = df.pivot(
            index="timestamp", columns="measurement_type", values="value"
        )

        # KORREKTUR: Sicherstellen, dass beide Spalten existieren, um KeyErrors zu vermeiden
        if "brightness" not in df_pivot:
            df_pivot["brightness"] = pd.NA
        if "temperature" not in df_pivot:
            df_pivot["temperature"] = pd.NA

        if avg_window > 1:
            df_pivot["brightness"] = (
                df_pivot["brightness"].rolling(window=avg_window, min_periods=1).mean()
            )
            df_pivot["temperature"] = (
                df_pivot["temperature"].rolling(window=avg_window, min_periods=1).mean()
            )

        df_resampled = df_pivot.resample("5min").mean().interpolate(method="time")

        return jsonify(
            {
                "labels": df_resampled.index.strftime("%Y-%m-%dT%H:%M:%S").tolist(),
                "brightness_avg": df_resampled["brightness"]
                .round(2)
                .where(pd.notna(df_resampled["brightness"]), None)
                .tolist(),
                "temperature_avg": df_resampled["temperature"]
                .round(2)
                .where(pd.notna(df_resampled["temperature"]), None)
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
