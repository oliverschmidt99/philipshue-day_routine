import yaml
from src.logger import Logger

def load_config(log: Logger, config_file: str = "config.yaml") -> dict:
    """
    Lädt die Konfigurationsdatei (config.yaml).

    Args:
        log: Das Logger-Objekt für die Protokollierung.
        config_file: Der Pfad zur Konfigurationsdatei.

    Returns:
        Ein Dictionary mit der geladenen Konfiguration.

    Raises:
        FileNotFoundError: Wenn die Konfigurationsdatei nicht gefunden wird.
        yaml.YAMLError: Wenn ein Fehler beim Parsen der YAML-Datei auftritt.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            log.info(f"Konfiguration aus '{config_file}' geladen.")
            return config
    except FileNotFoundError:
        log.error(f"Konfigurationsdatei '{config_file}' nicht gefunden.")
        raise
    except yaml.YAMLError as e:
        log.error(f"Fehler beim Parsen der YAML-Datei '{config_file}': {e}")
        raise
