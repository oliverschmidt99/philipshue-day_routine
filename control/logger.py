import logging
import sys

class Logger:
    """
    Eine einfache Wrapper-Klasse für das Python-Logging, um
    Nachrichten in eine Datei und auf die Konsole zu schreiben.
    """
    def __init__(self, file_name):
        # Wir holen den Logger mit einem eindeutigen Namen, um Konflikte zu vermeiden
        self.logger = logging.getLogger(f"hue_routine_logger_{file_name}")
        self.logger.setLevel(logging.DEBUG) # Das Gesamtlevel bleibt DEBUG, damit wir die Funktion im Code nutzen können

        # Verhindern, dass Handler mehrfach hinzugefügt werden
        if not self.logger.handlers:
            # Handler für das Schreiben in eine Datei
            file_handler = logging.FileHandler(file_name, mode='w', encoding='utf-8')
            
            # KORRIGIERT: Setze das Level für die Datei auf INFO.
            # Nur Nachrichten ab INFO (also INFO, WARNING, ERROR) werden in die Datei geschrieben.
            file_handler.setLevel(logging.INFO) 
            
            # Formatter für eine saubere Log-Datei
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Handler für die Ausgabe auf der Konsole
            stream_handler = logging.StreamHandler(sys.stdout)
            # Das Level für die Konsole bleibt INFO, das ist gut so.
            stream_handler.setLevel(logging.INFO) 
            stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)

    def debug(self, message):
        """Loggt eine Debug-Nachricht (wird jetzt nicht mehr in der Datei erscheinen)."""
        self.logger.debug(message)

    def info(self, message):
        """Loggt eine Info-Nachricht."""
        self.logger.info(message)

    def warning(self, message):
        """Loggt eine Warnung."""
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        """Loggt einen Fehler."""
        self.logger.error(message, exc_info=exc_info)
