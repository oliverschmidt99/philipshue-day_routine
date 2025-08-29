# src/config_manager.py
import json
import os
import threading
from .logger import Logger

# Pfade relativ zur Datei definieren
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


class ConfigManager:
    """Verwaltet das Laden und Speichern der getrennten Konfigurationsdateien."""

    def __init__(self, log: Logger):
        self.log = log
        self._lock = threading.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)
        self._ensure_config_files()

    def _ensure_config_files(self):
        """Stellt sicher, dass beide Konfigurationsdateien existieren."""
        if not os.path.exists(SETTINGS_FILE):
            self.safe_write(
                SETTINGS_FILE, {"bridge_ip": None, "app_key": None, "location": {}}
            )
        if not os.path.exists(CONFIG_FILE):
            self.safe_write(CONFIG_FILE, {"rooms": [], "scenes": {}, "routines": []})

    def safe_write(self, file_path: str, data: dict) -> bool:
        """Schreibt Daten atomar in eine Datei, um Datenverlust zu vermeiden."""
        temp_file = file_path + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, file_path)
            return True
        except (IOError, TypeError) as e:
            self.log.error(
                f"Fehler beim Schreiben von '{os.path.basename(file_path)}': {e}"
            )
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def get_full_config(self) -> dict:
        """Lädt und kombiniert settings.json und config.json."""
        with self._lock:
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return {**settings, **config}
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.log.error(
                    f"Konfiguration konnte nicht geladen werden: {e}. Erstelle leere Dateien."
                )
                self._ensure_config_files()
                return {}

    def save_full_config(self, full_config: dict) -> bool:
        """Trennt die Gesamtkonfiguration und speichert sie in die jeweiligen Dateien."""
        with self._lock:
            settings_data = {
                "bridge_ip": full_config.get("bridge_ip"),
                "app_key": full_config.get("app_key"),
                "location": full_config.get("location", {}),
                "global_settings": full_config.get("global_settings", {}),
            }
            config_data = {
                "rooms": full_config.get("rooms", []),
                "scenes": full_config.get("scenes", {}),
                "routines": full_config.get("routines", []),
            }
            if not isinstance(config_data.get("routines"), list):
                self.log.error("Speichern abgebrochen: Ungültige Konfigurationsdaten.")
                return False
            return self.safe_write(SETTINGS_FILE, settings_data) and self.safe_write(
                CONFIG_FILE, config_data
            )

    def get_settings(self) -> dict:
        """Lädt nur die settings.json."""
        with self._lock:
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
