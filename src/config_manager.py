"""
Verwaltet das Laden und Speichern der zentralen YAML-Konfigurationsdatei.
"""

import os
import threading
import yaml
from .logger import Logger


class ConfigManager:
    """Verwaltet das Laden und Speichern der zentralen YAML-Konfigurationsdatei."""

    def __init__(self, config_file: str, log: Logger):
        self.config_file = config_file
        self.log = log
        self._lock = threading.Lock()
        self._ensure_config_file()

    def _ensure_config_file(self):
        """Stellt sicher, dass die Konfigurationsdatei existiert."""
        if not os.path.exists(self.config_file):
            self.safe_write({})
            self.log.info(
                f"Leere Konfigurationsdatei '{self.config_file}' wurde erstellt."
            )

    def safe_write(self, data: dict) -> bool:
        """Schreibt Daten atomar in die YAML-Datei, um Datenverlust zu vermeiden."""
        temp_file = self.config_file + ".tmp"
        try:
            with self._lock:
                with open(temp_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        data, f, indent=2, allow_unicode=True, default_flow_style=False
                    )
                os.replace(temp_file, self.config_file)
            return True
        except (IOError, yaml.YAMLError) as e:
            self.log.error(f"Fehler beim Schreiben der Konfiguration: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def get_full_config(self) -> dict:
        """Lädt die gesamte Konfiguration aus der YAML-Datei."""
        try:
            with self._lock:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    return config if config is not None else {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.log.error(
                f"Konfiguration konnte nicht geladen werden: {e}. Erstelle eine leere Konfiguration."
            )
            self._ensure_config_file()
            return {}

    def get_last_modified_time(self) -> float:
        """Gibt den Zeitstempel der letzten Änderung der Konfigurationsdatei zurück."""
        try:
            return os.path.getmtime(self.config_file)
        except FileNotFoundError:
            return 0
