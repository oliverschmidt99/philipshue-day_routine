"""
Zentralisierte API-Endpunkte für die Philips Hue Routine-Steuerung.
"""

import os
import shutil
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta

import pandas as pd
import requests
from flask import Blueprint, jsonify, request, current_app, render_template, Response
from jinja2 import TemplateNotFound
from phue import Bridge, PhueException
from requests.exceptions import RequestException

# --- Pfaddefinitionen ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
CONFIG_BACKUP_FILE = os.path.join(DATA_DIR, "config.backup.yaml")
RESTART_FLAG_FILE = os.path.join(DATA_DIR, "restart.flag")

# --- Blueprint-Erstellung ---
api = Blueprint("api", __name__)


def get_bridge_instance():
    """Erstellt eine Bridge-Instanz aus der App-Konfiguration."""
    config = current_app.config_manager.get_full_config()
    ip, key = config.get("bridge_ip"), config.get("app_key")
    if not ip or not key:
        return None
    try:
        bridge = Bridge(ip, username=key)
        bridge.get_api()
        return bridge
    except (PhueException, RequestException):
        return None


# ... (Hier folgen alle API-Routen, wie in der vorherigen Antwort gezeigt)
