import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# Ein Dictionary, das als Cache dient, um Logger-Instanzen zu speichern.
_loggers = {}

class Logger:
    """
    Eine Klasse zur Konfiguration eines Loggers.
    Sie richtet Handler für die Konsolenausgabe und für rotierende Log-Dateien ein.
    """
    def __init__(self, name='HueFlowLogger', level_str='INFO', log_file="app.log"):
        self.logger = logging.getLogger(name)
        
        # Mapping von Log-Level-Strings auf die Konstanten von logging.
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level = levels.get(level_str.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Verhindert, dass Log-Nachrichten an übergeordnete Logger weitergegeben werden.
        self.logger.propagate = False

        # Fügt Handler nur hinzu, wenn der Logger noch keine hat, um Duplikate zu vermeiden.
        if not self.logger.handlers:
            # Konsolen-Handler (stdout)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

            # Datei-Handler (für app.log)
            try:
                # Erstellt eine täglich rotierende Log-Datei.
                fh = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
                fh.setLevel(level)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
            except Exception as e:
                # Fängt Fehler ab, z.B. wenn keine Schreibrechte für die Log-Datei bestehen.
                self.logger.error(f"Konnte den Datei-Handler für '{log_file}' nicht erstellen: {e}")

    def get_logger(self):
        """Gibt die konfigurierte Logger-Instanz zurück."""
        return self.logger

def setup_logger(name='HueFlowLogger', level_str='INFO'):
    """
    Diese Funktion dient als "Factory" für den Logger.
    Sie stellt sicher, dass für einen bestimmten Namen immer dieselbe Logger-Instanz
    verwendet wird, um eine saubere und konsistente Log-Ausgabe zu gewährleisten.
    """
    if name in _loggers:
        # Wenn der Logger bereits existiert, wird die existierende Instanz zurückgegeben.
        # So wird verhindert, dass versehentlich mehrere Handler hinzugefügt werden.
        return _loggers[name]

    # Wenn der Logger neu ist, wird eine Instanz der Logger-Klasse erstellt.
    logger_instance = Logger(name=name, level_str=level_str).get_logger()
    _loggers[name] = logger_instance
    return logger_instance
