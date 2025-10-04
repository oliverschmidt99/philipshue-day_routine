import os
import yaml
import shutil
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

# *** HIER IST DIE KORREKTUR: Logger -> AppLogger ***
from .logger import AppLogger

class ConfigManager:
    """Verwaltet das Laden, Speichern und Validieren von YAML-Konfigurationsdateien."""

    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.settings_file = os.path.join(self.data_dir, "settings.yaml")
        self.automation_file = os.path.join(self.data_dir, "automation.yaml")
        self.home_file = os.path.join(self.data_dir, "home.yaml")

    def get_last_modified_time(self):
        """Gibt den letzten Änderungszeitpunkt der Konfigurationsdateien zurück."""
        try:
            return max(
                os.path.getmtime(self.settings_file),
                os.path.getmtime(self.automation_file),
                os.path.getmtime(self.home_file),
            )
        except FileNotFoundError:
            return 0

    def load_yaml(self, file_path):
        """Lädt eine YAML-Datei sicher."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, YAMLError) as e:
            self.logger.warning(f"Fehler beim Laden von {os.path.basename(file_path)}: {e}")
            return None

    def get_full_config(self):
        """Lädt und kombiniert alle Konfigurationsdateien."""
        settings = self.load_yaml(self.settings_file) or {}
        automation = self.load_yaml(self.automation_file) or {}
        home = self.load_yaml(self.home_file) or {}
        
        # Kombiniere die Dictionaries
        full_config = {**settings, **automation, **home}
        return full_config

    def safe_write(self, file_path, data):
        """Schreibt Daten sicher in eine YAML-Datei mit Backup."""
        temp_path = file_path + ".tmp"
        backup_path = file_path + ".bak"
        
        try:
            # Schreibe in eine temporäre Datei
            with open(temp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            # Erstelle ein Backup der existierenden Datei, falls vorhanden
            if os.path.exists(file_path):
                shutil.copy(file_path, backup_path)
            
            # Benenne die temporäre Datei zur finalen Datei um
            os.rename(temp_path, file_path)
            
            return True
        except (IOError, YAMLError) as e:
            self.logger.error(f"Fehler beim Schreiben von {os.path.basename(file_path)}: {e}", exc_info=True)
            # Versuche, das Backup wiederherzustellen
            if os.path.exists(backup_path):
                os.rename(backup_path, file_path)
            return False