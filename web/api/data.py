"""
API-Endpunkte für den Zugriff auf Laufzeit- und historische Daten.
"""
import os
import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, jsonify, request, Response, current_app

data_api = Blueprint("data_api", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
LOG_FILE = os.path.join(BASE_DIR, "data", "app.log")
STATUS_FILE = os.path.join(BASE_DIR, "data", "status.json")

@data_api.route("/history")
def get_data_history():
    """Gibt historische Sensordaten aus der Datenbank zurück."""
    try:
        sensor_id = int(request.args.get("sensor_id"))
        date_str = request.args.get("date")
        start_date = datetime.fromisoformat(date_str)
        end_date = start_date + timedelta(days=1)
        
        with sqlite3.connect(DB_FILE) as con:
            query = "SELECT timestamp, measurement_type, value FROM measurements WHERE sensor_id IN (?, ?) AND timestamp >= ? AND timestamp < ?"
            df = pd.read_sql_query(query, con, params=(sensor_id + 1, sensor_id + 2, start_date.isoformat(), end_date.isoformat()))

        if df.empty:
            return jsonify({"labels": [], "brightness": [], "temperature": []})
        
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df_pivot = df.pivot(index="timestamp", columns="measurement_type", values="value").resample("5min").mean().interpolate(method="time")
        
        # Sicherstellen, dass die Spalten existieren, bevor darauf zugegriffen wird
        if "brightness" not in df_pivot.columns:
            df_pivot["brightness"] = None
        if "temperature" not in df_pivot.columns:
            df_pivot["temperature"] = None

        return jsonify({
            "labels": df_pivot.index.strftime('%Y-%m-%dT%H:%M:%S').tolist(),
            "brightness": df_pivot["brightness"].round(2).where(pd.notna(df_pivot["brightness"]), None).tolist(),
            "temperature": df_pivot["temperature"].round(2).where(pd.notna(df_pivot["temperature"]), None).tolist(),
        })
    except (sqlite3.Error, ValueError, KeyError) as e:
        current_app.logger_instance.error(f"Fehler bei der Abfrage der Datenhistorie: {e}")
        return jsonify({"error": f"Datenbank- oder Datenfehler: {e}"}), 500

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
    """Gibt den aktuellen Status der Routinen zurück."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="application/json")
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"routines": [], "sun_times": None})