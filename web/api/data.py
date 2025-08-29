# web/api/data.py
import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request, Response
from ..server import DB_FILE, LOG_FILE, STATUS_FILE, log

data_api = Blueprint("data_api", __name__)


@data_api.route("/history")
def get_data_history():
    """Gibt historische Sensordaten aus der Datenbank zurück."""
    try:
        sensor_id_str = request.args.get("sensor_id")
        date_str = request.args.get("date")

        if not sensor_id_str or not date_str:
            return (
                jsonify(
                    {"error": "Parameter 'sensor_id' und 'date' sind erforderlich."}
                ),
                400,
            )

        sensor_id = int(sensor_id_str)
        light_sensor_id, temp_sensor_id = sensor_id + 1, sensor_id + 2

        start_date = datetime.fromisoformat(date_str).replace(
            hour=0, minute=0, second=0
        )
        end_date = start_date + timedelta(days=1)

        query = "SELECT timestamp, measurement_type, value FROM measurements WHERE sensor_id IN (?, ?) AND timestamp >= ? AND timestamp < ? ORDER BY timestamp"

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
        ).reset_index()

        # Fülle fehlende Werte auf für eine durchgehende Linie im Chart
        df_pivot.set_index("timestamp", inplace=True)
        df_resampled = df_pivot.resample("5min").mean().interpolate(method="time")

        return jsonify(
            {
                "labels": df_resampled.index.strftime("%Y-%m-%dT%H:%M:%S").tolist(),
                "brightness_avg": df_resampled["brightness"]
                .where(pd.notna(df_resampled["brightness"]), None)
                .tolist(),
                "temperature_avg": df_resampled["temperature"]
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
            # Lese direkt den Inhalt und lasse Flask das JSON-Handling machen
            return Response(f.read(), mimetype="application/json")
    except (FileNotFoundError, json.JSONDecodeError):
        # Gib ein leeres Standardobjekt zurück, wenn die Datei nicht existiert oder leer ist
        return jsonify({"routines": [], "sun_times": None})
