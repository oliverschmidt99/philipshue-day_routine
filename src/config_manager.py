"""
Verwaltet das Laden und Speichern der zentralen YAML-Konfigurationsdateien.
"""

import os
import threading
import yaml
from .logger import AppLogger


class ConfigManager:
    """Verwaltet das Laden und Speichern der zentralen YAML-Konfigurationsdateien."""

    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.settings_file = os.path.join(self.data_dir, "settings.yaml")
        self.automation_file = os.path.join(self.data_dir, "automation.yaml")
        self.home_file = os.path.join(self.data_dir, "home.yaml")
        self._lock = threading.Lock()
        self._ensure_config_files()

    def _ensure_config_files(self):
        """Stellt sicher, dass die Konfigurationsdateien existieren."""
        for file_path in [self.settings_file, self.automation_file, self.home_file]:
            if not os.path.exists(file_path):
                self.safe_write(file_path, {})
                self.logger.info(
                    f"Leere Konfigurationsdatei '{os.path.basename(file_path)}' wurde erstellt."
                )

    def safe_write(self, file_path: str, data: dict) -> bool:
        """Schreibt Daten atomar in die YAML-Datei, um Datenverlust zu vermeiden."""
        temp_file = file_path + ".tmp"
        try:
            with self._lock:
                with open(temp_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        data, f, indent=2, allow_unicode=True, default_flow_style=False
                    )
                os.replace(temp_file, file_path)
            return True
        except (IOError, yaml.YAMLError) as e:
            self.logger.error(f"Fehler beim Schreiben der Konfiguration: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def get_full_config(self) -> dict:
        """Lädt die gesamte Konfiguration aus den YAML-Dateien und führt sie zusammen."""
        config = {}
        for file_path in [self.settings_file, self.automation_file, self.home_file]:
            try:
                with self._lock:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = yaml.safe_load(f)
                        if content:
                            config.update(content)
            except (FileNotFoundError, yaml.YAMLError) as e:
                self.logger.error(
                    f"Konfiguration konnte nicht geladen werden: {e}. Erstelle eine leere Konfiguration."
                )
                self._ensure_config_files()
        return config

    def get_last_modified_time(self) -> float:
        """Gibt den Zeitstempel der letzten Änderung der Konfigurationsdateien zurück."""
        latest_time = 0
        for file_path in [self.settings_file, self.automation_file, self.home_file]:
            try:
                latest_time = max(latest_time, os.path.getmtime(file_path))
            except FileNotFoundError:
                pass
        return latest_time